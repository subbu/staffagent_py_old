import datetime
import uuid
from pydantic import BaseModel


class User():
    def __init__(
            self,
            name: str,
            id: str,
            type: str,
            email: str,
            phone_number: str,
            resume_content: str | None,
            captured_at: datetime.datetime,
            blob_url: str | None,
            position_applied_for: str,
            company_name: str) -> None:
        self.id = id  # : uuid.UUID  # UNIQUE
        self.name = name  # : str
        self.type = type  # : str  # TXT or PDF
        self.email = email  # : str
        self.phone_number = phone_number  # : str
        self.resume_content = resume_content  # : str | None
        self.captured_at = captured_at  # : datetime.datetime
        self.blob_url = blob_url  # : str | None
        self.position_applied_for = position_applied_for  # : str  # FOR NAMESPACE
        self.company_name = company_name  # : str  # INDEX FOR COMPANY


class Document(BaseModel):
    id: uuid.UUID  # UNIQUE
    name: str
    type: str  # TXT or PDF
    email: str
    phone_number: str
    resume_content: str | None
    captured_at: datetime.datetime
    blob_url: str | None
    position_applied_for: str  # FOR NAMESPACE
    company_name: str  # INDEX FOR COMPANY


class Chunk(BaseModel):
    id: uuid.UUID
    chunk_id: uuid.UUID
    metadata: dict[str, str | list[str]]
    blob_url: str
