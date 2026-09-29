from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    plan = Column(
        String(50),
        default="Free"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    tickets = relationship(
        "Ticket",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    environment = relationship(
        "CustomerEnvironment",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan"
    )

    frustration_events = relationship(
        "FrustrationEvent",
        back_populates="customer",
        cascade="all, delete-orphan"
    )


class CustomerEnvironment(Base):
    __tablename__ = "customer_environments"

    id = Column(Integer, primary_key=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        unique=True
    )

    operating_system = Column(
        String(100)
    )

    browser = Column(
        String(100)
    )

    device = Column(
        String(100)
    )

    app_version = Column(
        String(50)
    )

    customer_plan = Column(
        String(50)
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="environment"
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    subject = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(30),
        default="open"
    )

    issue_type = Column(
        String(100)
    )

    known_issue = Column(
        String(255)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    customer = relationship(
        "Customer",
        back_populates="tickets"
    )

    messages = relationship(
        "Message",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    troubleshooting_attempts = relationship(
        "TroubleshootingAttempt",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id"),
        nullable=False
    )

    sender = Column(
        String(30),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    ticket = relationship(
        "Ticket",
        back_populates="messages"
    )


class TroubleshootingAttempt(Base):
    __tablename__ = "troubleshooting_attempts"

    id = Column(
        Integer,
        primary_key=True
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id"),
        nullable=False
    )

    solution = Column(
        String(255),
        nullable=False
    )

    result = Column(
        String(30),
        nullable=False
    )

    notes = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    ticket = relationship(
        "Ticket",
        back_populates="troubleshooting_attempts"
    )


class FrustrationEvent(Base):
    __tablename__ = "frustration_events"

    id = Column(
        Integer,
        primary_key=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id"),
        nullable=True
    )

    level = Column(
        String(30),
        nullable=False
    )

    score = Column(
        Float,
        nullable=True
    )

    reason = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="frustration_events"
    )