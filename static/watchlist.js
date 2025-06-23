// static/watchlist.js - Final Version

document.addEventListener('DOMContentLoaded', fetchWatchlist);

const watchlistContainer = document.getElementById('watchlist-container');
const coinIdInput = document.getElementById('coinIdInput');
const addButton = document.getElementById('addButton');
const messageDiv = document.getElementById('message');

async function fetchWatchlist() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        watchlistContainer.innerHTML = '<p>Please <a href="/login">login</a> to view your watchlist.</p>';
        return;
    }

    watchlistContainer.innerHTML = '<p>Loading watchlist...</p>';
    try {
        const response = await fetch('/api/watchlist', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            if (response.status === 401) { // Unauthorized
                window.location.href = '/login'; // Redirect if token is bad
            }
            throw new Error('Failed to load watchlist.');
        }
        
        const items = await response.json();
        
        if (items.length === 0) {
            watchlistContainer.innerHTML = '<p>Your watchlist is empty.</p>';
            return;
        }

        // Fetch prices for all coins
        const coinIds = items.map(item => item.coin_id);
        const priceResponse = await fetch('/api/get-prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ ids: coinIds })
        });
        const prices = await priceResponse.json();

        watchlistContainer.innerHTML = ''; // Clear loading message
        items.forEach(item => {
            const price = prices[item.coin_id] ? prices[item.coin_id].usd : 'N/A';
            const itemDiv = document.createElement('div');
            itemDiv.className = 'list-item'; // Use a generic class for styling
            itemDiv.innerHTML = `<span>${item.coin_id}</span> <span>$${price.toLocaleString()}</span>`;
            watchlistContainer.appendChild(itemDiv);
        });
    } catch (error) {
        watchlistContainer.innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
}

addButton.addEventListener('click', async () => {
    const coinId = coinIdInput.value.trim().toLowerCase();
    if (!coinId) return;
    const token = localStorage.getItem('accessToken');
    
    try {
        const response = await fetch('/api/watchlist/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ coin_id: coinId })
        });
        const data = await response.json();
        messageDiv.innerHTML = `<p>${data.message || data.error}</p>`;
        messageDiv.classList.remove('hidden');
        if (response.ok) {
            coinIdInput.value = '';
            fetchWatchlist(); // Refresh list on success
        }
    } catch (error) {
        messageDiv.innerHTML = `<p>An error occurred.</p>`;
        messageDiv.classList.remove('hidden');
    }
});