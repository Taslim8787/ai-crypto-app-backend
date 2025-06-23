// static/trades.js

document.addEventListener('DOMContentLoaded', fetchTrades);

// --- Get references to all needed elements ---
const coinIdInput = document.getElementById('coinIdInput');
const entryPriceInput = document.getElementById('entryPriceInput');
const exitPriceInput = document.getElementById('exitPriceInput');
const tradeTypeSelect = document.getElementById('tradeTypeSelect');
const logTradeButton = document.getElementById('logTradeButton');
const messageDiv = document.getElementById('message');
const winRatioContainer = document.getElementById('win-ratio-summary');
const tradeHistoryContainer = document.getElementById('trade-history-container');

// --- Add event listener for the "Log Trade" button ---
logTradeButton.addEventListener('click', handleLogTrade);

async function handleLogTrade() {
    const tradeData = {
        coin_id: coinIdInput.value.trim().toLowerCase(),
        entry_price: entryPriceInput.value,
        exit_price: exitPriceInput.value,
        trade_type: tradeTypeSelect.value
    };

    if (!tradeData.coin_id || !tradeData.entry_price || !tradeData.exit_price) {
        alert("Please fill in all fields.");
        return;
    }

    logTradeButton.disabled = true;

    try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch('/api/trades/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(tradeData)
        });
        const result = await response.json();
        
        if (!response.ok) throw new Error(result.error || 'Failed to log trade.');

        alert(result.message);
        // Clear inputs and refresh the list
        coinIdInput.value = '';
        entryPriceInput.value = '';
        exitPriceInput.value = '';
        fetchTrades();

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        logTradeButton.disabled = false;
    }
}

async function fetchTrades() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    winRatioContainer.innerHTML = '<p>Loading stats...</p>';
    tradeHistoryContainer.innerHTML = '<h3>Trade History</h3><p>Loading history...</p>';

    try {
        const response = await fetch('/api/trades', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            if (response.status === 401) { window.location.href = '/login'; }
            return;
        }
        
        const trades = await response.json();
        displayTrades(trades);
        calculateWinRatio(trades);

    } catch (error) {
        tradeHistoryContainer.innerHTML = '<p>Failed to load trade history.</p>';
    }
}

function calculateWinRatio(trades) {
    if (trades.length === 0) {
        winRatioContainer.innerHTML = '<h3>Performance</h3><p>No trades logged yet.</p>';
        return;
    }

    const totalTrades = trades.length;
    const wins = trades.filter(trade => trade.outcome === 'win').length;
    const winRate = ((wins / totalTrades) * 100).toFixed(2);

    winRatioContainer.innerHTML = `
        <h3>Performance</h3>
        <p>Total Trades: ${totalTrades}</p>
        <p>Wins: ${wins}</p>
        <p>Losses: ${totalTrades - wins}</p>
        <p>Win Rate: ${winRate}%</p>
    `;
}

function displayTrades(trades) {
    tradeHistoryContainer.innerHTML = '<h3>Trade History</h3>';
    if (trades.length === 0) {
        tradeHistoryContainer.innerHTML += '<p>No trades logged yet.</p>';
        return;
    }

    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Coin</th>
                <th>Type</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>Outcome</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;
    const tbody = table.querySelector('tbody');
    trades.forEach(trade => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${trade.coin_id}</td>
            <td>${trade.trade_type}</td>
            <td>$${trade.entry_price}</td>
            <td>$${trade.exit_price}</td>
            <td style="color: ${trade.outcome === 'win' ? 'lightgreen' : 'salmon'};">${trade.outcome}</td>
        `;
    });
    tradeHistoryContainer.appendChild(table);
    // Add some basic styling for the table
    tradeHistoryContainer.querySelector('table').style.width = '100%';
    tradeHistoryContainer.querySelector('table').style.textAlign = 'left';
}