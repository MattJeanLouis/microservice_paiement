from pydantic import BaseModel

class CustomerCreate(BaseModel):
    email: str
    name: str

class CustomerResponse(BaseModel):
    id: int
    provider_customer_id: str
    email: str
    name: str

    class Config:
        from_attributes = True