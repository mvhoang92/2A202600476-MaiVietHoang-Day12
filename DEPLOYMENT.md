# Deployment Information

## Public URL
- **URL:** [Điền URL Railway/Render của bạn ở đây, ví dụ: https://my-agent.up.railway.app]

## Platform
- Railway / Render / Cloud Run (Xóa bớt cái không dùng)

## Test Commands

### 1. Health Check
```bash
curl [URL_CUA_BAN]/health
# Kết quả mong đợi: {"status": "ok", ...}
```

### 2. API Test (with authentication)
```bash
curl -X POST [URL_CUA_BAN]/ask \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Xin chào, bạn có thể giúp gì cho tôi?"}'
```

### 3. Rate Limiting Test
```bash
# Chạy lệnh này nhiều lần liên tiếp để thấy lỗi 429 (mặc định là 20 req/min)
for i in {1..25}; do curl -X POST [URL_CUA_BAN]/ask -H "X-API-Key: my-secret-key" -H "Content-Type: application/json" -d '{"question": "test"}'; done
```

## Environment Variables Set
Cấu hình trên Platform (Railway/Render):
- `PORT`: 8000
- `REDIS_URL`: [Link Redis của bạn]
- `AGENT_API_KEY`: my-secret-key
- `OPENAI_API_KEY`: [Key của bạn hoặc để trống để dùng mock]
- `ENVIRONMENT`: production

## Screenshots
Vui lòng chụp ảnh và lưu vào thư mục `screenshots/` với tên tương ứng:
1. **Deployment Success**: `screenshots/railway-deploy-success.png`
2. **Health Check**: `screenshots/health-check.png`
3. **Rate Limit Blocked**: `screenshots/rate-limit-blocked.png`
4. **Cost Guard Blocked**: `screenshots/cost-guard-blocked.png`
