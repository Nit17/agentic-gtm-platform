from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel


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


@dataclass
class Store:
	contacts: List[Contact]
	notes: List[Note]
	_contact_seq: int
	_note_seq: int

	def create_contact(self, contact: ContactIn) -> Contact:
		self._contact_seq += 1
		c = Contact(id=self._contact_seq, **contact.model_dump())
		self.contacts.append(c)
		return c

	def list_contacts(self) -> List[Contact]:
		return self.contacts

	def get_contact(self, contact_id: int) -> Optional[Contact]:
		return next((c for c in self.contacts if c.id == contact_id), None)

	def create_note(self, note: NoteIn) -> Note:
		self._note_seq += 1
		n = Note(id=self._note_seq, **note.model_dump())
		self.notes.append(n)
		return n

	def list_notes(self) -> List[Note]:
		return self.notes


store = Store(contacts=[], notes=[], _contact_seq=0, _note_seq=0)
