from tools.vector_search import search_kb

class FAQAgent:
    async def handle(self, params: dict) -> str:
        results = search_kb(params["query"])
        if results:
            return "\n".join(results)
        return "No FAQ found for that query."
