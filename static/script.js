// static/script.js
const coinInput = document.getElementById("coinInput");
const analyzeButton = document.getElementById("analyzeButton");
const loadingIndicator = document.getElementById("loading");
const resultSection = document.getElementById("result");
const errorSection = document.getElementById("error");
const errorMessage = document.getElementById("errorMessage");
const coinNameDisplay = document.getElementById("coinName");
const currentPriceDisplay = document.getElementById("currentPrice");
const aiAnalysisContent = document.getElementById("aiAnalysisContent");

async function handleAnalysis() {
    const coinId = coinInput.value.trim().toLowerCase();
    if (!coinId) { showError("Please enter a coin ID."); return; }

    loadingIndicator.classList.remove("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    analyzeButton.disabled = true;

    try {
        const response = await fetch(`/api/analyze/${coinId}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        displayResults(data);
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

analyzeButton.addEventListener("click", handleAnalysis);