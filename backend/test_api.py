from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== /health ===")
print(client.get("/health").json())

print("\n=== signup ===")
r = client.post("/auth/signup", json={"email": "a@b.com", "password": "hunter2"})
print(r.status_code, r.json())
token = r.json().get("access_token")

print("\n=== duplicate signup ===")
r2 = client.post("/auth/signup", json={"email": "a@b.com", "password": "hunter2"})
print(r2.status_code, r2.json())

print("\n=== login ===")
r3 = client.post("/auth/login", json={"email": "a@b.com", "password": "hunter2"})
print(r3.status_code, r3.json())

print("\n=== login wrong password ===")
r4 = client.post("/auth/login", json={"email": "a@b.com", "password": "nope"})
print(r4.status_code, r4.json())

print("\n=== /me without token ===")
print(client.get("/me").status_code)

print("\n=== /me with token ===")
r5 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
print(r5.status_code, r5.json())
