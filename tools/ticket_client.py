from tools.db_client import create_ticket

def create_support_ticket(session_id: str, reason: str) -> str:
    ticket_id = create_ticket(session_id, reason)
    return f"Ticket #{ticket_id} created. A human agent will contact you within 24 hours."
