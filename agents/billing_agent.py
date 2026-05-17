class BillingAgent:
    async def handle(self, params: dict) -> str:
        query = params["query"]
        return f"Thank you for your billing inquiry about '{query}'. Our billing team will review this and get back to you within 2 business hours. If you have any urgent payment issues, please call our support line."
