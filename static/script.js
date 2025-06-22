// static/script.js
const coinInput = document.getElementById("coinInput");
const analyzeButton = document.getElementById("analyzeButton");
const logoutButton = document.getElementById("logoutButton");
const addToWatchlistButton = document.getElementById("addToWatchlistButton");
let currentCoinId = null;

async function handleAnalysis() {
    // ... (this function is mostly the same)
    const coinId = coinInput.value.trim().toLowerCase();
    if (!coinId) return;
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");
    analyzeButton.disabled = true;
    try {
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        currentCoinId = coinId;
        document.getElementById("coinNameDisplay").textContent = data.name;
        document.getElementById("currentPriceDisplay").textContent = parseFloat(data.current_price).toLocaleString('en-US');
        document.getElementById("aiAnalysisContent").textContent = data.ai_analysis;
        document.getElementById("result").classList.remove("hidden");
        // We can remove the logic to show/hide the button here, it will be handled by CSS or other logic later
    } catch (error) {
        // ...
    } finally {
        document.getElementById("loading").classList.add("hidden");
        analyzeButton.disabled = false;
    }
}

async function addToWatchlist() {
    if (!currentCoinId) return;
    try {
        const response = await fetch('/api/watchlist/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coin_id: currentCoinId })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        alert(data.message); // Simple alert for success
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function handleLogout() {
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/login';
}

analyzeButton.addEventListener("click", handleAnalysis);
addToWatchlistButton.addEventListener("click", addToWatchlist);
logoutButton.addEventListener("click", handleLogout);