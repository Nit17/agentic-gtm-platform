from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .store import store
from .search import search_notes

app = FastAPI(title="Agentic GTM Platform API", version="0.1.0")


class ContactIn(BaseModel):
	name: str
	email: str
	company: Optional[str] = None


class Contact(ContactIn):
	id: int


class NoteIn(BaseModel):
	contact_id: int
	text: str


class Note(NoteIn):
	id: int


class SearchRequest(BaseModel):
	q: str
	limit: int = 5


class DecisionRequest(BaseModel):
	goal_description: str
	contact_id: Optional[int] = None


@app.get("/health")
async def health():
	return {"status": "ok", "version": app.version}


@app.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactIn):
	return store.create_contact(contact)


@app.get("/contacts", response_model=List[Contact])
async def list_contacts():
	return store.list_contacts()


@app.post("/notes", response_model=Note)
async def create_note(note: NoteIn):
	if not store.get_contact(note.contact_id):
		raise HTTPException(404, "contact not found")
	return store.create_note(note)


@app.get("/notes", response_model=List[Note])
async def list_notes():
	return store.list_notes()


@app.post("/search")
async def search(req: SearchRequest):
	results = search_notes(req.q, limit=req.limit)
	return {"results": results}


@app.post("/decide")
async def decide(req: DecisionRequest):
	# Placeholder decision logic
	actions = []
	if req.contact_id and store.get_contact(req.contact_id):
		actions.append({
			"type": "email",
			"payload": {
				"subject": f"Re: {req.goal_description}",
				"body": "Draft outreach based on goal.",
			},
			"confidence": 0.65,
			"referenced_evidence_ids": [],
		})
	return {"actions": actions}
