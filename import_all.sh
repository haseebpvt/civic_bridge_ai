#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting complete import of all agents and tools..."
echo "=================================================="

# Function to run script and handle errors
run_script() {
    local script_name=$1
    echo ""
    echo "📋 Running $script_name..."
    echo "----------------------------------------"
    
    if [ -f "$script_name" ]; then
        if bash "$script_name"; then
            echo "✅ $script_name completed successfully"
        else
            echo "❌ $script_name failed"
            exit 1
        fi
    else
        echo "❌ Script $script_name not found"
        exit 1
    fi
}

# Import order matters - dependencies first, then orchestrating agents
echo "🔧 Importing foundational tools and agents..."

# 1. Import Weather Agent (foundational weather tools)
run_script "import_weather_agent.sh"

# 2. Import Work Order Agent (work order tools including Firebase persistence)
run_script "import_work_order_agent.sh"

# 3. Import Planning Agent (orchestrates weather and work order agents)
run_script "import_planning_agent.sh"

echo ""
echo "=================================================="
echo "🎉 All imports completed successfully!"
echo ""
echo "📊 Summary:"
echo "  ✅ Weather Agent & Tools"
echo "  ✅ Work Order Agent & Tools (including Firebase persistence)"
echo "  ✅ Planning Agent & Router Tools"
echo ""
echo "🚀 Your granite-agent system is ready to use!"
echo "==================================================" 