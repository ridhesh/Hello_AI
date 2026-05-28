import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tools.bootstrap

import logging

# Completely silence the buggy ChromaDB telemetry messages
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
# Silence specific multiprocessing/resource_tracker noise if desired
logging.getLogger("uvicorn.error").addFilter(lambda record: "telemetry" not in record.getMessage())

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from gateway.router import router
from tools.db_client import setup_db, engine, Ticket

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run DB setup on startup."""
    setup_db()
    yield

app = FastAPI(
    title="Agentic AI Customer Support API",
    description="REST API backed by Claude tool_use, ChromaDB, SQLite, and Redis.",
    version="1.1.0",
    lifespan=lifespan,
)

# Mount UI assets
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

@app.get("/", tags=["UI"])
async def read_index():
    """Serve the Chat UI."""
    return FileResponse("static/index.html")

@app.get("/dashboard", tags=["UI"])
async def read_dashboard():
    """Serve the Support Dashboard."""
    return FileResponse("static/dashboard.html")

@app.get("/tickets", tags=["Data"])
async def get_all_tickets():
    """Fetch all support tickets from the database."""
    with Session(engine) as session:
        tickets = session.query(Ticket).order_by(Ticket.id.desc()).all()
        return [
            {
                "id": t.id,
                "session_id": t.session_id,
                "reason": t.reason,
                "created_at": t.created_at
            }
            for t in tickets
        ]

@app.delete("/tickets/{ticket_id}", tags=["Data"])
async def resolve_ticket(ticket_id: int):
    """Resolve and delete a support ticket."""
    from tools.db_client import delete_ticket
    from fastapi import HTTPException
    success = delete_ticket(ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "success", "message": f"Ticket #{ticket_id} resolved."}

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Simple liveness probe."""
    return {"status": "ok"}
