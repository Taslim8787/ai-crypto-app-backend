// static/script.js

const coinInput = document.getElementById("coinInput");
const analyzeButton = document.getElementById("analyzeButton");
const loadingIndicator = document.getElementById("loading");
const resultSection = document.getElementById("result");
const errorSection = document.getElementById("error");
const errorMessage = document.getElementById("errorMessage");
const coinNameDisplay = document.getElementById("coinNameDisplay");
const currentPriceDisplay = document.getElementById("currentPriceDisplay");
const aiAnalysisContent = document.getElementById("aiAnalysisContent");

// --- NEW elements for watchlist and auth ---
const addToWatchlistButton = document.getElementById("addToWatchlistButton");
const addMessage = document.getElementById("add-message");
const logoutButton = document.getElementById("logoutButton");
const navLinks = document.getElementById("nav-links");

let currentCoinId = null; // To store the ID of the analyzed coin

// --- Check login status when page loads ---
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        // If user is logged in, show the logout button
        logoutButton.classList.remove('hidden');
    }
});

async function handleAnalysis() {
    const coinId = coinInput.value.trim().toLowerCase();
    if (!coinId) { showError("Please enter a coin ID."); return; }

    loadingIndicator.classList.remove("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    addToWatchlistButton.classList.add('hidden'); // Hide button on new analysis
    addMessage.classList.add('hidden'); // Hide message on new analysis
    analyzeButton.disabled = true;

    try {
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to fetch data.');
        
        currentCoinId = coinId; // Save the coin ID for the add to watchlist function
        displayResults(data);
        
        // If user is logged in, show the "Add to Watchlist" button
        if (localStorage.getItem('accessToken')) {
            addToWatchlistButton.classList.remove('hidden');
        }

    } catch (error) {
        showError(error.message);
    } finally {
        loadingIndicator.classList.add("hidden");
        analyzeButton.disabled = false;
    }
}

function displayResults(data) {
    coinNameDisplay.textContent = data.name;
    currentPriceDisplay.textContent = parseFloat(data.current_price).toLocaleString('en-US');
    aiAnalysisContent.textContent = data.ai_analysis;
    resultSection.classList.remove("hidden");
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove("hidden");
}

// --- NEW function to add a coin to the watchlist ---
async function addToWatchlist() {
    const token = localStorage.getItem('accessToken');
    if (!token || !currentCoinId) return; // Exit if no token or no coin analyzed

    addToWatchlistButton.disabled = true;
    addMessage.classList.remove('hidden');
    addMessage.textContent = 'Adding...';

    try {
        const response = await fetch('/api/watchlist/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Send the token for authentication
            },
            body: JSON.stringify({ coin_id: currentCoinId })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to add coin.');
        
        addMessage.textContent = data.message; // Show success message from backend

    } catch (error) {
        addMessage.textContent = error.message;
    } finally {
        addToWatchlistButton.disabled = false;
    }
}

// --- NEW function for logout ---
function handleLogout() {
    localStorage.removeItem('accessToken'); // Remove the token
    logoutButton.classList.add('hidden'); // Hide the logout button
    // Optional: reload the page or show a message
    window.location.reload(); 
}

// --- Event Listeners ---
analyzeButton.addEventListener("click", handleAnalysis);
addToWatchlistButton.addEventListener("click", addToWatchlist);
logoutButton.addEventListener("click", handleLogout);