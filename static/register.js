// static/register.js
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const registerButton = document.getElementById("registerButton");
const messageDiv = document.getElementById("message");
const messageText = document.getElementById("messageText");

async function handleRegister() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (!username || !password) { showMessage("Username and password required.", "error"); return; }
    
    registerButton.disabled = true;
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        showMessage(data.message, "success");
    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        registerButton.disabled = false;
    }
}

function showMessage(message, type) {
    messageText.textContent = message;
    messageDiv.className = type; // Use 'success' or 'error' as class
    messageDiv.classList.remove("hidden");
}
registerButton.addEventListener("click", handleRegister);