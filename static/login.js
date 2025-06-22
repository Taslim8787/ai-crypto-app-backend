// login.js

// This must be the same URL from your other JS files
const BACKEND_URL = "";

// Get references to HTML elements
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const messageDiv = document.getElementById("message");
const messageText = document.getElementById("messageText");

async function handleLogin() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        showMessage("Username and password cannot be empty.", "error");
        return;
    }

    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";

    try {
        // Send a POST request to our /login endpoint
        const response = await fetch(`${BACKEND_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "An unknown login error occurred.");
        }

        // --- IMPORTANT: Handle successful login ---
        // Save the received access token to the browser's local storage
        localStorage.setItem('accessToken', data.access_token);
        
        showMessage("Login successful! Redirecting...", "success");

        // Redirect to the main app page after a short delay
        setTimeout(() => {
            window.location.href = 'index.html'; // Redirect to the main analyzer page
        }, 1500); // 1.5 second delay

    } catch (error) {
        showMessage(error.message, "error");
        loginButton.disabled = false;
        loginButton.textContent = "Login";
    }
}

// Helper function to display messages
function showMessage(message, type) {
    messageText.textContent = message;
    messageDiv.style.backgroundColor = type === 'success' ? '#1c4b2c' : '#5d1a21';
    messageDiv.style.color = type === 'success' ? '#d4edda' : '#f8d7da';
    messageDiv.classList.remove("hidden");
}

// Add event listener to the button
loginButton.addEventListener("click", handleLogin);