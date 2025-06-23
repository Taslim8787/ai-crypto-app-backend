// static/auth.js - Updated with Trade History Link

document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.getElementById('nav-links');
    const token = localStorage.getItem('accessToken'); // We are using JWT tokens now

    if (token) {
        // This is the updated navigation bar for a logged-in user
        navLinks.innerHTML = `
            <p style="text-align: center; margin-bottom: 20px;">
                <a href="/">Analyzer</a> | 
                <a href="/watchlist">Watchlist</a> | 
                <a href="/portfolio">Portfolio</a> | 
                <a href="/trades">Trade History</a> | 
                <a href="#" id="logoutButton" style="color: #ff6b6b;">Logout</a>
            </p>`;
        
        // Find the new logout button and add its click event
        document.getElementById('logoutButton').addEventListener('click', handleLogout);

    } else {
        // This is the navigation for a logged-out user
        navLinks.innerHTML = `<p><a href="/login">Login</a> | <a href="/register">Register</a></p>`;
    }
});

async function handleLogout() {
    // We removed the backend logout route for simplicity, so we just handle it on the frontend
    localStorage.removeItem('accessToken');
    alert("You have been logged out.");
    window.location.href = '/login';
}