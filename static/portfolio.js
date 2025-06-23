// static/portfolio.js - Final Version

document.addEventListener('DOMContentLoaded', fetchPortfolio);

const portfolioContainer = document.getElementById('portfolio-container');
const summaryContainer = document.getElementById('portfolio-summary');

async function fetchPortfolio() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    portfolioContainer.innerHTML = '<p>Loading portfolio...</p>';
    summaryContainer.innerHTML = '';

    try {
        const response = await fetch('/api/portfolio', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            if (response.status === 401) { window.location.href = '/login'; }
            throw new Error('Failed to load portfolio.');
        }
        
        const items = await response.json();

        if (items.length === 0) {
            portfolioContainer.innerHTML = '<p>Your portfolio is empty.</p>';
            return;
        }

        const coinIds = items.map(item => item.coin_id);
        const priceResponse = await fetch('/api/get-prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ ids: coinIds })
        });
        const prices = await priceResponse.json();

        portfolioContainer.innerHTML = '';
        let totalValue = 0;
        let totalCost = 0;

        items.forEach(item => {
            const currentPrice = prices[item.coin_id] ? prices[item.coin_id].usd : 0;
            const currentValue = item.amount * currentPrice;
            const cost = item.amount * item.buy_price;
            const pnl = currentValue - cost;

            totalValue += currentValue;
            totalCost += cost;

            const itemDiv = document.createElement('div');
            itemDiv.className = 'list-item';
            itemDiv.innerHTML = `
                <div><strong>${item.coin_id}</strong></div>
                <div>Amount: ${item.amount}</div>
                <div>Value: $${currentValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                <div style="color: ${pnl >= 0 ? 'lightgreen' : 'salmon'};">P/L: $${pnl.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
            `;
            portfolioContainer.appendChild(itemDiv);
        });

        const totalPnl = totalValue - totalCost;
        summaryContainer.innerHTML = `
            <h3>Summary</h3>
            <p>Total Value: $${totalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
            <p style="color: ${totalPnl >= 0 ? 'lightgreen' : 'salmon'};">Total P/L: $${totalPnl.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
        `;

    } catch (error) {
        portfolioContainer.innerHTML = `<p style="color:red;">${error.message}</p>`;
    }
}

document.getElementById('addButton').addEventListener('click', async () => {
     const token = localStorage.getItem('accessToken');
     const coinId = document.getElementById('coinIdInput').value;
     const amount = document.getElementById('amountInput').value;
     const buyPrice = document.getElementById('priceInput').value;

     const response = await fetch('/api/portfolio/add', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
         body: JSON.stringify({ coin_id: coinId, amount: amount, buy_price: buyPrice })
     });
     const data = await response.json();
     alert(data.message || data.error);
     if (response.ok) fetchPortfolio();
});