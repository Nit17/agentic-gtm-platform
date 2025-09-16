import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
	resp = client.get("/health")
	assert resp.status_code == 200
	assert resp.json()["status"] == "ok"


def test_contacts_and_notes_and_search():
	# create contact
	c = client.post("/contacts", json={"name": "Alice", "email": "alice@example.com"}).json()
	assert c["id"] == 1
	# add notes
	n1 = client.post("/notes", json={"contact_id": c["id"], "text": "Discussed pricing for Agentic GTM"}).json()
	n2 = client.post("/notes", json={"contact_id": c["id"], "text": "Follow up about Pinecone vector DB"}).json()
	assert n1["id"] == 1 and n2["id"] == 2
	# search
	s = client.post("/search", json={"q": "pricing"}).json()
	assert len(s["results"]) >= 1
