// static/watchlist.js

// --- Get references to all needed elements ---
const watchlistContainer = document.getElementById('watchlist-container');
const loadingMessage = document.getElementById('loading-message');
const coinIdInput = document.getElementById('coinIdInput');
const addButton = document.getElementById('addButton');
const addMessageDiv = document.getElementById('add-message');

// --- Main function to run when the page loads ---
document.addEventListener('DOMContentLoaded', () => {
    fetchWatchlist(); // Fetch the watchlist as soon as the page loads
});

// --- Add event listener for the new "Add Coin" button ---
addButton.addEventListener('click', handleAddCoin);

async function handleAddCoin() {
    const coinId = coinIdInput.value.trim().toLowerCase();
    if (!coinId) {
        alert("Please enter a coin ID.");
        return;
    }

    addButton.disabled = true;
    addButton.textContent = 'Adding...';

    try {
        const response = await fetch('/api/watchlist/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coin_id: coinId })
        });
        const data = await response.json();
        
        if (!response.ok) {
            // Handle cases where user might not be logged in
            if (response.status === 401) {
                alert("You are not logged in. Redirecting to login page.");
                window.location.href = '/login';
                return;
            }
            throw new Error(data.error || 'Failed to add coin.');
        }
        
        // Show success message and refresh the watchlist
        alert(data.message);
        coinIdInput.value = ''; // Clear the input box
        fetchWatchlist(); // Reload the watchlist to show the new coin

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        addButton.disabled = false;
        addButton.textContent = 'Add Coin';
    }
}

async function fetchWatchlist() {
    // Clear the current list and show loading message
    watchlistContainer.innerHTML = '<p id="loading-message">Loading your watchlist...</p>';
    
    try {
        const response = await fetch('/api/watchlist');
        if (response.status === 401) { // Not logged in
            watchlistContainer.innerHTML = '<p>Please <a href="/login">login</a> to see your watchlist.</p>';
            return;
        }
        const watchlistItems = await response.json();

        // Clear the "Loading..." message
        watchlistContainer.innerHTML = '';

        if (watchlistItems.length === 0) {
            watchlistContainer.innerHTML = '<p>Your watchlist is empty.</p>';
            return;
        }

        // For each item in the watchlist, fetch its current data
        for (const item of watchlistItems) {
            fetchCoinData(item.coin_id);
        }

    } catch (error) {
        watchlistContainer.innerHTML = '<p>Failed to load watchlist.</p>';
    }
}

async function fetchCoinData(coinId) {
    try {
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        createWatchlistItemElement(data, coinId);
    } catch (error) {
        console.error(`Error fetching data for ${coinId}:`, error);
    }
}

function createWatchlistItemElement(coinData, coinId) {
    const itemDiv = document.createElement('div');
    itemDiv.style.cssText = `display: flex; justify-content: space-between; align-items: center; background-color: #2a2a2a; padding: 15px; border-radius: 8px; margin-bottom: 10px;`;
    const nameSpan = document.createElement('span');
    nameSpan.textContent = `${coinData.name} (${coinId.toUpperCase()})`;
    nameSpan.style.fontWeight = 'bold';
    const priceSpan = document.createElement('span');
    const price = parseFloat(coinData.current_price);
    priceSpan.textContent = `$${price.toLocaleString('en-US')}`;
    itemDiv.appendChild(nameSpan);
    itemDiv.appendChild(priceSpan);
    watchlistContainer.appendChild(itemDiv);
}