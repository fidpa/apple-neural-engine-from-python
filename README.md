# Apple Neural Engine from Python

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)
![Status](https://img.shields.io/badge/status-curiosity%20experiment-yellow.svg?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Apple%20Silicon%20%7C%20macOS-black?style=flat-square&logo=apple)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)
![Not Production](https://img.shields.io/badge/scope-learning%20repo%2C%20not%20production-orange?style=flat-square)

Reaching the Apple Neural Engine (ANE) of an M4 Pro from Python via CoreML —
a working BERT question-answering demo, the model-introspection tool that
makes the undocumented input contract discoverable, and a throughput probe.
Plus a written record of the parts that **aren't in the docs**.

**The Problem**: "Just use the ANE from Python" sounds trivial and isn't. You
can't target the ANE directly — you hand a CoreML model to `coremltools` and
*CoreML* decides whether it runs on ANE, GPU or CPU. The example BERT-SQuAD
model rejects the obvious inputs with three different cryptic errors before it
runs once, none of which are documented: wrong input dtype, wrong shape, wrong
`coremltools` version. This repo is the 2-hour debugging trail turned into
something the next curious person reproduces in 10 minutes.

> **Scope honesty**: a learning artifact, not a production inference service
> and not a benchmark you should cite. The genuinely useful parts are the
> *model inspector* and the *gotchas* section below.

## What's in here

| File | What it does |
|------|--------------|
| **`ane_working.py`** | The real demo — tokenises real (context, question) pairs, runs them through the CoreML model on the ANE, extracts the answer span. Start here. |
| **`model_inspect.py`** | Dumps the model spec (input names, dtypes, shapes) **and** systematically probes which dtype/shape combinations the model accepts. This is *how* the gotchas below were found — run it on any CoreML model. |
| **`ane_benchmark.py`** | Throughput probe, `--mode {fast,blitz,full}`. `--mode full` demonstrates that threading does **not** help (CoreML serialises inference). |
| `download_model.sh` | Fetches Apple's BERT-SQuAD model (not redistributed here). |

## What actually happened

| Metric | Result (M4 Pro Mac Mini, BERT-SQuAD FP16) |
|--------|--------------------------------------------|
| Throughput | ~10.5 inferences/s, stable |
| Latency | ~95 ms/inference |
| ANE load | ~13 % (1.6 W of ~12 W) — massive headroom unused |
| Threading (8 / pool-12) | **No improvement** — CoreML serialises inference |

The low utilisation and the threading non-result are the interesting findings,
not the raw number. Open hypotheses (Float64 bandwidth waste, attention-only
ANE placement, …) remain untested — see *Roadmap* below.

## Quick Start

```bash
git clone https://github.com/fidpa/apple-neural-engine-from-python
cd apple-neural-engine-from-python

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# The BERT-SQuAD model is Apple's and is NOT in this repo.
# Get the .mlmodel URL from https://developer.apple.com/machine-learning/models/
ANE_MODEL_URL='https://.../BERTSQUADFP16.mlmodel' ./download_model.sh

python ane_working.py            # real Q&A on the ANE — start here
python model_inspect.py          # see/why the input contract is what it is
python ane_benchmark.py --mode full   # proves the serialisation claim
```

While anything runs, watch **Activity Monitor → Window → GPU History → ANE**
for the load spikes.

## The things that aren't documented

The four facts that cost the debugging time. You can rediscover all of them by
running `model_inspect.py` — it's the tool, this is the summary:

1. **Input dtype must be `float64`, not `int32`.** The intuitive
   `inputs['input_ids']` (Int) raises `value type not convertible`. You must
   `.astype(np.float64)`.
2. **Shape must be exactly `[1, 384]`**, not `[384]`. A flat array raises
   `MultiArray shape does not match`.
3. **The input keys are `wordIDs` / `wordTypes`** — *not* the standard BERT
   `input_ids` / `token_type_ids`. Inspect the model spec, don't assume.
4. **`coremltools` must be 8.3.0.** 7.x with Python 3.12 fails at
   `Unable to load CoreML.framework`. The error points nowhere near the
   version mismatch. (The original session even pinned 7.2 — that pin was
   wrong; `requirements.txt` carries the corrected 8.3.0.)

## Prerequisites

- Apple Silicon with an ANE (tested: M4 Pro Mac Mini, macOS)
- Python 3.12.7 (pinned in `.python-version`; other 3.12.x likely fine)
- Network access to fetch the Apple model once

### A note on the pinned versions

`transformers==4.36.2` and `torch==2.5.1` are deliberately old — these are the
versions the original session ran on, and the pins exist so the experiment
reproduces. `pip-audit` will flag ~20 advisories against them (mostly
deserialization and ReDoS issues in `transformers`, two in `torch`). For
**this** script none of them are reachable: the model file is Apple's, the
tokenizer is downloaded from Hugging Face's signed CDN, and the inference
inputs are hardcoded English strings. There is no path through which a
hostile blob reaches the vulnerable code.

If you copy this as scaffolding for a service that accepts untrusted input
(user-uploaded models, free-form text from the wire, fine-tuning pipelines),
upgrade first: `pip install -U transformers torch`. The ANE-specific parts
(the `wordIDs`/`wordTypes`/float64/[1, 384] contract) do **not** depend on
the transformers version.

## Roadmap / not yet done

Plausible **batch processing at 5–10× throughput** — untested, and the
obvious next experiment. INT8 quantisation and multi-model pipelines are the
other open threads. Reproducible results there, with hardware details, are
exactly the contributions that would make this more than a curiosity.

## Provenance

Honesty about what's first-hand vs. cleaned up — the same standard I hold my
other repos to:

- **`ane_working.py`** and **`model_inspect.py`** are the original
  session scripts (16.08.2025), kept essentially as-is. First-hand, not
  re-derived.
- **`ane_benchmark.py`** is a *consolidation* of three working throwaway
  benchmark scripts (`ane_fast` / `ane_max` / `ane_blitz`) into one
  maintainable file. Further redundant variants (`ane_turbo`,
  `ane_stress_test`, `ane_test`) and an early heavier prototype
  (`coreml_example.py`, pulled in TensorFlow) were dropped, not republished.
- **The original session log** (German, 16.08.2025) lives in my private
  notes, not in this public repo. Its substantive findings are already
  distilled above; the rest is diary.
- **The model is not mine.** Apple's BERT-SQuAD sample, fetched at setup time,
  never redistributed.

## Contributing

Small repo, real roadmap (see above). Reproducible batch-processing or INT8
results with hardware details welcome — open an issue or PR.

## See Also

- [proxmox-gpu-passthrough](https://github.com/fidpa/proxmox-gpu-passthrough) — same spirit: battle-tested recipe + the failure modes the official docs skip
- [bash-production-toolkit](https://github.com/fidpa/bash-production-toolkit) — production-ready Bash libraries used across fidpa repos

## License

MIT (code) — see [LICENSE](LICENSE). The BERT-SQuAD CoreML model is Apple's
property and is fetched, not redistributed.

## Author

Marc Allgeier ([@fidpa](https://github.com/fidpa))

**Why I Built This**: Pure curiosity — I wanted to see the M4 Pro's Neural
Engine actually answer a question from Python, once. Two hours later I had it
working *and* a pile of undocumented gotchas. The working part is short; the
gotchas (and the tool that surfaces them) are the reason this is a repo and
not a deleted folder.
