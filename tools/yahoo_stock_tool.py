from langchain_core.tools import tool
import yfinance as yf
import re

@tool
def yahoo_stock_info(ticker: str) -> str:
    """Get the current stock price for a given stock ticker like 'SAGILITY.NS'."""
    try:
        # Validate and normalize ticker
        ticker = ticker.strip().upper()
        # Append .NS for NSE stocks if not present
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            ticker = f"{ticker}.NS"  # Default to NSE
        # Check if ticker is valid (basic regex for NSE/BSE tickers)
        if not re.match(r'^[A-Z0-9]+(\.NS|\.BO)?$', ticker):
            return f"Invalid ticker format: {ticker}. Please use a valid NSE/BSE ticker (e.g., SAGILITY.NS or 544282.BO)."
        
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        currency = info.get("currency", "INR")  # Default to INR for Indian tickers

        if price:
            if ticker.endswith('.NS') or ticker.endswith('.BO'):
                # Indian tickers are in INR
                return f"The current price of {ticker} is ₹{price:.2f}"
            else:
                # Non-Indian tickers use native currency with INR conversion
                inr_price = price * 83.5
                return f"The current price of {ticker} is {currency} {price:.2f} (approximately ₹{inr_price:.2f})"
        else:
            return f"Could not retrieve price for {ticker}. The ticker may not be listed or data is unavailable."
    except Exception as e:
        if "404" in str(e):
            return f"Error: Ticker {ticker} not found on Yahoo Finance. Please verify the ticker symbol."
        return f"Error fetching stock info for {ticker}: {str(e)}. Please try again or check Yahoo Finance."