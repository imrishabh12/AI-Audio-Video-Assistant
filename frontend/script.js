async function processVideo() {

    const urlInput = document.getElementById("videoUrl");
    const language = document.getElementById("language").value;

    const processBtn = document.getElementById("processBtn");
    const loading = document.getElementById("loading");
    const results = document.getElementById("results");
    const errorBox = document.getElementById("error");

    const source = urlInput.value.trim();

    if (!source) {
        showError("Please enter a YouTube URL.");
        return;
    }

    errorBox.classList.add("hidden");
    results.classList.add("hidden");
    loading.classList.remove("hidden");

    processBtn.disabled = true;
    processBtn.textContent = "Processing...";

    try {

        const response = await fetch("/api/process", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                source: source,
                language: language
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong.");
        }

        document.getElementById("title").textContent =
            data.title || "Untitled Meeting";

        document.getElementById("summary").textContent =
            data.summary || "No summary available.";

        document.getElementById("actionItems").textContent =
            data.action_items || "No action items found.";

        document.getElementById("decisions").textContent =
            data.key_decisions || "No key decisions found.";

        document.getElementById("questions").textContent =
            data.open_questions || "No open questions found.";

        results.classList.remove("hidden");

        document.getElementById("chatMessages").innerHTML = `
            <div class="message assistant">
                <div class="avatar">AI</div>
                <div class="message-content">
                    Your meeting has been processed. Ask me anything about it.
                </div>
            </div>
        `;

        window.scrollTo({
            top: results.offsetTop - 30,
            behavior: "smooth"
        });

    } catch (error) {

        console.error(error);

        showError(error.message);

    } finally {

        loading.classList.add("hidden");

        processBtn.disabled = false;
        processBtn.textContent = "Process Video";
    }
}


async function askQuestion() {

    const input = document.getElementById("questionInput");
    const question = input.value.trim();

    if (!question) {
        return;
    }

    addMessage(question, "user");

    input.value = "";

    const thinkingId = addThinkingMessage();

    try {

        const response = await fetch("/api/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        removeThinkingMessage(thinkingId);

        if (!response.ok) {
            throw new Error(data.detail || "Unable to get an answer.");
        }

        addMessage(data.answer, "assistant");

    } catch (error) {

        removeThinkingMessage(thinkingId);

        addMessage(
            "Error: " + error.message,
            "assistant"
        );
    }
}


function addMessage(text, type) {

    const chatMessages = document.getElementById("chatMessages");

    const message = document.createElement("div");

    message.className = `message ${type}`;

    if (type === "assistant") {

        message.innerHTML = `
            <div class="avatar">AI</div>
            <div class="message-content"></div>
        `;

    } else {

        message.innerHTML = `
            <div class="message-content"></div>
            <div class="avatar">You</div>
        `;
    }

    message.querySelector(".message-content").textContent = text;

    chatMessages.appendChild(message);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function addThinkingMessage() {

    const chatMessages = document.getElementById("chatMessages");

    const id = "thinking-" + Date.now();

    const message = document.createElement("div");

    message.id = id;
    message.className = "message assistant";

    message.innerHTML = `
        <div class="avatar">AI</div>
        <div class="message-content">
            Thinking...
        </div>
    `;

    chatMessages.appendChild(message);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}


function removeThinkingMessage(id) {

    const message = document.getElementById(id);

    if (message) {
        message.remove();
    }
}


function handleEnter(event) {

    if (event.key === "Enter") {
        askQuestion();
    }
}


function showError(message) {

    const errorBox = document.getElementById("error");

    errorBox.textContent = message;

    errorBox.classList.remove("hidden");

    errorBox.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}