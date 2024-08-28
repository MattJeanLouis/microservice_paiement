from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    provider = Column(String)
    provider_transaction_id = Column(String)
    created_at = Column(DateTime)
    checkout_url = Column(String, nullable=True)
    success_url = Column(String)
    cancel_url = Column(String)
    custom_metadata = Column(JSON, nullable=True)
    description = Column(String, nullable=True)
    subscription = relationship("Subscription", back_populates="transaction", uselist=False)