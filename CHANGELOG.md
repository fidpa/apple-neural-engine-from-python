# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-08-08

Removes `torch` from `requirements.txt`. Nothing in this repository ever
imported it: `ane_working.py` uses `transformers` for `BertTokenizer` alone,
and the inference is CoreML's job. The pin had been carrying a deep-learning
framework into every install of a project that never calls one.

MINOR rather than PATCH, because `pip install -r requirements.txt` now produces
a different environment than it did in 1.0.x — the pins are this project's
promise, so a changed pin is never a patch.

### Removed

- **`torch==2.5.1` from `requirements.txt`.** Verified before removal, on
  2026-08-08:
  - No source file imports `torch`, directly or indirectly.
  - `coremltools==8.3.0` does not depend on it either — a resolve of that pin
    installs `attrs`, `cattrs`, `mpmath`, `protobuf`, `pyaml` and `sympy`, and
    no framework.
  - In a fresh virtualenv containing only `transformers==4.36.2` and
    `numpy==1.26.3`, the complete tokenizer path of `ane_working.py` runs:
    tokenisation of a real (question, context) pair, the cast to `float64`,
    and the `convert_ids_to_tokens` / `convert_tokens_to_string` round-trip
    used for answer extraction. `wordIDs` and `wordTypes` come out as
    `(1, 384)` `float64`, which is the contract the model requires.

  What this saves is smaller than it sounds and is stated here properly: on
  this project's target platform the `torch` 2.5.1 wheel is **63.9 MB**
  (macOS 11+, arm64, cp312; PyPI metadata as of 2026-08-08), not the 906 MB of
  the Linux x86-64 wheel. The real gain is the dependency that disappears:
  OSV lists **22 advisories** against `torch` 2.5.1 as of 2026-08-08, all of
  which leave the tree with it.

### Changed

- **The README's note on the pinned versions was measurably out of date.** It
  claimed "~20 advisories … two in `torch`". Measured against OSV on
  2026-08-08: 44 for `transformers` 4.36.2, 22 for `torch` 2.5.1, and none for
  `coremltools` 8.3.0 or `numpy` 1.26.3. The section now carries the current
  figures, names its source and date, and drops the `torch` half.
- **The README now documents the warning `transformers` prints on import**
  when no framework is installed ("None of PyTorch, TensorFlow >= 2.0, or Flax
  have been found …"). It is the visible cost of this release, it is harmless
  here, and letting people discover it unexplained would look like a broken
  setup.

## [1.0.1] — 2026-08-08

Maintenance release. One real defect in the benchmark, one README claim the
code did not back up, and the project infrastructure this repository never had:
a changelog, a CI gate and a pinned lint configuration. No behaviour of the
working demo changed, and no dependency pin moved.

### Fixed

- **`run_pool()` in `ane_benchmark.py` silently swallowed failed inferences.**
  Finished futures were dropped with `[f for f in futures if not f.done()]`
  without ever calling `.result()`, so an exception raised inside
  `model.predict` disappeared without a trace while the submission counter kept
  climbing. The `pool(12)` figure could therefore report throughput for work
  that never completed — and `--mode full` is exactly the run behind the
  "threading does not help" claim in the README. Finished futures are now
  resolved, so a failed inference aborts loudly instead of being counted.
  This fix has **not** been re-measured on Apple Silicon; it cannot make a
  successful run report differently, only turn a silent failure into a visible
  one.
- **The README overstated what `model_inspect.py` does.** It promised "run it
  on any CoreML model". The spec dump is indeed model-agnostic, but the
  acceptance probe is wired to the file name `BERTSQUADFP16.mlmodel` and to the
  `wordIDs` / `wordTypes` input keys, so a foreign model needs two edits first.
  The table entry now says which half is generic and what to change.
- **`ane_benchmark.py` carried a shebang without the executable bit** (mode
  `100644`), while `ane_working.py`, `model_inspect.py` and `download_model.sh`
  were all `100755`. Now consistent, and enforced by the `EXE` ruleset.

### Added

- **`CHANGELOG.md`** — this file, with the 1.0.0 section reconstructed from the
  README and the original release.
- **`.github/workflows/lint.yml`** — the repository's first CI. Three jobs:
  `python` (ruff plus a syntax check), `shell` (ShellCheck plus `bash -n`), and
  `requirements`, which fails the build if any line in `requirements.txt` is not
  pinned with `==`. The exact pins are this project's central promise, so a
  loosened one should break the build rather than be discovered months later.
  Python comes from `.python-version`, so the gate runs on the interpreter the
  README names.
- **`ruff.toml`** with an explicit rule selection. An unconfigured `ruff check`
  gates against a moving target: ruff 0.16 reported findings on an unchanged
  tree that earlier versions did not. The selection also enables `BLE`, which
  the two `# noqa: BLE001` directives in the sources had been assuming all
  along, and `RUF100`, which reports such directives once they go stale.

### Note on scope

The scripts require macOS and an Apple Neural Engine, so CI checks syntax and
lint only — it cannot execute them. There is no test suite. Anything that
depends on actually running a model still has to be verified by hand on Apple
Silicon.

## [1.0.0] — 2026-05-19

First public release. The repository is the cleaned-up trail of a two-hour
session that reached the Apple Neural Engine of an M4 Pro from Python through
CoreML — a working BERT-SQuAD question-answering demo plus the introspection
tool that makes the model's undocumented input contract discoverable. It is a
learning artifact, not a production inference service.

### Added

- **`ane_working.py` — the working demo.** Tokenises real (context, question)
  pairs, runs them through the CoreML BERT-SQuAD model on the ANE and extracts
  the answer span. Original session script, kept essentially as-is.
- **`model_inspect.py` — the model inspector.** Dumps the CoreML model spec
  (input names, dtypes, shapes) and systematically probes which dtype/shape
  combinations the model actually accepts. This is the tool that surfaced the
  gotchas below; it works on any CoreML model, not just this one.
- **`ane_benchmark.py` — throughput probe** with `--mode {fast,blitz,full}`.
  Consolidated from three working throwaway benchmark scripts of the original
  session. `--mode full` demonstrates that threading does not help, because
  CoreML serialises inference.
- **`download_model.sh`** — fetches Apple's BERT-SQuAD FP16 model via
  `ANE_MODEL_URL`. The model is Apple's property and is never redistributed
  here; the script only points at the official download page.
- **`requirements.txt` with exact pins** and the reasoning behind them, plus
  `.python-version` (3.12.7).
- **README with the four undocumented facts** that cost the debugging time:
  input dtype must be `float64` and not `int32`; shape must be exactly
  `[1, 384]` and not `[384]`; the input keys are `wordIDs` / `wordTypes` and
  not the standard BERT `input_ids` / `token_type_ids`; and `coremltools` must
  be 8.3.0, because 7.x on Python 3.12 fails with `Unable to load
  CoreML.framework` — an error that points nowhere near the version mismatch.

### Measured

Numbers from the original session on an M4 Pro Mac Mini with BERT-SQuAD FP16,
not estimates and not a benchmark worth citing:

- Throughput ~10.5 inferences/s, latency ~95 ms per inference.
- ANE load ~13 % (1.6 W of roughly 12 W) — most of the accelerator sits idle.
- Threading with 8 threads and a pool of 12 gives no improvement at all.

The low utilisation and the threading non-result are the interesting part; the
raw throughput number is not.

[1.1.0]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.1.0
[1.0.1]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.0.1
[1.0.0]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.0.0
