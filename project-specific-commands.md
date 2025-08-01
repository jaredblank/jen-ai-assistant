# Jen AI Assistant - Project Specific Render Commands

## Project Configuration
```bash
export RENDER_API_KEY="YOUR_RENDER_API_KEY_HERE"
export OWNER_ID="tea-d1rf5j3e5dus73dl49og"
export SERVICE_ID="srv-d26jisruibrs739vvrv0"
export SERVICE_URL="https://jen-ai-assistant.onrender.com"
export REPO_URL="https://github.com/jaredblank/jen-ai-assistant"
```

## Quick Commands for This Project
```bash
# Check deployment status
curl -X GET "https://api.render.com/v1/services/srv-d26jisruibrs739vvrv0/deploys" -H "Authorization: Bearer YOUR_RENDER_API_KEY_HERE" -H "Content-Type: application/json"

# Test service health
curl -X GET "https://jen-ai-assistant.onrender.com/health" --max-time 10

# Get environment variables
curl -X GET "https://api.render.com/v1/services/srv-d26jisruibrs739vvrv0/env-vars" -H "Authorization: Bearer YOUR_RENDER_API_KEY_HERE" -H "Content-Type: application/json"

# Suspend service (for maintenance)
curl -X PATCH "https://api.render.com/v1/services/srv-d26jisruibrs739vvrv0" -H "Authorization: Bearer YOUR_RENDER_API_KEY_HERE" -H "Content-Type: application/json" -d '{"suspended": "suspended"}'

# Resume service
curl -X PATCH "https://api.render.com/v1/services/srv-d26jisruibrs739vvrv0" -H "Authorization: Bearer YOUR_RENDER_API_KEY_HERE" -H "Content-Type: application/json" -d '{"suspended": "not_suspended"}'
```

## Current Configuration
- **Service Name**: jen-ai-assistant
- **Runtime**: Docker
- **Region**: Oregon
- **Plan**: Starter
- **Environment**: Development (sandbox credentials)
- **Database**: Broker_Mgmt_New_Sandbox
- **Health Check**: /health
- **Start Command**: uvicorn main:app --host 0.0.0.0 --port $PORT