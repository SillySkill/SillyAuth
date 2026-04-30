# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = "webhook-hub-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
USER_ID = "33"
EMAIL = "hughwang@sillymd.com"

# 生成过期时间为 24 小时后
exp_time = datetime.now(timezone.utc) + timedelta(hours=24)
iat_time = datetime.now(timezone.utc)

payload = {
    "sub": USER_ID,
    "email": EMAIL,
    "exp": int(exp_time.timestamp()),
    "iat": int(iat_time.timestamp())
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(f"JWT Token (24小时有效):")
print(token)
print()
print(f"过期时间: {exp_time}")
print(f"过期时间戳: {int(exp_time.timestamp())}")
