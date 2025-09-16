import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from . import models
from .settings import RETRIEVER_BACKEND
from .retriever import TfidfRetriever, ChromaRetriever, PineconeRetrieverStub, PineconeRetriever

app = FastAPI(title="Agentic GTM Platform API", version="0.2.0")

# Create tables if not exist (for dev).
Base.metadata.create_all(bind=engine)


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
def get_retriever():
	if RETRIEVER_BACKEND == "chroma":
		return ChromaRetriever()
	if RETRIEVER_BACKEND == "pinecone":
		if PineconeRetriever is not None:
			try:
				return PineconeRetriever()
			except Exception:
				# If pinecone env/deps not set, degrade gracefully to stub
				return PineconeRetrieverStub()
		return PineconeRetrieverStub()
	return TfidfRetriever()


class DecisionRequest(BaseModel):
	goal_description: str
	contact_id: Optional[int] = None


@app.get("/health")
async def health():
	return {"status": "ok", "version": app.version}


@app.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactIn, db: Session = Depends(get_db)):
	c = models.Contact(name=contact.name, email=contact.email, company=contact.company)
	db.add(c)
	db.commit()
	db.refresh(c)
	return Contact(id=c.id, name=c.name, email=c.email, company=c.company)


@app.get("/contacts", response_model=List[Contact])
async def list_contacts(db: Session = Depends(get_db)):
	rows = db.query(models.Contact).all()
	return [Contact(id=r.id, name=r.name, email=r.email, company=r.company) for r in rows]


@app.post("/notes", response_model=Note)
async def create_note(note: NoteIn, db: Session = Depends(get_db)):
	c = db.get(models.Contact, note.contact_id)
	if not c:
		raise HTTPException(404, "contact not found")
	n = models.Note(contact_id=note.contact_id, text=note.text)
	db.add(n)
	db.commit()
	db.refresh(n)
	return Note(id=n.id, contact_id=n.contact_id, text=n.text)


@app.get("/notes", response_model=List[Note])
async def list_notes(db: Session = Depends(get_db)):
	rows = db.query(models.Note).all()
	return [Note(id=r.id, contact_id=r.contact_id, text=r.text) for r in rows]


@app.post("/search")
async def search(req: SearchRequest, db: Session = Depends(get_db)):
	retriever = get_retriever()
	results = retriever.search(db, req.q, limit=req.limit)
	return {"results": results}


# Email tool adapter (interface + stub)
class EmailRequest(BaseModel):
	to: List[str]
	subject: str
	body: str


@app.post("/tools/email/send")
async def send_email(req: EmailRequest):
	# Use SendGrid if configured; otherwise dry-run
	api_key = os.getenv("SENDGRID_API_KEY")
	from_addr = os.getenv("EMAIL_FROM_ADDRESS")
	if api_key and from_addr:
		try:
			import sendgrid
			from sendgrid.helpers.mail import Mail
			sg = sendgrid.SendGridAPIClient(api_key)
			message = Mail(from_email=from_addr, to_emails=req.to, subject=req.subject, plain_text_content=req.body)
			response = sg.client.mail.send.post(request_body=message.get())
			return {"status": "sent", "provider": "sendgrid", "code": response.status_code}
		except Exception as e:
			# Do not leak secrets; return safe error
			raise HTTPException(status_code=502, detail=f"Email provider error: {type(e).__name__}")
	# Fallback dry-run
	return {"status": "queued", "provider": "dry-run", "to": req.to, "subject": req.subject}


@app.post("/decide")
async def decide(req: DecisionRequest, db: Session = Depends(get_db)):
	# Placeholder decision logic
	actions = []
	if req.contact_id and db.get(models.Contact, req.contact_id):
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
