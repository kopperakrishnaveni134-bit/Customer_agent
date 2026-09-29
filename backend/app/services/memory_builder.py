from app.models import (
    Customer,
    CustomerEnvironment,
    Ticket,
    Message,
    TroubleshootingAttempt,
    FrustrationEvent,
)


def build_ticket_memory(
    customer: Customer,
    ticket: Ticket,
):
    """
    Convert a support ticket and its history
    into a meaningful memory for Hindsight.
    """

    environment = customer.environment

    environment_text = "Environment information unavailable."

    if environment:
        environment_text = (
            f"Operating system: {environment.operating_system}. "
            f"Browser: {environment.browser}. "
            f"Device: {environment.device}. "
            f"App version: {environment.app_version}. "
            f"Plan: {environment.customer_plan}."
        )

    messages = sorted(
        ticket.messages,
        key=lambda message: message.created_at
    )

    conversation_lines = []

    for message in messages:
        conversation_lines.append(
            f"{message.sender}: {message.content}"
        )

    conversation = "\n".join(conversation_lines)

    attempts = sorted(
        ticket.troubleshooting_attempts,
        key=lambda attempt: attempt.created_at
    )

    solution_lines = []

    for attempt in attempts:
        solution_lines.append(
            f"- {attempt.solution} → {attempt.result}. "
            f"{attempt.notes or ''}"
        )

    solutions = "\n".join(solution_lines)

    frustration_events = sorted(
        customer.frustration_events,
        key=lambda event: event.created_at
    )

    frustration_lines = []

    for event in frustration_events:
        frustration_lines.append(
            f"- Level: {event.level}, "
            f"score: {event.score}. "
            f"Reason: {event.reason or 'Not specified'}"
        )

    frustration_history = "\n".join(
        frustration_lines
    )

    memory = f"""
Customer support experience.

Customer:
Name: {customer.name}
Email: {customer.email}
Plan: {customer.plan}

Environment:
{environment_text}

Ticket:
Ticket number: {ticket.ticket_number}
Issue: {ticket.subject}
Description: {ticket.description}
Issue type: {ticket.issue_type}
Known issue: {ticket.known_issue}
Status: {ticket.status}

Conversation:
{conversation}

Troubleshooting and solution outcomes:
{solutions}

Customer frustration history:
{frustration_history}

Important support learning:
Remember this customer's environment, previous support history,
failed troubleshooting attempts, successful solutions, and
frustration level so future support interactions can avoid
repeating unsuccessful steps and can start with solutions that
previously worked.
""".strip()

    return memory