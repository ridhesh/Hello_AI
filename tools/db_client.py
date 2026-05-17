from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    user_id = Column(String)
    status = Column(String)
    total = Column(Float)
    created_at = Column(String)

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String)
    reason = Column(Text)
    created_at = Column(String)

engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)

def setup_db():
    """Initialize tables and seed sample data."""
    Base.metadata.create_all(engine)
    session = Session()
    if session.query(Order).count() == 0:
        orders = [
            Order(id='ORD001', user_id='u1', status='shipped', total=99.99, created_at=datetime.datetime.now().isoformat()),
            Order(id='ORD002', user_id='u2', status='pending', total=49.99, created_at=datetime.datetime.now().isoformat()),
            Order(id='ORD003', user_id='u3', status='delivered', total=29.99, created_at=datetime.datetime.now().isoformat()),
        ]
        session.add_all(orders)
        session.commit()
    session.close()

def get_order(order_id: str):
    session = Session()
    order = session.query(Order).filter(Order.id == order_id).first()
    session.close()
    if order:
        return {
            'id': order.id,
            'user_id': order.user_id,
            'status': order.status,
            'total': order.total,
            'created_at': order.created_at
        }
    return None

def create_ticket(session_id: str, reason: str) -> int:
    session = Session()
    ticket = Ticket(session_id=session_id, reason=reason, created_at=datetime.datetime.now().isoformat())
    session.add(ticket)
    session.commit()
    ticket_id = ticket.id
    session.close()
    return ticket_id
