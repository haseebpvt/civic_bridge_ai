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
  -f tools/weather/weather_forecast_tool.py \
  -p tools/ \
  -r tools/weather/requirements.txt

#orchestrate tools import \
#  -k python \
#  -f tools/weather/weather_forecast_summarizer_tool.py \
#  -p tools/ \
#  -r tools/weather/requirements.txt


echo "✅ Done."

echo "Importing Agents"

orchestrate agents import -f agents/weather_agent.yaml

echo "✅ Done."
