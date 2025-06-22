// static/script.js - Final Analyzer Fix

const coinInput = document.getElementById('coinInput');
const analyzeButton = document.getElementById('analyzeButton');
const resultContainer = document.getElementById('result-container');

analyzeButton.addEventListener('click', async () => {
    const coinId = coinInput.value.trim().toLowerCase();
    if (!coinId) {
        resultContainer.innerHTML = `<p style="color:red;">Please enter a coin ID.</p>`;
        resultContainer.classList.remove('hidden');
        return;
    }

    resultContainer.classList.remove('hidden');
    resultContainer.innerHTML = `<p>Analyzing...</p>`;
    analyzeButton.disabled = true;

    try {
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Failed to fetch data.");
        
        // --- THIS IS THE CORRECTED LOGIC ---
        let html = `
            <div class="result-section">
                <h2>Analysis for ${data.name}</h2>
                <p><strong>Price:</strong> $${parseFloat(data.current_price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</p>
                <h3>AI Analysis:</h3>
                <div class="ai-analysis">${data.ai_analysis}</div>
            </div>
        `;
        // --- END CORRECTION ---

        resultContainer.innerHTML = html;

    } catch (error) {
        resultContainer.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    } finally {
        analyzeButton.disabled = false;
    }
});