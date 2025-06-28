#!/usr/bin/env bash
set -euo pipefail

echo "📦 Packaging & importing tools"

orchestrate tools import \
  -k python \
  -f tools/work_order/create_work_order_tool.py \
  -p tools/ \
  -r tools/work_order/requirements.txt

orchestrate tools import \
  -k python \
  -f tools/work_order/endity_extraction_tool.py \
  -p tools/ \
  -r tools/work_order/requirements.txt


echo "✅ Done."

echo "Importing Agents"

orchestrate agents import -f agents/work_order_agent.yaml

echo "✅ Done."
