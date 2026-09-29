from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db

from app.models import (
    Customer,
    CustomerEnvironment,
    Ticket,
    Message,
    TroubleshootingAttempt,
    FrustrationEvent,
)

from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    TicketCreate,
    TicketResponse,
    EnvironmentCreate,
    EnvironmentResponse,
    MessageCreate,
    MessageResponse,
    TroubleshootingCreate,
    TroubleshootingResponse,
    FrustrationCreate,
    FrustrationResponse,
)

from app.services.hindsight_service import (
    retain_memory,
    recall_memory,
    list_memories,
)

from app.services.memory_builder import (
    build_ticket_memory,
)

from app.services.groq_service import (
    generate_support_response,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(title="RecallDesk")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "message": "RecallDesk API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# CUSTOMER API
# ============================================================

@app.post(
    "/customers",
    response_model=CustomerResponse
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.email == customer.email)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer with this email already exists.",
        )

    db_customer = Customer(
        name=customer.name,
        email=customer.email,
        plan=customer.plan,
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


@app.get(
    "/customers",
    response_model=list[CustomerResponse]
)
def get_customers(
    db: Session = Depends(get_db),
):
    customers = (
        db.query(Customer)
        .order_by(Customer.id)
        .all()
    )

    return customers


# ============================================================
# TICKET API
# ============================================================

@app.post(
    "/tickets",
    response_model=TicketResponse
)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == ticket.customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    ticket_count = db.query(Ticket).count()

    ticket_number = f"TKT-{1001 + ticket_count}"

    db_ticket = Ticket(
        ticket_number=ticket_number,
        customer_id=ticket.customer_id,
        subject=ticket.subject,
        description=ticket.description,
        status="open",
        issue_type=ticket.issue_type,
        known_issue=ticket.known_issue,
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


@app.get(
    "/tickets",
    response_model=list[TicketResponse]
)
def get_tickets(
    db: Session = Depends(get_db),
):
    tickets = (
        db.query(Ticket)
        .order_by(Ticket.id.desc())
        .all()
    )

    return tickets


@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    return ticket


# ============================================================
# CUSTOMER ENVIRONMENT API
# ============================================================

@app.post(
    "/environment",
    response_model=EnvironmentResponse
)
def create_or_update_environment(
    environment: EnvironmentCreate,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == environment.customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    existing_environment = (
        db.query(CustomerEnvironment)
        .filter(
            CustomerEnvironment.customer_id
            == environment.customer_id
        )
        .first()
    )

    if existing_environment:
        existing_environment.operating_system = (
            environment.operating_system
        )
        existing_environment.browser = (
            environment.browser
        )
        existing_environment.device = (
            environment.device
        )
        existing_environment.app_version = (
            environment.app_version
        )
        existing_environment.customer_plan = (
            environment.customer_plan
        )

        db.commit()
        db.refresh(existing_environment)

        return existing_environment

    db_environment = CustomerEnvironment(
        customer_id=environment.customer_id,
        operating_system=environment.operating_system,
        browser=environment.browser,
        device=environment.device,
        app_version=environment.app_version,
        customer_plan=environment.customer_plan,
    )

    db.add(db_environment)
    db.commit()
    db.refresh(db_environment)

    return db_environment


@app.get(
    "/environment/{customer_id}",
    response_model=EnvironmentResponse
)
def get_environment(
    customer_id: int,
    db: Session = Depends(get_db),
):
    environment = (
        db.query(CustomerEnvironment)
        .filter(
            CustomerEnvironment.customer_id
            == customer_id
        )
        .first()
    )

    if not environment:
        raise HTTPException(
            status_code=404,
            detail="Environment information not found.",
        )

    return environment


# ============================================================
# MESSAGE API
# ============================================================

@app.post(
    "/messages",
    response_model=MessageResponse
)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == message.ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    db_message = Message(
        ticket_id=message.ticket_id,
        sender=message.sender,
        content=message.content,
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


@app.get(
    "/tickets/{ticket_id}/messages",
    response_model=list[MessageResponse]
)
def get_ticket_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    messages = (
        db.query(Message)
        .filter(Message.ticket_id == ticket_id)
        .order_by(Message.created_at)
        .all()
    )

    return messages


# ============================================================
# TROUBLESHOOTING API
# ============================================================

@app.post(
    "/troubleshooting",
    response_model=TroubleshootingResponse
)
def create_troubleshooting(
    troubleshooting: TroubleshootingCreate,
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == troubleshooting.ticket_id
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    attempt = TroubleshootingAttempt(
        ticket_id=troubleshooting.ticket_id,
        solution=troubleshooting.solution,
        result=troubleshooting.result,
        notes=troubleshooting.notes,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


@app.get(
    "/tickets/{ticket_id}/troubleshooting",
    response_model=list[TroubleshootingResponse]
)
def get_ticket_troubleshooting(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    attempts = (
        db.query(TroubleshootingAttempt)
        .filter(
            TroubleshootingAttempt.ticket_id
            == ticket_id
        )
        .order_by(
            TroubleshootingAttempt.created_at
        )
        .all()
    )

    return attempts


# ============================================================
# FRUSTRATION API
# ============================================================

@app.post(
    "/frustration",
    response_model=FrustrationResponse
)
def create_frustration_event(
    frustration: FrustrationCreate,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == frustration.customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    event = FrustrationEvent(
        customer_id=frustration.customer_id,
        ticket_id=frustration.ticket_id,
        level=frustration.level,
        score=frustration.score,
        reason=frustration.reason,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@app.get(
    "/customers/{customer_id}/frustration",
    response_model=list[FrustrationResponse]
)
def get_customer_frustration(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    events = (
        db.query(FrustrationEvent)
        .filter(
            FrustrationEvent.customer_id
            == customer_id
        )
        .order_by(
            FrustrationEvent.created_at
        )
        .all()
    )

    return events


# ============================================================
# HINDSIGHT MEMORY - RETAIN TICKET
# ============================================================

@app.post(
    "/memory/customers/{customer_id}/tickets/{ticket_id}/retain"
)
def retain_ticket_memory(
    customer_id: int,
    ticket_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.customer_id == customer_id,
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found for this customer.",
        )

    memory_content = build_ticket_memory(
        customer,
        ticket,
    )

    result = retain_memory(
        content=memory_content,
        context="Customer support ticket",
        document_id=f"ticket-{ticket.id}-support-memory",
        metadata={
            "customer_id": str(customer.id),
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "issue_type": ticket.issue_type or "",
        },
    )

    return {
        "status": "success",
        "message": "Ticket memory retained in Hindsight.",
        "customer_id": customer_id,
        "ticket_id": ticket_id,
        "memory": memory_content,
        "hindsight_result": str(result),
    }


# ============================================================
# HINDSIGHT MEMORY - RECALL
# ============================================================

@app.get(
    "/memory/customers/{customer_id}/recall"
)
def recall_customer_memory(
    customer_id: int,
    query: str,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    customer_query = (
        f"Customer: {customer.name}. "
        f"Customer ID: {customer.id}. "
        f"Support question: {query}"
    )

    result = recall_memory(
        query=customer_query,
        max_tokens=3000,
    )

    memories = []

    for memory in result.results:
        memories.append(
            {
                "text": memory.text,
                "type": memory.type,
            }
        )

    return {
        "status": "success",
        "customer_id": customer_id,
        "query": query,
        "memories": memories,
    }


# ============================================================
# HINDSIGHT MEMORY - LIST
# ============================================================

@app.get("/memory/list")
def get_memories():
    result = list_memories(limit=50)

    memories = []

    for memory in result.items:
        memories.append(
            {
                "memory": str(memory),
            }
        )

    return {
        "status": "success",
        "count": len(memories),
        "memories": memories,
    }


# ============================================================
# AI SUPPORT AGENT
# ============================================================

@app.post("/agent/respond")
def agent_respond(
    customer_id: int,
    message: str,
    db: Session = Depends(get_db),
):
    # 1. Find customer
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    # 2. Find the customer's latest open ticket
    ticket = (
        db.query(Ticket)
        .filter(Ticket.customer_id == customer_id)
        .order_by(Ticket.id.desc())
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="No ticket found for this customer.",
        )

    # 3. Prevent duplicate customer messages
    existing_message = (
        db.query(Message)
        .filter(
            Message.ticket_id == ticket.id,
            Message.sender == "customer",
            Message.content == message,
        )
        .first()
    )

    if not existing_message:
        customer_message = Message(
            ticket_id=ticket.id,
            sender="customer",
            content=message,
        )

        db.add(customer_message)
        db.commit()
        db.refresh(customer_message)

    # 4. Recall relevant customer history from Hindsight
    memory_query = (
        f"Customer {customer.name} support history. "
        f"Current issue: {message}"
    )

    memory_result = recall_memory(
        query=memory_query,
        max_tokens=3000,
    )

    memory_parts = []

    for memory in memory_result.results:
        memory_parts.append(memory.text)

    memory_context = "\n\n".join(memory_parts)

    # 5. Generate AI support response
    response = generate_support_response(
        customer_message=message,
        customer_name=customer.name,
        memory_context=memory_context,
    )

    # 6. Prevent duplicate agent messages
    existing_agent_message = (
        db.query(Message)
        .filter(
            Message.ticket_id == ticket.id,
            Message.sender == "agent",
            Message.content == response,
        )
        .first()
    )

    if not existing_agent_message:
        agent_message = Message(
            ticket_id=ticket.id,
            sender="agent",
            content=response,
        )

        db.add(agent_message)
        db.commit()
        db.refresh(agent_message)

    # 7. Retain the complete interaction in Hindsight
    interaction_memory = f"""
Customer support interaction.

Customer:
Name: {customer.name}
Customer ID: {customer.id}

Ticket:
Ticket Number: {ticket.ticket_number}
Ticket ID: {ticket.id}

Customer message:
{message}

AI support response:
{response}

Important:
This interaction is part of the customer's ongoing support history.
Remember useful information, troubleshooting outcomes, preferences,
environment details, and customer sentiment that may help future
support interactions.

Do not claim that an action was performed unless the system actually
performed that action.
""".strip()

    retain_result = retain_memory(
        content=interaction_memory,
        context="Customer support conversation",
        metadata={
            "customer_id": str(customer.id),
            "ticket_id": str(ticket.id),
            "source": "agent_response",
        },
    )

    # 8. Return everything needed by the frontend
    return {
        "status": "success",
        "customer_id": customer_id,
        "customer_name": customer.name,
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "customer_message": message,
        "memory_used": memory_parts,
        "response": response,
        "memory_retained": True,
        "retain_result": str(retain_result),
    }
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    # -----------------------------------------
    # 1. RECALL PREVIOUS CUSTOMER MEMORY
    # -----------------------------------------

    memory_query = (
        f"Customer {customer.name} support history. "
        f"Current issue: {message}"
    )

    memory_result = recall_memory(
        query=memory_query,
        max_tokens=3000,
    )

    memory_parts = []

    for memory in memory_result.results:
        memory_parts.append(memory.text)

    memory_context = "\n\n".join(memory_parts)

    # -----------------------------------------
    # 2. GENERATE AI RESPONSE
    # -----------------------------------------

    response = generate_support_response(
        customer_message=message,
        customer_name=customer.name,
        memory_context=memory_context,
    )

    # -----------------------------------------
    # 3. RETAIN NEW INTERACTION
    # -----------------------------------------

    interaction_memory = f"""
Customer support interaction.

Customer:
Name: {customer.name}
Customer ID: {customer.id}

Customer message:
{message}

AI support response:
{response}

Important:
This interaction is part of the customer's ongoing support history.
Remember useful information, troubleshooting outcomes, preferences,
environment details, and customer sentiment that may help future
support interactions.
""".strip()

    retain_result = retain_memory(
        content=interaction_memory,
        context="Customer support conversation",
        metadata={
            "customer_id": str(customer.id),
            "source": "agent_response",
        },
    )

    # -----------------------------------------
    # 4. RETURN RESPONSE
    # -----------------------------------------

    return {
        "status": "success",
        "customer_id": customer_id,
        "customer_name": customer.name,
        "customer_message": message,
        "memory_used": memory_parts,
        "response": response,
        "memory_retained": True,
        "retain_result": str(retain_result),
    }