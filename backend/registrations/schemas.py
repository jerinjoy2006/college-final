from pydantic import BaseModel


class RegistrationCreate(BaseModel):
    event_id: str
