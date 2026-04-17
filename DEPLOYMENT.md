# Deployment Information — Day 12 AI Agent

## Public URL
[https://2a202600476-maiviethoang-day12-production.up.railway.app](https://2a202600476-maiviethoang-day12-production.up.railway.app)

## Platform
- **Hosting**: Railway
- **Database**: Railway Redis (Managed)
- **Runtime**: Docker (Python 3.11-slim)

## Test Commands

### 1. Health Check
Kiểm tra trạng thái sẵn sàng của Agent trên Cloud.
```bash
curl https://2a202600476-maiviethoang-day12-production.up.railway.app/health
```
**Kết quả mong đợi:** `{"status": "ok", "platform": "Railway", ...}`

### 2. API Test (Xác thực API Key)
Kiểm tra khả năng gọi Agent và theo dõi chi phí (Redis Cost Guard).
```bash
curl -X POST https://2a202600476-maiviethoang-day12-production.up.railway.app/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"question": "Deployment successful?"}'
```
**Kết quả mong đợi:** JSON có chứa trường `usage` với `cost_usd` > 0.

## Biến môi trường đã cấu hình (Secrets)
- `PORT`: Railway tự động cấp.
- `REDIS_URL`: Liên kết tới dịch vụ Redis nội bộ.
- `AGENT_API_KEY`: Khóa bảo mật API.
- `JWT_SECRET`: Khóa bí mật ký Token.

## Danh sách ảnh chụp (Screenshots)
- `screenshots/dashboard.png`: Giao diện quản lý Railway (Agent + Redis).
- `screenshots/running.png`: Kết quả gọi health check thành công.
- `screenshots/test.png`: Kết quả gọi API `/ask` có kèm thông tin usage từ Redis.
- `screenshots/ready.png`: Kết quả kiểm tra Production Readiness đạt 20/20 (100%).
