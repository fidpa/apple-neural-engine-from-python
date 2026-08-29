# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.3] - 2026-08-29: The README drops its em-dash habit

The prose reads the same, the punctuation is now plain ASCII, and one typo in a
quick-start comment is fixed. Nothing about the experiment, the scripts, or the
pins changed.

### Changed

- **Twenty em-dash asides became regular punctuation.** Colons, commas, and
  semicolons where the dashes stood, the ellipsis and the "5-10x" range are
  plain ASCII, and the Activity Monitor menu path uses ">" separators. The
  problem-intro paragraph lost its "The Problem" label and reads as plain
  prose; its content is unchanged

### Fixed

- **A quick-start comment said "see/why" where it meant "see why"**
  (`python model_inspect.py` line in the README). The slash was a typo, not
  a path
- **The `[1.1.2]` link reference at the end of this file was missing.** The
  section existed, the reference did not; added alongside this release's

## [1.1.2] - 2026-08-28: GitHub identifies the license as MIT

GitHub reported no license for this project, and has done so since the first
commit: `LICENSE` carried the MIT text followed by a note about Apple's model.
GitHub's license detection reads any addition to the MIT text as a modification.
The license field on the repository page therefore stayed empty, and a
repository without a detected license matches no `license:` filter in GitHub
search, while the README badge said MIT. The note itself was correct and stays,
in the file where such information belongs.

### Changed

- **The license field on the repository page says MIT.** `LICENSE` now carries
  the MIT text and nothing else; with the note removed it is byte-identical to
  that of a repository GitHub reports as `mit`. Nothing about the terms changed:
  the model was never covered, because `download_model.sh` fetches it and this
  repository has never contained it.
- **Third-party components have their own file.** `NOTICE` names what this
  project fetches at setup time and does not redistribute: Apple's BERT-SQuAD
  CoreML model, under Apple's terms, and the tokenizer vocabulary from Hugging
  Face. `README.md` points at it from the `## License` section.

### Upgrade notes

None. This release changes no code and no terms; it moves an informational note
out of `LICENSE` and into `NOTICE`.

## [1.1.1] - 2026-08-28: Older sections now match the code they describe

An editorial pass over the whole changelog. Every entry was read against the tag
it describes, and the release titles and bodies on GitHub were brought in line
with the sections they are cut from. No script changed; the only file outside
`CHANGELOG.md` is a new release workflow.

Measured values, paths and identifiers stay as they were. Where a statement
contradicted the tree it describes, it was corrected, and each correction is an
entry below.

### Fixed

- **`model_inspect.py` is no longer advertised as running on any CoreML model.**
  The [1.0.0] section said it "works on any CoreML model, not just this one".
  The spec dump is model-agnostic, but the script loads
  `MLModel('BERTSQUADFP16.mlmodel')` by name and probes the `wordIDs` /
  `wordTypes` keys, so a foreign model needs two edits first. The [1.0.1]
  section corrected exactly that sentence in the README and left it standing in
  the changelog.
- **The `### Measured` block says which of its numbers came from an
  instrument.** It presented all six values as measurements and "not estimates".
  Throughput, latency and the threading result come from `ane_benchmark.py`
  runs; the ANE load and the two wattages were read off Activity Monitor by eye,
  without `powermetrics`. The block now separates the two.
- **The `download_model.sh` entry no longer contradicts itself.** It described
  the script as fetching the model and, two lines further on, as only pointing
  at Apple's download page. It does both, in different branches: with
  `ANE_MODEL_URL` set it downloads via `curl -fL`, without it prints the page
  and exits 1.
- **The [1.0.1] entry names a source that carries something.** It credited the
  reconstructed [1.0.0] section to "the README and the original release"; the
  body of the v1.0.0 release is the two words "Initial release". The section
  came from the README and the v1.0.0 tree.

### Changed

- **The bold line of an entry carries the effect, not the identifier.** The file
  or function it happened in moved into the paragraph below it, where it is
  still the anchor that makes the entry checkable.
- **The changelog is plain ASCII.** Em dashes and ellipses were replaced by the
  punctuation or the word they stood in for.
- **Every section heading carries the release headline**
  (`## [X.Y.Z] - YYYY-MM-DD: <headline>`). That is where the release title now
  comes from, so the two cannot drift apart.

### Added

- **A tag push publishes the GitHub release.**
  `.github/workflows/release.yml` cuts the body out of `CHANGELOG.md` between
  the version heading and the next `##` or the link definitions, strips the
  leading blank line, and takes the title from the headline in that same
  heading. It refuses to run if the version has no section or more than one.

### Upgrade notes

Nothing to do. No script, no dependency and no interface changed in this
release. Anyone reading the older release pages will find them worded
differently than before; the versions they describe are untouched.

## [1.1.0] - 2026-08-08: Installing this project no longer pulls in a deep-learning framework

Removes `torch` from `requirements.txt`. Nothing in this repository ever
imported it: `ane_working.py` uses `transformers` for `BertTokenizer` alone,
and the inference is CoreML's job. The pin had been carrying a deep-learning
framework into every install of a project that never calls one.

MINOR rather than PATCH, because `pip install -r requirements.txt` now produces
a different environment than it did in 1.0.x. The pins are this project's
promise, so a changed pin is never a patch.

### Removed

- **A fresh install no longer downloads PyTorch.** `torch==2.5.1` left
  `requirements.txt`. Verified before removal, on 2026-08-08:
  - No source file imports `torch`, directly or indirectly.
  - `coremltools==8.3.0` does not depend on it either. Resolved next to the
    two remaining pins, it adds `attrs`, `cattrs`, `mpmath`, `protobuf`,
    `pyaml` and `sympy`, and no framework.
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

- **The README's advisory figures are measured, dated and sourced.** It
  claimed `pip-audit` "will flag ~20 advisories against them ... two in
  `torch`", without saying when. Measured against OSV on 2026-08-08: 44 for
  `transformers` 4.36.2, 22 for `torch` 2.5.1, and none for `coremltools`
  8.3.0 or `numpy` 1.26.3. The section carries those figures, names its
  database and date, and drops the `torch` half.
- **The import warning that appears without a framework is explained where
  people meet it.** `transformers` prints "None of PyTorch, TensorFlow >= 2.0,
  or Flax have been found ..." on import; the README now says so. It is the
  visible cost of this release, it is harmless here, and letting people
  discover it unexplained would look like a broken setup.

## [1.0.1] - 2026-08-08: A failed inference can no longer be counted as throughput

Maintenance release. One real defect in the benchmark, one README claim the
code did not back up, and the project infrastructure this repository never had:
a changelog, a CI gate and a pinned lint configuration. No behaviour of the
working demo changed, and no dependency pin moved.

### Fixed

- **A failed inference aborts the benchmark instead of inflating its result.**
  `run_pool()` in `ane_benchmark.py` dropped finished futures with
  `[f for f in futures if not f.done()]` without ever calling `.result()`, so
  an exception raised inside `model.predict` disappeared without a trace while
  the submission counter kept climbing. The `pool(12)` figure could therefore
  report throughput for work that never completed, and `--mode full` is exactly
  the run behind the "threading does not help" claim in the README. Finished
  futures are now resolved. This fix has **not** been re-measured on Apple
  Silicon; it cannot make a successful run report differently, only turn a
  silent failure into a visible one.
- **The README says which half of `model_inspect.py` a foreign model can use.**
  It promised "run it on any CoreML model". The spec dump is indeed
  model-agnostic, but the acceptance probe is wired to the file name
  `BERTSQUADFP16.mlmodel` and to the `wordIDs` / `wordTypes` input keys, so a
  foreign model needs two edits first. The table entry now says which half is
  generic and what to change.
- **`ane_benchmark.py` can be started the way its shebang says.** It was
  checked in as mode `100644` while `ane_working.py`, `model_inspect.py` and
  `download_model.sh` were all `100755`, all four carrying a shebang. Now
  consistent, and enforced by the `EXE` ruleset.

### Added

- **The project has a changelog from this release on.** `CHANGELOG.md`, with
  the 1.0.0 section reconstructed from the README and the v1.0.0 tree.
- **Every push is gated by lint, a syntax check and a pin check.**
  `.github/workflows/lint.yml` is the repository's first CI. Three jobs:
  `python` (ruff plus a syntax check), `shell` (ShellCheck plus `bash -n`), and
  `requirements`, which fails the build if any line in `requirements.txt` is not
  pinned with `==`. The exact pins are this project's central promise, so a
  loosened one should break the build rather than be discovered months later.
  Python comes from `.python-version`, so the gate runs on the interpreter the
  README names.
- **The lint gate no longer moves with the ruff version.** `ruff.toml` carries
  an explicit rule selection. An unconfigured `ruff check` gates against a
  moving target: ruff 0.16 reported findings on an unchanged tree that earlier
  versions did not. The selection also enables `BLE`, which the two
  `# noqa: BLE001` directives in the sources had been assuming all along, and
  `RUF100`, which reports such directives once they go stale.

### Note on scope

The scripts require macOS and an Apple Neural Engine, so CI checks syntax and
lint only; it cannot execute them. There is no test suite. Anything that
depends on actually running a model still has to be verified by hand on Apple
Silicon.

## [1.0.0] - 2026-05-19: Reaching the Apple Neural Engine from Python

First public release. The repository is the cleaned-up trail of a two-hour
session that reached the Apple Neural Engine of an M4 Pro from Python through
CoreML: a working BERT-SQuAD question-answering demo plus the introspection
tool that makes the model's undocumented input contract discoverable. It is a
learning artifact, not a production inference service.

### Added

- **Real question answering runs on the ANE from Python.** `ane_working.py`
  tokenises real (context, question) pairs, runs them through the CoreML
  BERT-SQuAD model on the ANE and extracts the answer span. Original session
  script, kept essentially as-is.
- **The model's input contract can be read off the model itself.**
  `model_inspect.py` dumps the CoreML model spec (input names, dtypes, shapes)
  and systematically probes which dtype/shape combinations the model actually
  accepts. This is the tool that surfaced the gotchas below. The spec dump
  works on any CoreML model; the probe is wired to `BERTSQUADFP16.mlmodel` and
  to the `wordIDs` / `wordTypes` keys.
- **The threading non-result is reproducible on your own hardware.**
  `ane_benchmark.py` is a throughput probe with `--mode {fast,blitz,full}`,
  consolidated from three working throwaway benchmark scripts of the original
  session. `--mode full` demonstrates that threading does not help, because
  CoreML serialises inference.
- **The Apple model is fetched, never redistributed.** `download_model.sh`
  downloads the BERT-SQuAD FP16 model from the URL in `ANE_MODEL_URL`, and
  prints Apple's download page instead when that variable is unset. The model
  is Apple's property; the repository carries the fetch, not the file.
- **A fresh install reproduces the environment the session ran on.**
  `requirements.txt` carries exact pins and the reasoning behind them, next to
  `.python-version` (3.12.7).
- **The four undocumented facts that cost the debugging time are written
  down.** The README names them: input dtype must be `float64` and not `int32`;
  shape must be exactly `[1, 384]` and not `[384]`; the input keys are
  `wordIDs` / `wordTypes` and not the standard BERT `input_ids` /
  `token_type_ids`; and `coremltools` must be 8.3.0, because 7.x on Python 3.12
  fails with `Unable to load CoreML.framework`, an error that points nowhere
  near the version mismatch.

### Measured

Numbers from the original session on an M4 Pro Mac Mini with BERT-SQuAD FP16,
not a benchmark worth citing.

From `ane_benchmark.py` runs:

- Throughput ~10.5 inferences/s, latency ~95 ms per inference.
- Threading with 8 threads and a pool of 12 gives no improvement at all.

Read off Activity Monitor by eye, without `powermetrics`:

- ANE load ~13 %, roughly 1.6 W of the ~12 W the panel showed. Most of the
  accelerator sits idle.

The low utilisation and the threading non-result are the interesting part; the
raw throughput number is not.

[1.1.3]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.1.3
[1.1.2]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.1.2
[1.1.1]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.1.1
[1.1.0]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.1.0
[1.0.1]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.0.1
[1.0.0]: https://github.com/fidpa/apple-neural-engine-from-python/releases/tag/v1.0.0
