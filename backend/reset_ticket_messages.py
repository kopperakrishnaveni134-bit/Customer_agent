from app.database import SessionLocal
from app.models import Message


def main():
    db = SessionLocal()

    try:
        ticket_id = 1

        # --------------------------------------------------
        # DELETE ALL EXISTING MESSAGES FOR TICKET 1
        # --------------------------------------------------

        deleted = (
            db.query(Message)
            .filter(Message.ticket_id == ticket_id)
            .delete(synchronize_session=False)
        )

        db.commit()

        print(f"Deleted {deleted} old messages.")

        # --------------------------------------------------
        # CREATE ONE CLEAN CONVERSATION
        # --------------------------------------------------

        messages = [
            Message(
                ticket_id=ticket_id,
                sender="customer",
                content=(
                    "My payment keeps failing. "
                    "I already tried refreshing the page."
                ),
            ),

            Message(
                ticket_id=ticket_id,
                sender="agent",
                content=(
                    "I understand. Since refreshing the page "
                    "did not help, let's try resetting your "
                    "checkout session."
                ),
            ),

            Message(
                ticket_id=ticket_id,
                sender="customer",
                content=(
                    "That worked. The payment went through."
                ),
            ),
        ]

        db.add_all(messages)
        db.commit()

        print("Created clean conversation.")
        print()
        print("Ticket 1 now contains:")
        print("1. Customer → Payment is failing")
        print("2. Agent → Reset checkout session")
        print("3. Customer → Payment worked")

    finally:
        db.close()


if __name__ == "__main__":
    main()