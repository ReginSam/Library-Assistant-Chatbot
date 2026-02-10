document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("new-chat-form");
  const chatMessages = document.getElementById("new-chat-messages");

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const message = document.getElementById("new-message").value;

    if (!message) {
      alert("Please type a message.");
      return;
    }

    // Add user message to chat
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = `You: ${message}`;
    chatMessages.appendChild(userMessage);

    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Send message to the server
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ message }),
    });

    const data = await response.text();

    // Add bot response to chat
    const botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot");
    botMessage.textContent = `Bot: ${data}`;
    chatMessages.appendChild(botMessage);

    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Clear input field
    document.getElementById("new-message").value = "";
  });
});