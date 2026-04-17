# -*- coding: utf-8 -*-
"""
Tập trung tất cả các biến cấu hình và cài đặt của ứng dụng.
"""
import os

# Thư mục gốc của dự án (đi lên 2 cấp từ file config.py này)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# === API Key Settings ===
API_KEY_NAME = "X-API-Key"
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "my-secret-key")

# === Cost Guard Settings ===
# Sử dụng đường dẫn tuyệt đối để đảm bảo file cost.json luôn được tìm thấy ở cùng một nơi
COST_FILE = os.path.join(PROJECT_ROOT, "cost.json")
BUDGET = 10.0  # USD

# === Redis Settings ===
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# === Rate Limiting Settings ===
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_PERIOD_SECONDS = 60

# === LLM Cost Estimation Settings ===
# Giả sử giá là $0.03 / 1K input tokens và $0.06 / 1K output tokens
# Chúng ta lấy trung bình là $0.045
AVG_TOKEN_PRICE = 0.045