import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.bootstrap

from tools.db_client import Session, Order, setup_db

setup_db()
session = Session()
orders = session.query(Order).all()
print(f"Total Orders in DB: {len(orders)}")
for o in orders:
    print(f"- ID: {o.id}, Status: {o.status}")
session.close()
