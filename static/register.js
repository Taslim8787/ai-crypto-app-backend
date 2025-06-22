// register.js

// IMPORTANT: This must be the same URL from your main script.js
const BACKEND_URL = "";

// Get references to HTML elements
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const registerButton = document.getElementById("registerButton");
const messageDiv = document.getElementById("message");
const messageText = document.getElementById("messageText");

async function handleRegister() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        showMessage("Username and password cannot be empty.", "error");
        return;
    }

    // Disable button to prevent multiple clicks
    registerButton.disabled = true;
    registerButton.textContent = "Registering...";

    try {
        // Send a POST request to our /register endpoint
        const response = await fetch(`${BACKEND_URL}/api/register`, {
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
            // If response is not 2xx, throw an error with the message from the server
            throw new Error(data.error || "An unknown registration error occurred.");
        }

        // If registration is successful
        showMessage(data.message, "success");

    } catch (error) {
        // If any error happened, display it
        showMessage(error.message, "error");
    } finally {
        // Re-enable the button
        registerButton.disabled = false;
        registerButton.textContent = "Register";
    }
}

// Helper function to display messages
function showMessage(message, type) {
    messageText.textContent = message;
    // Change color based on message type (success or error)
    messageDiv.style.backgroundColor = type === 'success' ? '#1c4b2c' : '#5d1a21';
    messageDiv.style.color = type === 'success' ? '#d4edda' : '#f8d7da';
    messageDiv.classList.remove("hidden");
}

// Add event listener to the button
registerButton.addEventListener("click", handleRegister);