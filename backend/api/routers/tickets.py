"""
Tickets Router
Mock API for escalation ticket management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter()


class TicketCreate(BaseModel):
    patient_id: Optional[str]
    subject: str
    description: str
    priority: str
    category: str
    created_by: str


class TicketResponse(BaseModel):
    id: str
    patient_id: Optional[str]
    subject: str
    description: str
    priority: str
    status: str
    category: str
    created_by: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]


# Mock ticket storage
MOCK_TICKETS = {
    "TKT001": {
        "id": "TKT001",
        "patient_id": "PAT001",
        "subject": "Claim CLM003 requires additional documentation",
        "description": "Patient's chest x-ray claim requires prior authorization documentation",
        "priority": "high",
        "status": "open",
        "category": "claims",
        "created_by": "Dr. Johnson",
        "assigned_to": "Billing Team",
        "created_at": "2024-01-21T09:00:00",
        "updated_at": "2024-01-21T09:00:00",
        "resolved_at": None
    }
}


@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate):
    """Create a new escalation ticket"""
    ticket_id = f"TKT{uuid.uuid4().hex[:6].upper()}"
    
    new_ticket = {
        "id": ticket_id,
        "patient_id": ticket.patient_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "priority": ticket.priority,
        "status": "open",
        "category": ticket.category,
        "created_by": ticket.created_by,
        "assigned_to": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "resolved_at": None
    }
    
    MOCK_TICKETS[ticket_id] = new_ticket
    return TicketResponse(**new_ticket)


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str):
    """Retrieve ticket details"""
    ticket = MOCK_TICKETS.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return TicketResponse(**ticket)


@router.get("/tickets")
async def list_tickets(patient_id: Optional[str] = None, status: Optional[str] = None):
    """List all tickets, optionally filtered"""
    tickets = list(MOCK_TICKETS.values())
    
    if patient_id:
        tickets = [t for t in tickets if t["patient_id"] == patient_id]
    
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    
    return {"tickets": tickets, "count": len(tickets)}


@router.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, status: str, assigned_to: Optional[str] = None):
    """Update ticket status"""
    ticket = MOCK_TICKETS.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket["status"] = status
    ticket["assigned_to"] = assigned_to or ticket["assigned_to"]
    ticket["updated_at"] = datetime.now()
    
    if status == "resolved":
        ticket["resolved_at"] = datetime.now()
    
    return TicketResponse(**ticket)
