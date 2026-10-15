from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Fresh user (unique email to avoid collision on reruns)
import uuid
email = f"chat_{uuid.uuid4().hex[:8]}@b.com"
r = client.post("/auth/signup", json={"email": email, "password": "hunter2"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=== plain chat ===")
r = client.post("/chat", json={"message": "Say hello briefly."}, headers=headers)
print(r.status_code, r.json())

print("\n=== task intent ===")
r = client.post("/chat", json={"message": "Remind me to call mom tomorrow at 6pm"}, headers=headers)
data = r.json()
print(r.status_code)
print("assistant content:", data["message"]["content"])
print("approval:", data.get("approval"))

conv_id = data["conversation_id"]
approval_id = data["approval"]["id"] if data.get("approval") else None

if approval_id:
    print("\n=== approve ===")
    r = client.post(f"/approvals/{approval_id}/approve", headers=headers)
    print(r.status_code, r.json())

    print("\n=== try to approve again ===")
    r = client.post(f"/approvals/{approval_id}/approve", headers=headers)
    print(r.status_code, r.json())

print("\n=== conversation messages ===")
r = client.get(f"/conversations/{conv_id}/messages", headers=headers)
for m in r.json():
    print("-", m["role"], "|", m["content"], "|", m["tool_calls"])

print("\n=== list conversations ===")
r = client.get("/conversations", headers=headers)
print(r.status_code, [c["title"] for c in r.json()])

print("\n=== reject flow ===")
r = client.post("/chat", json={"message": "Create a task to buy milk", "conversation_id": conv_id}, headers=headers)
data = r.json()
if data.get("approval"):
    ap_id = data["approval"]["id"]
    r = client.post(f"/approvals/{ap_id}/reject", headers=headers)
    print("reject:", r.status_code, r.json()["status"])
else:
    print("no approval returned, assistant said:", data["message"]["content"])
