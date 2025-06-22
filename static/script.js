// script.js

// Your live Render backend URL is now correctly set.
const BACKEND_URL = "";

// Get references to all the HTML elements we need to work with
const coinInput = document.getElementById("coinInput");
const analyzeButton = document.getElementById("analyzeButton");
const loadingIndicator = document.getElementById("loading");
const resultSection = document.getElementById("result");
const errorSection = document.getElementById("error");
const errorMessage = document.getElementById("errorMessage");

const coinSymbolDisplay = document.getElementById("coinSymbolDisplay");
const coinNameDisplay = document.getElementById("coinName");
const currentPriceDisplay = document.getElementById("currentPrice");
const marketCapDisplay = document.getElementById("marketCap");
const volume24hDisplay = document.getElementById("volume24h");
const aiAnalysisContent = document.getElementById("aiAnalysisContent");

// This function will be called when the button is clicked
async function handleAnalysis() {
    const coinSymbol = coinInput.value.trim().toLowerCase();
    if (!coinSymbol) {
        showError("Please enter a full coin ID (e.g., bitcoin).");
        return;
    }

    // --- Show loading state and hide previous results/errors ---
    loadingIndicator.classList.remove("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    analyzeButton.disabled = true; // Disable button during analysis
    analyzeButton.textContent = "Analyzing...";

    try {
        // --- Fetch data from our backend API ---
        // We construct the full URL, e.g., https://.../analyze/bitcoin
        const response = await fetch(`${BACKEND_URL}/api/analyze/${coinSymbol}`);
        const data = await response.json();

        // If the response from the server is not "ok" (e.g., a 404 or 500 error)
        if (!response.ok) {
            // Throw an error with the message from our backend's JSON response
            throw new Error(data.error || "An unknown server error occurred.");
        }

        // --- If the fetch was successful, display the data ---
        displayResults(data);

    } catch (error) {
        // --- If any error happened in the try block, display the error ---
        console.error("Fetch error:", error);
        // Provide a more user-friendly error message for network issues
        if (error instanceof TypeError) { // This often indicates a network or CORS error
             showError("Failed to connect to the server. Please check your internet connection.");
        } else {
             showError(error.message);
        }
    } finally {
        // --- This code runs no matter what (success or error) ---
        loadingIndicator.classList.add("hidden"); // Hide loading indicator
        analyzeButton.disabled = false; // Re-enable the button
        analyzeButton.textContent = "Analyze";
    }
}

// A helper function to display the results on the page
function displayResults(data) {
    coinSymbolDisplay.textContent = data.coin_symbol;
    coinNameDisplay.textContent = data.name;
    // Format numbers to look like currency (e.g., 1,234,567.89)
    currentPriceDisplay.textContent = parseFloat(data.current_price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 });
    marketCapDisplay.textContent = parseFloat(data.market_cap).toLocaleString('en-US');
    volume24hDisplay.textContent = parseFloat(data.volume_24h).toLocaleString('en-US');
    aiAnalysisContent.textContent = data.ai_analysis;

    // Hide any old errors and show the result section
    errorSection.classList.add("hidden");
    resultSection.classList.remove("hidden");
}

// A helper function to show an error message on the page
function showError(message) {
    errorMessage.textContent = message;
    // Hide any old results and show the error section
    resultSection.classList.add("hidden");
    errorSection.classList.remove("hidden");
}

// --- Event Listeners ---
// This makes the "Analyze" button clickable
analyzeButton.addEventListener("click", handleAnalysis);

// This allows pressing the "Enter" key in the input field to trigger the analysis
coinInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        handleAnalysis();
    }
});