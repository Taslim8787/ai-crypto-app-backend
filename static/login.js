// static/login.js
const usernameInput = document.getElementById('usernameInput');
const passwordInput = document.getElementById('passwordInput');
const loginButton = document.getElementById('loginButton');
const messageDiv = document.getElementById('message');

loginButton.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (!username || !password) return;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        // This time, we use the JWT token from the response
        localStorage.setItem('accessToken', data.access_token);
        messageDiv.innerHTML = `<p>Login successful! Redirecting...</p>`;
        messageDiv.classList.remove('hidden');
        setTimeout(() => { window.location.href = '/'; }, 1500);
    } catch (error) {
        messageDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        messageDiv.classList.remove('hidden');
    }
});