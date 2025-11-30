const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chatBox = document.getElementById("chat-box");

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", function(e){
    if(e.key === "Enter") sendMessage();
});

async function sendMessage(){
    const message = input.value.trim();
    if(!message) return;

    addMessage("You", message);
    input.value = "";

    // Typing indicator
    const typingIndicator = document.createElement("p");
    typingIndicator.classList.add("chat-message","ai","typing");
    typingIndicator.textContent = "AI is typing";
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    try{
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        typingIndicator.remove();
        addMessage("AI", data.reply);
    } catch(e){
        typingIndicator.remove();
        addMessage("AI", "Sorry, something went wrong with AI response.");
    }
}

function addMessage(sender, text){
    const msg = document.createElement("p");
    msg.classList.add("chat-message");
    msg.classList.add(sender === "You" ? "user" : "ai");
    msg.textContent = `${sender}: ${text}`;
    chatBox.appendChild(msg);

    // Trigger animation
    void msg.offsetWidth;
    chatBox.scrollTop = chatBox.scrollHeight;
}
