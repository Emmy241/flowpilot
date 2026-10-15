from app.auth import hash_password, verify_password, create_access_token, decode_access_token

# 1. hash + verify
h = hash_password("hunter2")
print("hash starts with $2b$:", h.startswith("$2b$"))
print("verify correct password:", verify_password("hunter2", h))
print("verify wrong password:", verify_password("wrong", h))

# 2. token round-trip
token = create_access_token("user-123")
print("\ntoken:", token[:40], "...")

uid = decode_access_token(token)
print("decoded user_id:", uid)

# 3. tampered token
bad = token[:-3] + "xxx"
print("tampered token decode:", decode_access_token(bad))
