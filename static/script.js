// static/script.js
const coinInput = document.getElementById('coinInput');
const analyzeButton = document.getElementById('analyzeButton');
const resultContainer = document.getElementById('result-container');

analyzeButton.addEventListener('click', async () => {
    const coinId = coinInput.value.trim().toLowerCase();
    if (!coinId) return;
    resultContainer.innerHTML = `<p>Analyzing...</p>`;
    try {
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        let html = `
            <h2>Analysis for ${data.name}</h2>
            <p><strong>Price:</strong> $${parseFloat(data.current_price).toLocaleString()}</p>
            <h3>AI Analysis:</h3>
            <div>${data.ai_analysis}</div>
        `;
        resultContainer.innerHTML = html;
    } catch (error) {
        resultContainer.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
});