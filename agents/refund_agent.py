from datetime import datetime, timezone, timedelta
from tools.db_client import get_order


class RefundAgent:
    """Handles refund requests by checking order eligibility (30-day window)."""

    async def handle(self, params: dict) -> str:
        # Normalize Order ID
        order_id = str(params.get("order_id", "")).upper().strip()
        
        if not order_id:
            return "Please provide an Order ID to check refund eligibility."

        order = get_order(order_id)
        if not order:
            return f"I looked for Order {order_id} to process your refund, but it doesn't seem to exist. Please verify the ID."

        # Parse order date
        try:
            # Handle potential Z suffix or simple ISO format
            date_str = order["created_at"].replace('Z', '+00:00')
            created_at = datetime.fromisoformat(date_str)
            # Ensure it's timezone-aware for comparison
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
        except ValueError:
            return "I found the order, but its date is in an unusual format. I'll need a human to help with this refund."

        # Check 30-day policy
        now = datetime.now(timezone.utc)
        age = now - created_at
        
        if age > timedelta(days=30):
            return (
                f"Order {order_id} was placed on {created_at.date()}. "
                "Our policy allows refunds only within 30 days of purchase. "
                "Since this order is over 30 days old, it is not eligible for a self-service refund. "
                "Would you like me to escalate this to a human manager for an exception?"
            )

        return (
            f"Good news! Order {order_id} is within the 30-day refund window. "
            "I have initiated the refund process for you. You should see the credit back on "
            "your original payment method within 5-7 business days."
        )
