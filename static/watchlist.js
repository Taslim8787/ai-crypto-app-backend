// static/watchlist.js

// Function to run when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // First, check if the user is logged in by looking for the access token
    const token = localStorage.getItem('accessToken');
    if (!token) {
        // If no token, redirect to the login page
        window.location.href = '/login';
        return;
    }
    
    // If logged in, fetch the watchlist
    fetchWatchlist(token);
});

const watchlistContainer = document.getElementById('watchlist-container');
const loadingMessage = document.getElementById('loading-message');

async function fetchWatchlist(token) {
    try {
        // Fetch the user's saved watchlist from our backend
        const response = await fetch('/api/watchlist', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}` // Send the token for authentication
            }
        });

        if (response.status === 401) { // Unauthorized
            // Token might be expired or invalid, redirect to login
            window.location.href = '/login';
            return;
        }

        const watchlistItems = await response.json();

        // Clear the "Loading..." message
        loadingMessage.style.display = 'none';

        if (watchlistItems.length === 0) {
            watchlistContainer.innerHTML = '<p>Your watchlist is empty. Add coins from the main page!</p>';
            return;
        }

        // For each item in the watchlist, fetch its current data
        for (const item of watchlistItems) {
            fetchCoinData(item.coin_id);
        }

    } catch (error) {
        console.error('Error fetching watchlist:', error);
        loadingMessage.textContent = 'Failed to load watchlist.';
    }
}

async function fetchCoinData(coinId) {
    try {
        // Use our own /api/analyze endpoint to get coin data
        // This is efficient because our backend handles the CoinGecko API key
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch coin data');
        }

        // Create and append the new HTML element for this coin
        createWatchlistItemElement(data);

    } catch (error) {
        console.error(`Error fetching data for ${coinId}:`, error);
        // Optionally, display an error for this specific coin
    }
}

function createWatchlistItemElement(coinData) {
    // Create the main div for the item
    const itemDiv = document.createElement('div');
    itemDiv.className = 'watchlist-item'; // We'll add styling for this later
    itemDiv.style.cssText = `
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        background-color: #2a2a2a; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px;
    `;

    // Create the span for the coin name
    const nameSpan = document.createElement('span');
    nameSpan.className = 'coin-name';
    nameSpan.textContent = `${coinData.name} (${coinData.coin_symbol || coinId.toUpperCase()})`;
    nameSpan.style.fontWeight = 'bold';

    // Create the span for the coin price
    const priceSpan = document.createElement('span');
    priceSpan.className = 'coin-price';
    const price = parseFloat(coinData.current_price);
    priceSpan.textContent = `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}`;

    // Add the name and price to the item div
    itemDiv.appendChild(nameSpan);
    itemDiv.appendChild(priceSpan);

    // Add the full item to the container on the page
    watchlistContainer.appendChild(itemDiv);
}