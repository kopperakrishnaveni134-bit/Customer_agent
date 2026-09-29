import { useEffect, useState } from "react";

import {
  getCustomers,
  getTickets,
  getTicketMessages,
  sendAgentMessage,
} from "./api";

function App() {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const [tickets, setTickets] = useState([]);
  const [messages, setMessages] = useState([]);

  const [messageInput, setMessageInput] = useState("");
  const [sending, setSending] = useState(false);

  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [loadingConversation, setLoadingConversation] = useState(false);

  const [error, setError] = useState("");

  // =========================================================
  // LOAD CUSTOMERS
  // =========================================================

  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadCustomers() {
    try {
      setLoadingCustomers(true);
      setError("");

      const data = await getCustomers();

      setCustomers(data);

      if (data.length > 0) {
        await selectCustomer(data[0]);
      }
    } catch (err) {
      console.error(err);
      setError("Unable to connect to RecallDesk backend.");
    } finally {
      setLoadingCustomers(false);
    }
  }

  // =========================================================
  // SELECT CUSTOMER
  // =========================================================

  async function selectCustomer(customer) {
    try {
      setSelectedCustomer(customer);
      setLoadingConversation(true);
      setError("");

      const allTickets = await getTickets();

      const customerTickets = allTickets.filter(
        (ticket) => ticket.customer_id === customer.id
      );

      setTickets(customerTickets);

      if (customerTickets.length > 0) {
        const latestTicket = customerTickets[0];

        const ticketMessages = await getTicketMessages(
          latestTicket.id
        );

        setMessages(ticketMessages);
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error(err);
      setError("Unable to load customer support history.");
      setMessages([]);
    } finally {
      setLoadingConversation(false);
    }
  }

  // =========================================================
  // SEND MESSAGE TO AI AGENT
  // =========================================================

  async function handleSendMessage() {
    const text = messageInput.trim();

    if (!text || !selectedCustomer || sending) {
      return;
    }

    try {
      setSending(true);
      setError("");

      // Immediately show customer's new message
      const temporaryCustomerMessage = {
        id: `temp-customer-${Date.now()}`,
        sender: "customer",
        content: text,
      };

      setMessages((previous) => [
        ...previous,
        temporaryCustomerMessage,
      ]);

      setMessageInput("");

      // Call FastAPI → Hindsight Recall → Groq → Hindsight Retain
      const result = await sendAgentMessage(
        selectedCustomer.id,
        text
      );

      // Add AI response to conversation
      const agentMessage = {
        id: `temp-agent-${Date.now()}`,
        sender: "agent",
        content: result.response,
      };

      setMessages((previous) => [
        ...previous,
        agentMessage,
      ]);

    } catch (err) {
      console.error(err);

      setError(
        "The AI agent could not respond. Check the backend terminal."
      );
    } finally {
      setSending(false);
    }
  }

  // =========================================================
  // ENTER KEY
  // =========================================================

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="min-h-screen bg-slate-50">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="border-b border-slate-200 bg-white">

        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

          <div>

            <h1 className="text-xl font-bold text-slate-900">
              RecallDesk
            </h1>

            <p className="text-xs text-slate-500">
              AI Customer Support Console
            </p>

          </div>

          <div className="flex items-center gap-2">

            <div className="h-2.5 w-2.5 rounded-full bg-emerald-500" />

            <span className="text-sm text-slate-600">
              Agent Online
            </span>

          </div>

        </div>

      </header>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="mx-auto max-w-7xl px-6 py-6">

        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">


          {/* =================================================
              CUSTOMER SIDEBAR
          ================================================= */}

          <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">

            <div className="mb-4">

              <h2 className="font-semibold text-slate-900">
                Customers
              </h2>

              <p className="text-sm text-slate-500">
                Select a customer
              </p>

            </div>


            {loadingCustomers && (
              <p className="text-sm text-slate-500">
                Loading customers...
              </p>
            )}


            {error && (
              <p className="mb-3 text-sm text-red-500">
                {error}
              </p>
            )}


            <div className="space-y-2">

              {customers.map((customer) => (

                <button
                  key={customer.id}
                  onClick={() => selectCustomer(customer)}
                  className={`w-full rounded-lg p-3 text-left transition ${
                    selectedCustomer?.id === customer.id
                      ? "bg-slate-900 text-white"
                      : "hover:bg-slate-100"
                  }`}
                >

                  <div className="font-medium">
                    {customer.name}
                  </div>

                  <div
                    className={`mt-1 text-xs ${
                      selectedCustomer?.id === customer.id
                        ? "text-slate-300"
                        : "text-slate-500"
                    }`}
                  >
                    {customer.plan} · {customer.email}
                  </div>

                </button>

              ))}

            </div>

          </aside>


          {/* =================================================
              SUPPORT AREA
          ================================================= */}

          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">


            {/* SUPPORT HEADER */}

            <div className="border-b border-slate-200 p-5">

              <h2 className="text-lg font-semibold text-slate-900">
                Support Inbox
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                AI-powered customer support with persistent memory
              </p>

            </div>


            {!selectedCustomer ? (

              /* EMPTY STATE */

              <div className="flex min-h-[500px] items-center justify-center">

                <div className="text-center">

                  <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900 text-xl font-bold text-white">
                    AI
                  </div>

                  <h3 className="text-xl font-semibold">
                    Select a customer to start
                  </h3>

                </div>

              </div>

            ) : (

              /* CUSTOMER CONVERSATION */

              <div className="p-6">


                {/* CUSTOMER HEADER */}

                <div className="mb-6">

                  <h3 className="text-2xl font-semibold text-slate-900">
                    {selectedCustomer.name}
                  </h3>

                  <p className="text-sm text-slate-500">
                    {selectedCustomer.email} ·{" "}
                    {selectedCustomer.plan}
                  </p>

                </div>


                {/* =================================================
                    LATEST TICKET
                ================================================= */}

                {tickets.length > 0 && (

                  <div className="mb-5 rounded-lg border border-slate-200 bg-slate-50 p-4">

                    <div className="flex items-center justify-between">

                      <div>

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                          Latest Ticket
                        </p>

                        <h4 className="mt-1 font-semibold text-slate-900">
                          {tickets[0].subject}
                        </h4>

                      </div>

                      <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">
                        {tickets[0].status}
                      </span>

                    </div>

                    <p className="mt-2 text-sm text-slate-600">
                      {tickets[0].description}
                    </p>

                  </div>

                )}


                {/* =================================================
                    PREVIOUS CONVERSATION
                ================================================= */}

                <div>

                  <div className="mb-3 flex items-center justify-between">

                    <h4 className="font-semibold text-slate-900">
                      Previous Conversation
                    </h4>

                    <span className="text-xs text-slate-500">
                      {messages.length} messages
                    </span>

                  </div>


                  {loadingConversation ? (

                    <div className="rounded-lg border border-slate-200 p-5 text-sm text-slate-500">
                      Loading conversation...
                    </div>

                  ) : messages.length === 0 ? (

                    <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                      No previous conversation found.
                    </div>

                  ) : (

                    <div className="max-h-[420px] space-y-3 overflow-y-auto pr-2">

                      {messages.map((message) => (

                        <div
                          key={message.id}
                          className={`flex ${
                            message.sender === "customer"
                              ? "justify-start"
                              : "justify-end"
                          }`}
                        >

                          <div
                            className={`max-w-[75%] rounded-xl px-4 py-3 text-sm ${
                              message.sender === "customer"
                                ? "bg-slate-100 text-slate-800"
                                : "bg-slate-900 text-white"
                            }`}
                          >

                            <div className="mb-1 text-xs font-medium opacity-60">
                              {message.sender === "customer"
                                ? selectedCustomer.name
                                : "Support Agent"}
                            </div>

                            <div>
                              {message.content}
                            </div>

                          </div>

                        </div>

                      ))}

                    </div>

                  )}

                </div>


                {/* =================================================
                    AI CHAT BOX
                ================================================= */}

                <div className="mt-6 border-t border-slate-200 pt-5">

                  <div className="mb-2">

                    <h4 className="font-semibold text-slate-900">
                      Ask RecallDesk
                    </h4>

                    <p className="text-xs text-slate-500">
                      The agent will recall this customer's previous
                      support history before responding.
                    </p>

                  </div>


                  <div className="flex gap-3">

                    <textarea
                      value={messageInput}
                      onChange={(event) =>
                        setMessageInput(event.target.value)
                      }
                      onKeyDown={handleKeyDown}
                      disabled={sending}
                      rows={3}
                      placeholder="Example: My payment is failing again. What should I try?"
                      className="flex-1 resize-none rounded-lg border border-slate-300 p-3 text-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200 disabled:bg-slate-100"
                    />

                    <button
                      onClick={handleSendMessage}
                      disabled={
                        sending || !messageInput.trim()
                      }
                      className="self-end rounded-lg bg-slate-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {sending ? "Thinking..." : "Send"}
                    </button>

                  </div>


                  {sending && (
                    <p className="mt-2 text-xs text-slate-500">
                      RecallDesk is checking customer memory and
                      generating a response...
                    </p>
                  )}

                </div>


              </div>

            )}

          </section>

        </div>

      </main>

    </div>
  );
}

export default App;