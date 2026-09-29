# RecallDesk 🧠

## AI Customer Support Agent That Remembers

RecallDesk is an AI-powered customer support agent designed to solve one of the most frustrating problems in customer support:

> **Customers should not have to repeat their history every time they contact support.**

Traditional support agents and stateless AI chatbots often treat each conversation as a new interaction. They may know what the customer is asking right now, but they don't necessarily remember what happened during previous tickets, which troubleshooting steps failed, what actually solved the problem, what environment the customer uses, or how frustrated the customer became.

RecallDesk introduces **persistent customer memory** into the support workflow.

It combines:

- **Hindsight** → long-term memory and recall
- **Groq** → AI response generation
- **SQLite** → structured customer and support data
- **FastAPI** → backend API
- **React + Vite** → support dashboard

The result is a support agent that can use previous customer experiences when handling new problems.

---

# 🎯 The Problem

Customer support often follows this pattern:

```text
Customer has a problem
        ↓
Contacts support
        ↓
Explains the problem
        ↓
Tries troubleshooting
        ↓
Problem gets resolved
        ↓
Conversation ends

Later, the same customer encounters a similar problem.

Customer returns
        ↓
New support conversation
        ↓
Customer explains everything again
        ↓
Agent asks questions that were already answered
        ↓
Previously failed solutions may be suggested again

This creates several problems:

1. Repeated explanations

Customers have to repeatedly explain:

What happened
What they already tried
Their environment
Previous ticket history
What eventually fixed the issue
2. Lost troubleshooting knowledge

A previous ticket may contain valuable information:
Refresh page → Failed

Reset checkout session → Worked
A future support interaction should be able to use that knowledge.

3. Lack of customer context

Support responses can become generic when the system doesn't remember:

Operating system
Browser
Device
Application version
Customer plan
Previous issues
Previous solutions
Frustration level
4. Repeating failed troubleshooting

If a customer already tried something and it failed, suggesting the same step again creates unnecessary frustration.

💡 The RecallDesk Solution

RecallDesk gives the support agent persistent memory.

Instead of treating every interaction independently:

Current Message
      ↓
Generic Response

RecallDesk works like this:

Current Message
      ↓
Retrieve Relevant Customer History
      ↓
Hindsight Memory
      ↓
Combine Current Issue + Previous Context
      ↓
Groq
      ↓
Personalized Support Response
      ↓
Store New Interaction
      ↓
Future Conversations Can Recall It

The agent can therefore answer questions using information learned from previous support interactions.

