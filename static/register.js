// static/register.js
const usernameInput = document.getElementById('usernameInput');
const passwordInput = document.getElementById('passwordInput');
const registerButton = document.getElementById('registerButton');
const messageDiv = document.getElementById('message');

registerButton.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (!username || !password) return;
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        messageDiv.innerHTML = `<p>${data.message || data.error}</p>`;
        messageDiv.classList.remove('hidden');
        if(response.ok) {
             setTimeout(() => { window.location.href = '/login'; }, 2000);
        }
    } catch (error) {
        messageDiv.innerHTML = `<p>An error occurred.</p>`;
        messageDiv.classList.remove('hidden');
    }
});