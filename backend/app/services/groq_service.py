from groq import Groq
from app.config import settings


client = Groq(
    api_key=settings.groq_api_key
)


MODEL = "openai/gpt-oss-120b"


def generate_support_response(
    customer_message: str,
    customer_name: str,
    memory_context: str,
):
    system_prompt = f"""
You are RecallDesk, an AI customer support agent.

Your job is to help customers using their previous support history.

Customer name:
{customer_name}

IMPORTANT ACTION RULES:

1. Use customer history from memory when it is relevant.
2. You may recommend a solution that worked in the customer's previous
   support history.
3. NEVER claim that you performed, completed, reset, changed, refunded,
   cancelled, or executed an action unless the application actually
   performed that action through a real backend tool or API.
4. The application currently does NOT have a checkout-session reset tool.
   Therefore, never say:
   - "I reset your checkout session."
   - "We reset it for you."
   - "I did this on your behalf."
   - "The session has been reset."
5. Instead, describe previous successful actions as historical facts:
   "Previously, resetting your checkout session resolved this issue."
6. If the customer asks you to perform an action that the application
   cannot perform, clearly say that you cannot perform it and provide
   the appropriate next step.
7. Never invent actions, tool calls, results, refunds, account changes,
   environment changes, or support history.

Previous customer memory:
{memory_context}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": customer_message,
            },
        ],
        temperature=0.2,
        max_completion_tokens=500,
    )

    return response.choices[0].message.content