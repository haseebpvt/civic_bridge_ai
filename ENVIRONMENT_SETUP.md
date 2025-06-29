# Environment Setup Guide

This guide covers two approaches for managing sensitive information in the Granite Agent project.

## 🔐 Approach 1: Environment Variables (.env files)

### For Local Development and Traditional Deployment

1. **Copy the environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit the `.env` file with your credentials:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Required credentials to configure:**

   #### Twilio (WhatsApp Integration)
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Authentication Token

   #### Watson Orchestrate
   - `WATSON_BEARER_TOKEN`: Your Watson Orchestrate Bearer Token (JWT)
   - `WATSON_ORCHESTRATE_HOST`: Watson Orchestrate API host
   - `WATSON_ORCHESTRATE_INSTANCE_ID`: Your Watson Orchestrate instance ID
   - `WATSON_ORCHESTRATE_ORCHESTRATION_ID`: Your orchestration ID

   #### Watson AI (watsonx.ai)
   - `WATSONX_APIKEY`: Your Watson AI API key
   - `WATSONX_URL`: Watson AI service URL
   - `WATSONX_PROJECT_ID`: Your Watson AI project ID

   #### IBM Watson Speech-to-Text
   - `IBM_STT_API_KEY`: Your IBM STT API key
   - `IBM_STT_SERVICE_URL`: Your IBM STT service URL

   #### Firebase (for work order persistence)
   - `FIREBASE_DATABASE_URL`: Your Firebase Realtime Database URL
   - `FIREBASE_STORAGE_BUCKET`: Your Firebase Storage bucket name
   - `FIREBASE_SERVICE_ACCOUNT_JSON`: Complete JSON service account (for cloud deployment)

   #### LangSmith (Optional - for debugging)
   - `LANGSMITH_API_KEY`: Your LangSmith API key
   - `LANGSMITH_PROJECT`: Your LangSmith project name

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

## 🚀 Approach 2: Watson Orchestrate Connections (Recommended)

### For Watson Orchestrate v1.5.0+ Production Deployment

Watson Orchestrate now supports **connections** for credential management, which is more secure and easier to manage.

### 1. Set up Watson Orchestrate Environment

```bash
# Install Watson Orchestrate ADK
pip install ibm-watsonx-orchestrate==1.5.1

# Configure your environment
orchestrate env add -n your-environment -u https://your-watson-orchestrate-url

# Activate the environment
orchestrate env activate your-environment --apikey your-api-key
```

### 2. Create Connections

Instead of environment variables, create connections in Watson Orchestrate:

#### Watson AI Connection
```bash
# Create Watson AI connection
orchestrate connections create \
  --name "watsonx-ai" \
  --type "watsonx" \
  --config '{
    "api_key": "your_watsonx_api_key",
    "url": "https://us-south.ml.cloud.ibm.com",
    "project_id": "your_project_id"
  }'
```

#### Firebase Connection
```bash
# Create Firebase connection
orchestrate connections create \
  --name "firebase" \
  --type "firebase" \
  --config '{
    "service_account_json": "your_service_account_json",
    "database_url": "https://your-project-id.firebaseio.com",
    "storage_bucket": "your-project-id.appspot.com"
  }'
```

#### Third-party API Connections
```bash
# Create Twilio connection
orchestrate connections create \
  --name "twilio" \
  --type "http" \
  --config '{
    "account_sid": "your_twilio_account_sid",
    "auth_token": "your_twilio_auth_token"
  }'

# Create IBM STT connection
orchestrate connections create \
  --name "ibm-stt" \
  --type "ibm-watson" \
  --config '{
    "api_key": "your_ibm_stt_api_key",
    "service_url": "your_ibm_stt_service_url"
  }'
```

### 3. Update Agent and Tool Configurations

Modify your agent YAML files to use connections instead of hardcoded credentials:

#### Example: agents/weather_agent.yaml
```yaml
spec_version: v1
kind: native
name: weather_agent
llm: watsonx/ibm/granite-3-3-8b-instruct
connections:
  - name: watsonx-ai
    type: watsonx
tools:
  - weather_forecast_tool
```

#### Example: Tool Configuration
```python
# In your tool files, use connection references instead of environment variables
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

@tool(
    name="example_tool",
    description="Example tool using connections",
    permission=ToolPermission.READ_ONLY,
    connections=["watsonx-ai", "firebase"]
)
def example_tool(param: str):
    # Watson Orchestrate will automatically inject connection credentials
    # You can access them through the tool context
    pass
```

### 4. Import Agents and Tools

```bash
# Import all agents and tools
./import_all.sh

# Or import individually
orchestrate agents import agents/weather_agent.yaml
orchestrate tools import tools/weather/
orchestrate tools import tools/work_order/
```

## 🔄 Migration from .env to Connections

If you're migrating from environment variables to connections:

1. **Identify all environment variables** used in your project
2. **Create corresponding connections** in Watson Orchestrate
3. **Update agent YAML files** to reference connections
4. **Modify tool code** to use connection context instead of environment variables
5. **Test thoroughly** before deploying to production

## 🛠️ Troubleshooting

### Environment Variable Issues
- **Missing variables**: Compare your `.env` with `.env.template`
- **Invalid JSON**: Ensure Firebase JSON is properly escaped
- **Authentication errors**: Verify API keys are correct and active

### Connection Issues
- **Connection not found**: Verify connection names match agent configurations
- **Permission errors**: Ensure connections have appropriate permissions
- **Connection timeout**: Check network connectivity to Watson Orchestrate

### General Issues
- **Import errors**: Run `pip install -r requirements.txt`
- **Module not found**: Ensure Python path includes project directory
- **Firebase errors**: Check service account permissions

## 📚 Additional Resources

- [Watson Orchestrate Documentation](https://developer.watson-orchestrate.ibm.com/)
- [Watson Orchestrate ADK Guide](https://developer.watson-orchestrate.ibm.com/get-started/installing)
- [IBM Watson AI Documentation](https://cloud.ibm.com/docs/watson)
- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin)

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use connections for production** deployments
3. **Rotate credentials regularly**
4. **Limit API key permissions** to minimum required
5. **Monitor usage** of all connected services
6. **Use separate environments** for development/staging/production 