from typing import List, Dict, Any
from sqlalchemy.orm import Session


class PineconeRetrieverStub:
    def __init__(self):
        pass

    def search(self, db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # placeholder: implement when Pinecone is configured
        return []
