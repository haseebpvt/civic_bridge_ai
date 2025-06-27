#!/usr/bin/env bash
set -euo pipefail

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

orchestrate tools import \
  -k python \
  -f tools/weather/weather_forcast_tool.py \
  -p tools/ \
  -r tools/weather/requirements.txt

orchestrate tools import \
  -k python \
  -f tools/weather/weather_forcast_summarizer.py \
  -p tools/ \
  -r tools/weather/requirements.txt

echo "✅ Done."
