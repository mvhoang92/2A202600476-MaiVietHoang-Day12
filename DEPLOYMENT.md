# Deployment Information

## Public URL
https://2a202600476-maiviethoang-day12-production.up.railway.app/

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://2a202600476-maiviethoang-day12-production.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": ...}
```

### API Test (với Authentication - Dùng Key của bạn)
```bash
curl -X POST https://2a202600476-maiviethoang-day12-production.up.railway.app/ask \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## Environment Variables Set
- `PORT`: 8000
- `AGENT_API_KEY`: [my-secret-key]
- `LOG_LEVEL`: INFO

## Screenshots
- [Link to deployment screenshot](screenshots/railway_deploy.png)
