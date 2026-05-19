#!/usr/bin/env python3
"""ANE benchmark — talk to the Apple Neural Engine from Python via CoreML.

Curiosity experiment, not a production tool. Loads a BERT-SQuAD FP16 CoreML
model and hammers it with synthetic inputs to observe ANE behaviour in
Activity Monitor (Window > GPU History > ANE).

Key finding: CoreML serialises inference, so threading does NOT improve
throughput. The --mode full run demonstrates exactly that.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from coremltools.models import MLModel  # type: ignore[import-untyped]

MODEL_FILE = "BERTSQUADFP16.mlmodel"
SEQ_LEN = 384  # model expects exactly [1, 384]

# Pre-generated synthetic model inputs (float64, shape [1, 384]).
Inputs = list[dict[str, np.ndarray]]


def make_inputs(n: int) -> Inputs:
    """Pre-generate n synthetic inputs.

    The model needs Float64 (DOUBLE), shape [1, 384], keys 'wordIDs' /
    'wordTypes' — NOT the standard BERT names or Int32. This single
    non-obvious detail cost the most debugging time.
    """
    return [
        {
            "wordIDs": np.random.randint(100, 10000, (1, SEQ_LEN)).astype(np.float64),
            "wordTypes": np.random.randint(0, 2, (1, SEQ_LEN)).astype(np.float64),
        }
        for _ in range(n)
    ]


def load_model() -> MLModel:
    if not Path(MODEL_FILE).is_file():
        print(f"✗ {MODEL_FILE} not found. Run ./download_model.sh first.")
        sys.exit(1)
    print(f"Loading {MODEL_FILE} ...")
    model = MLModel(MODEL_FILE)
    print("✓ Model ready")
    return model


def run_single(model: MLModel, inputs: Inputs, seconds: int) -> float:
    """Baseline: one thread, tight loop."""
    count = 0
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        model.predict(inputs[count % len(inputs)])
        count += 1
    rate = count / (time.perf_counter() - start)
    print(f"  single-thread : {rate:6.1f} inf/s ({count} in {seconds}s)")
    return rate


def run_threaded(model: MLModel, inputs: Inputs, seconds: int,
                  workers: int) -> float:
    """Multiple threads sharing one model — expected: NO speedup."""
    total = {"n": 0}
    lock = threading.Lock()
    stop = threading.Event()

    def worker() -> None:
        local = 0
        while not stop.is_set():
            model.predict(inputs[local % len(inputs)])
            local += 1
        with lock:
            total["n"] += local

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    time.sleep(seconds)
    stop.set()
    for t in threads:
        t.join()
    rate = total["n"] / (time.perf_counter() - start)
    print(f"  {workers:>2} threads    : {rate:6.1f} inf/s ({total['n']} in {seconds}s)")
    return rate


def run_pool(model: MLModel, inputs: Inputs, seconds: int,
             workers: int) -> float:
    """ThreadPoolExecutor keeping a deep submission queue."""
    count = 0
    start = time.perf_counter()
    end = start + seconds
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures: list = []
        while time.perf_counter() < end:
            while len(futures) < workers * 2:
                futures.append(ex.submit(model.predict, inputs[count % len(inputs)]))
                count += 1
            futures = [f for f in futures if not f.done()]
        for f in futures:
            f.result()
    rate = count / (time.perf_counter() - start)
    print(f"  pool({workers:>2})     : {rate:6.1f} inf/s ({count} in {seconds}s)")
    return rate


def mode_fast(model: MLModel) -> None:
    print("\n=== FAST: single-thread, 10s ===")
    run_single(model, make_inputs(5), 10)


def mode_blitz(model: MLModel) -> None:
    print("\n=== BLITZ: 4 rapid-fire rounds, 10s each ===")
    inputs = make_inputs(10)
    for r in range(4):
        print(f"round {r + 1}/4")
        run_single(model, inputs, 10)


def mode_full(model: MLModel) -> None:
    print("\n=== FULL: baseline vs threading (demonstrates serialisation) ===")
    inputs = make_inputs(20)
    base = run_single(model, inputs, 5)
    for label, rate in (
        ("8 threads", run_threaded(model, inputs, 5, 8)),
        ("pool(12)", run_pool(model, inputs, 5, 12)),
    ):
        delta = (rate / base - 1) * 100
        print(f"  -> {label} vs baseline: {delta:+.1f}%  "
              f"(expect ~0%: CoreML serialises inference)")


MODES = {"fast": mode_fast, "blitz": mode_blitz, "full": mode_full}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apple Neural Engine benchmark")
    parser.add_argument("--mode", choices=MODES, default="fast",
                        help="fast (default) | blitz | full")
    args = parser.parse_args()

    print("Apple Neural Engine benchmark — observe in Activity Monitor:")
    print("  Window > GPU History > ANE\n")
    model = load_model()
    MODES[args.mode](model)
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
