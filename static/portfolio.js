// static/portfolio.js
// This file will be very similar to watchlist.js for now
// We will add the P/L logic later
const portfolioContainer = document.getElementById('portfolio-container');

async function fetchPortfolio() {
    const token = localStorage.getItem('accessToken');
    if (!token) { window.location.href = '/login'; return; }
    
    portfolioContainer.innerHTML = '<p>Loading portfolio...</p>';
    try {
        const response = await fetch('/api/portfolio', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) { window.location.href = '/login'; return; }
        const items = await response.json();
        
        if (items.length === 0) {
            portfolioContainer.innerHTML = '<p>Your portfolio is empty.</p>';
            return;
        }
        portfolioContainer.innerHTML = ''; // Clear loading
        items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.innerHTML = `<span>${item.coin_id}</span> <span>Amount: ${item.amount}</span>`;
            portfolioContainer.appendChild(itemDiv);
        });

    } catch (error) {
        portfolioContainer.innerHTML = '<p>Error loading portfolio.</p>';
    }
}

// Add logic for the 'add' button
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
     if (response.ok) fetchPortfolio(); // Refresh list
});


fetchPortfolio();