import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from app.config import settings

# JWT Config
ALGORITHM = "HS256"
security_bearer = HTTPBearer(auto_error=False)
security_apikey = APIKeyHeader(name="X-API-Key", auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate a JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)

async def verify_user(
    api_key: str = Security(security_apikey),
    token: HTTPAuthorizationCredentials = Depends(security_bearer)
) -> dict:
    """
    Dual authentication: JWT preferred, fallback to API Key.
    """
    # 1. Check JWT Token
    if token:
        try:
            payload = jwt.decode(token.credentials, settings.jwt_secret, algorithms=[ALGORITHM])
            return {
                "id": payload.get("sub"),
                "role": payload.get("role", "user"),
                "type": "jwt"
            }
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    # 2. Check API Key
    if api_key and api_key == settings.agent_api_key:
        return {
            "id": "default_bot",
            "role": "admin",
            "type": "apikey"
        }

    raise HTTPException(
        status_code=401,
        detail="Authentication required: X-API-Key header or Bearer Token"
    )
