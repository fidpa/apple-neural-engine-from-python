#!/usr/bin/env bash
# Fetches the BERT-SQuAD FP16 CoreML model.
#
# Source: Apple Core ML Models — https://developer.apple.com/machine-learning/models/
# (model "BERT-SQuAD"). It is Apple's asset and is intentionally NOT
# redistributed in this repository. Grab the current download link from
# that page and pass it via ANE_MODEL_URL (Apple rotates CDN paths).
set -euo pipefail

MODEL="BERTSQUADFP16.mlmodel"
MODEL_URL="${ANE_MODEL_URL:-}"

if [[ -f "$MODEL" ]]; then
  echo "✓ $MODEL already present."
  exit 0
fi

if [[ -z "$MODEL_URL" ]]; then
  cat <<'EOF'
✗ ANE_MODEL_URL is not set.

  1. Open https://developer.apple.com/machine-learning/models/
  2. Find "BERT-SQuAD", copy the .mlmodel download URL
  3. Re-run:

     ANE_MODEL_URL='https://.../BERTSQUADFP16.mlmodel' ./download_model.sh
EOF
  exit 1
fi

echo "→ Downloading $MODEL ..."
curl -fL --progress-bar -o "$MODEL" "$MODEL_URL"
echo "✓ Done: $(du -h "$MODEL" | cut -f1) — verify the checksum against Apple's page."
