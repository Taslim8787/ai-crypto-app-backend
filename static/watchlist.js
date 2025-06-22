// static/watchlist.js
const coinIdInput = document.getElementById('coinIdInput');
const addButton = document.getElementById('addButton');
const watchlistContainer = document.getElementById('watchlist-container');
const messageDiv = document.getElementById('message');

async function fetchWatchlist() {
    const token = localStorage.getItem('accessToken');
    if (!token) { window.location.href = '/login'; return; }
    
    watchlistContainer.innerHTML = '<p>Loading watchlist...</p>';
    try {
        const response = await fetch('/api/watchlist', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) { window.location.href = '/login'; return; }
        const items = await response.json();
        
        if (items.length === 0) {
            watchlistContainer.innerHTML = '<p>Your watchlist is empty.</p>';
            return;
        }
        
        // Fetch prices for all coins at once
        const coinIds = items.map(item => item.coin_id);
        const priceResponse = await fetch('/api/get-prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: coinIds })
        });
        const prices = await priceResponse.json();

        watchlistContainer.innerHTML = ''; // Clear loading message
        items.forEach(item => {
            const price = prices[item.coin_id] ? prices[item.coin_id].usd : 'N/A';
            const itemDiv = document.createElement('div');
            itemDiv.innerHTML = `<span>${item.coin_id}</span> <span>$${price.toLocaleString()}</span>`;
            watchlistContainer.appendChild(itemDiv);
        });
    } catch (error) {
        watchlistContainer.innerHTML = '<p>Error loading watchlist.</p>';
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
        if (response.ok) fetchWatchlist(); // Refresh list on success
    } catch (error) {
        messageDiv.innerHTML = `<p>An error occurred.</p>`;
        messageDiv.classList.remove('hidden');
    }
});

fetchWatchlist();