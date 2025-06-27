import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from jose import jwt

# Set secret before importing app
os.environ["SUPABASE_JWT_SECRET"] = "testsecret"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.server import app, jobdb

client = TestClient(app)

def create_token(admin: bool):
    payload = {"sub": "123", "email": "user@example.com"}
    if admin:
        payload["app_metadata"] = {"roles": ["admin"]}
    token = jwt.encode(payload, os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256")
    return token

def test_missing_auth():
    r = client.get("/jobs")
    assert r.status_code == 422

def test_invalid_token():
    r = client.get("/jobs", headers={"Authorization": "Bearer bad"})
    assert r.status_code == 401

def test_non_admin_token():
    token = create_token(False)
    r = client.get("/jobs", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

def test_admin_token():
    token = create_token(True)
    jobdb.list_jobs = lambda owner_email=None: []
    r = client.get("/jobs", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

