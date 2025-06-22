// static/login.js
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const messageDiv = document.getElementById("message");
const messageText = document.getElementById("messageText");

async function handleLogin() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (!username || !password) { showMessage("Username and password required.", "error"); return; }
    
    loginButton.disabled = true;
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        localStorage.setItem('accessToken', data.access_token);
        showMessage("Login successful! Redirecting...", "success");
        setTimeout(() => { window.location.href = '/'; }, 1500);
    } catch (error) {
        showMessage(error.message, "error");
        loginButton.disabled = false;
    }
}

function showMessage(message, type) {
    messageText.textContent = message;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");
}
loginButton.addEventListener("click", handleLogin);