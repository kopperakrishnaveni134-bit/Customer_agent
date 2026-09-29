const API_URL = "http://127.0.0.1:8000";

async function request(url, options = {}) {
  const response = await fetch(`${API_URL}${url}`, options);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCustomers() {
  return request("/customers");
}

export async function getTickets() {
  return request("/tickets");
}

export async function getTicketMessages(ticketId) {
  return request(`/tickets/${ticketId}/messages`);
}

export async function getEnvironment(customerId) {
  return request(`/environment/${customerId}`);
}

export async function getTroubleshooting(ticketId) {
  return request(`/tickets/${ticketId}/troubleshooting`);
}

export async function getFrustration(customerId) {
  return request(`/customers/${customerId}/frustration`);
}

export async function getCustomerMemory(customerId, query) {
  return request(
    `/memory/customers/${customerId}/recall?query=${encodeURIComponent(query)}`
  );
}

export async function sendAgentMessage(customerId, message) {
  return request(
    `/agent/respond?customer_id=${customerId}&message=${encodeURIComponent(message)}`,
    {
      method: "POST",
    }
  );
}