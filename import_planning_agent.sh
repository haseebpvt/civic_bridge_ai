#!/usr/bin/env bash
set -euo pipefail

echo "📦 Packaging & importing tools"

orchestrate tools import \
  -k python \
  -f tools/router/create_work_order_tool.py \
  -p tools/ \
  -r tools/router/requirements.txt


echo "✅ Done."

echo "Importing Agents"

orchestrate agents import -f agents/planning_agent.yaml

echo "✅ Done."
