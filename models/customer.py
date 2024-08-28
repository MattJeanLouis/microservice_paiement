from sqlalchemy import Column, Integer, String
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    provider_customer_id = Column(String, unique=True, index=True)
    email = Column(String)
    name = Column(String)