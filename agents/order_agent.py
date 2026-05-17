from tools.db_client import get_order, Session, Order

class OrderAgent:
    async def handle(self, params: dict) -> str:
        # 1. Get the ID and clean it up
        raw_id = str(params.get("order_id", "")).strip()
        # Handle common mistakes (Zero vs Letter O)
        order_id = raw_id.upper().replace('0RD', 'ORD')
        
        logger_prefix = f"[DEBUG: Looking for {order_id}] "
        
        # 2. Try exact match
        order = get_order(order_id)
        
        # 3. If no exact match, try a fuzzy search in the DB
        if not order:
            session = Session()
            # Look for IDs that contain the user's input
            fuzzy_order = session.query(Order).filter(Order.id.contains(order_id)).first()
            if fuzzy_order:
                order = {
                    'id': fuzzy_order.id,
                    'status': fuzzy_order.status,
                    'total': fuzzy_order.total,
                    'created_at': fuzzy_order.created_at
                }
            session.close()

        if order:
            # Return a VERY explicit string so the AI can't ignore it
            return (f"DATABASE_SUCCESS: Found order record for {order['id']}. "
                    f"Current Status is '{order['status'].upper()}'. "
                    f"Total amount: ${order['total']}. "
                    f"Placed on: {order['created_at'][:10]}.")
        
        return f"DATABASE_ERROR: No order matching '{raw_id}' exists in the system."
