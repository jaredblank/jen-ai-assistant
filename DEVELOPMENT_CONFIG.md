# JEN AI ASSISTANT - DEVELOPMENT CONFIGURATION

## ⚠️ IMPORTANT: DEVELOPMENT ENVIRONMENT ONLY

This configuration uses **SANDBOX/DEVELOPMENT** credentials to prevent any impact on production systems.

## 🔧 Development Settings Applied:

### Database
- **Environment**: `development` 
- **Database**: `Broker_Mgmt_New_Sandbox` (NOT production `Broker_Mgmt`)
- **Log Level**: `DEBUG` for detailed troubleshooting

### Phone & Voice Services  
- **ElevenLabs Agent**: `DEV_TEST_AGENT_ID` (NOT production agent)
- **Phone Number SID**: `DEV_TEST_PHONE_SID` (NOT production phone)
- **Twilio**: All test credentials (`DEV_TEST_*`)

### API Keys
- **JEN API Key**: `JenAI2025_DEV` (development suffix)
- **API Secret**: `EquityRachel2025ChatAPI_DEV` (development suffix)

## 🚫 Production Systems Protected:
- ❌ Production database `Broker_Mgmt` - NOT USED
- ❌ Production ElevenLabs agent `agent_6501k1bae0n2ebbs8dmvwgzjmbjy` - NOT USED  
- ❌ Production phone number SID `PNd7a8b8e2904cae40f0035b5c28e2dfbf` - NOT USED
- ❌ Production Twilio credentials - NOT USED

## ✅ Safe for Testing:
- Web API endpoints
- Database queries against sandbox data
- AI processing with OpenRouter
- Voice synthesis (no live calls)

## 📝 Notes:
- Service will show "degraded" health due to test Twilio credentials
- Voice features will work for synthesis but not live phone calls
- Database operations will use sandbox data only
- No impact on production systems or live customer interactions