// static/auth.js - Handles login status and navigation links
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.getElementById('nav-links');
    const token = localStorage.getItem('accessToken'); // We are still using JWT tokens from the simple session

    if (token) {
        navLinks.innerHTML = `
            <p>
                <a href="/">Analyzer</a> | 
                <a href="/watchlist">Watchlist</a> | 
                <a href="/portfolio">Portfolio</a> | 
                <a href="#" id="logoutButton">Logout</a>
            </p>`;
        document.getElementById('logoutButton').addEventListener('click', handleLogout);
    } else {
        navLinks.innerHTML = `<p><a href="/login">Login</a> | <a href="/register">Register</a></p>`;
    }
});

async function handleLogout() {
    // We now use a session on the backend, but we still need to clear the local token
    localStorage.removeItem('accessToken');
    await fetch('/api/logout', { method: 'POST' }); // Tell backend to clear session
    window.location.href = '/login';
}