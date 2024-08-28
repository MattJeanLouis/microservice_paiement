from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    plan_id = Column(String, index=True)
    status = Column(String)
    amount = Column(Float)
    currency = Column(String)
    interval = Column(String)  # 'month', 'year', etc.
    interval_count = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    provider = Column(String)
    provider_subscription_id = Column(String)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    transaction = relationship("Transaction", back_populates="subscription")