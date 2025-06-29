# Granite Agent - CivicBridge AI

A Watson Orchestrate-powered AI agent system for handling civic services, weather information, and work order management.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Watson Orchestrate environment
- IBM Cloud account with Watson services
- Twilio account (for WhatsApp integration)

### Environment Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd granite-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Copy the template file and add your credentials:
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` with your actual credentials (see [Environment Variables](#environment-variables) section below).

4. **Run the application:**
   ```bash
   python app.py
   ```

## 🔧 Environment Variables

All sensitive information has been extracted to environment variables for security. Configure these in your `.env` file:

### Required Environment Variables

#### Twilio Configuration
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

#### Watson Orchestrate Configuration
```bash
WATSON_BEARER_TOKEN=your_watson_orchestrate_bearer_token
WATSON_ORCHESTRATE_HOST=api.au-syd.watson-orchestrate.cloud.ibm.com
WATSON_ORCHESTRATE_INSTANCE_ID=your_watson_orchestrate_instance_id
WATSON_ORCHESTRATE_ORCHESTRATION_ID=your_watson_orchestrate_orchestration_id
```

#### Watson AI Configuration
```bash
WATSONX_APIKEY=your_watsonx_api_key
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_watsonx_project_id
```

#### IBM Watson Speech-to-Text Configuration
```bash
IBM_STT_API_KEY=your_ibm_stt_api_key
IBM_STT_SERVICE_URL=your_ibm_stt_service_url
```

#### Firebase Configuration
```bash
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
# For cloud deployment:
FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"your-project-id",...}'
```

### Optional Environment Variables

#### LangSmith Configuration (for debugging/monitoring)
```bash
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=your_langsmith_project_name
LANGSMITH_TRACING=true
```

## 🤖 Watson Orchestrate Configuration

### For Agents and Tools (Recommended Approach)

Instead of using `.env` files, Watson Orchestrate v1.5.0+ supports **connections** for credential management:

1. **Configure connections in Watson Orchestrate:**
   ```bash
   orchestrate env activate your-environment
   ```

2. **Set up credentials using connections:**
   - Navigate to your Watson Orchestrate dashboard
   - Go to "Connections" section
   - Create connections for:
     - Watson AI services
     - Firebase
     - Third-party APIs

3. **Import agents and tools:**
   ```bash
   # Import all agents and tools
   ./import_all.sh
   
   # Or import individually
   ./import_planning_agent.sh
   ./import_weather_agent.sh
   ./import_work_order_agent.sh
   ```

### Environment Variables for Watson Agents

For Watson Orchestrate agents, you can also configure environment variables directly in the deployment:

```bash
# Set environment variables in Watson Orchestrate
orchestrate env activate your-environment --apikey your-api-key

# Variables will be available to agents and tools
export WATSONX_APIKEY=your_watsonx_api_key
export FIREBASE_SERVICE_ACCOUNT_JSON='your_service_account_json'
```

## 📁 Project Structure

```
granite-agent/
├── agents/                     # Watson Orchestrate agent definitions
│   ├── planning_agent.yaml
│   ├── weather_agent.yaml
│   └── work_order_agent.yaml
├── tools/                      # Custom tools for agents
│   ├── router/                # Query routing tools
│   ├── weather/               # Weather-related tools
│   └── work_order/            # Work order management tools
├── knowledge_base/            # Knowledge base files
├── others/                    # Utility modules
│   ├── speech.py             # Speech processing
│   └── transcribe.py         # Audio transcription
├── app.py                    # Main FastAPI application
├── watson_orchestrate_api.py # Watson API client
├── .env.template            # Environment variables template
└── .env                     # Your environment variables (git-ignored)
```

## 🔒 Security Notes

- The `.env` file is automatically git-ignored for security
- Never commit actual credentials to version control
- Use Watson Orchestrate connections for production deployments
- Firebase service account files are bundled for local development but use environment variables for cloud deployment

## 🚀 Deployment

### Local Development
1. Configure `.env` file with your credentials
2. Run `python app.py`

### Watson Orchestrate Deployment
1. Use connections for credential management
2. Import agents using the provided scripts
3. Deploy using Watson Orchestrate ADK

### Cloud Deployment
1. Set environment variables in your cloud platform
2. Use `FIREBASE_SERVICE_ACCOUNT_JSON` for Firebase authentication
3. Ensure all required environment variables are available

## 📝 Agent Descriptions

- **Planning Agent**: Handles general planning and coordination tasks
- **Weather Agent**: Provides weather forecasts and related information
- **Work Order Agent**: Manages work order creation, PDF generation, and Firebase persistence

## 🛠️ Troubleshooting

### Common Issues

1. **Missing environment variables**: Check your `.env` file against `.env.template`
2. **Firebase authentication errors**: Ensure service account JSON is properly formatted
3. **Watson API errors**: Verify your Watson API keys and project IDs
4. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Getting Help

- Check Watson Orchestrate documentation
- Review Firebase setup guide: `FIREBASE_CLOUD_SETUP.md`
- Ensure all environment variables are properly configured

## 📄 License

[Add your license information here] 