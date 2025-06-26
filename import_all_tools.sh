#!/usr/bin/env bash
set -euo pipefail

# (optional) point to a specific orchestrate environment
# orchestrate config set active-environment <YOUR_ENV_ID>

echo "📦 Packaging & importing tools"

orchestrate tools import \
  -k python \
  -f tools/weather/weather_tool.py \
  -p tools/ \
  -r tools/weather/requirements.txt

orchestrate tools import \
  -k python \
  -f tools/weather/weather_summarizer_tool.py \
  -p tools/ \
  -r tools/weather/requirements.txt

echo "✅ Done."
