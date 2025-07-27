import streamlit as st
from langchain_core.messages import HumanMessage
from graph.graph_builder import build_graph
from llm_config import get_llm
from prompts.system_prompt import get_system_prompt
from tools.tavily_tool import is_tavily_used

# Set page config as the first Streamlit command
st.set_page_config(page_title="Stock Assistant", layout="wide")

# Initialize session state for search history
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Custom CSS for styling
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #1E90FF;
        margin-bottom: 20px;
    }
    .instructions {
        text-align: center;
        font-size: 1.2em;
        color: #333;
        margin-bottom: 10px;
    }
    .centered {
        text-align: center;
        margin-bottom: 20px;
    }
    .output-section {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Centered title with stock market emoji
st.markdown('<div class="title">📈 Stock Market Assistant</div>', unsafe_allow_html=True)

# Centered instructional text
st.markdown(
    '<div class="instructions">Enter a stock ticker to get the latest news, current price, and investment recommendations (e.g., SAGILITY.NS for Sagility India Ltd.).</div>',
    unsafe_allow_html=True
)

# Centered input field
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    ticker = st.text_input(
        "Enter Stock Ticker (e.g., SAGILITY.NS or 544282.BO):",
        value="SAGILITY.NS",
        placeholder="Type ticker here...",
        label_visibility="collapsed"
    )

# Centered button
with col2:
    if st.button("Get Stock Info", use_container_width=True):
        if ticker:
            # Add ticker to search history
            if ticker not in st.session_state.search_history:
                st.session_state.search_history.append(ticker)
                if len(st.session_state.search_history) > 5:  # Limit to 5 recent searches
                    st.session_state.search_history.pop(0)

            # Initialize LLM and graph
            llm = get_llm()
            graph = build_graph(llm)

            # Construct query
            query = f"What is {ticker} news and what is the current situation going on and tell me what is the stock price now and should I buy it or not?"
            messages = [HumanMessage(content=query)]
            print(f"Query constructed: {query}")  # Debug

            # Show loading spinner
            with st.spinner("Fetching stock data and news..."):
                try:
                    result = graph.invoke({"messages": messages})
                    print(f"Graph invoke result: {result}")  # Debug
                    response = result["messages"][-1].content
                    print(f"Raw response: {response}")  # Debug

                    # Create two columns for layout
                    col1, col2 = st.columns([1, 3])

                    # Sidebar for search history
                    with col1:
                        st.markdown("### Recent Searches")
                        if st.session_state.search_history:
                            for past_ticker in reversed(st.session_state.search_history):
                                if st.button(past_ticker, key=past_ticker):
                                    st.session_state.ticker = past_ticker
                                    st.rerun()
                        st.markdown("### Search Status")
                        if is_tavily_used():
                            st.info("Using Tavily for search.")
                        else:
                            st.warning("Search API not configured correctly.")

                    # Output display
                    with col2:
                        st.markdown("### Stock Analysis")
                        if not response or "Error" in response or "not found" in response or "Failed to perform search" in response:
                            st.markdown(
                                f'<div class="error-box"><b>Error:</b> {response or "No data retrieved"}</div>',
                                unsafe_allow_html=True
                            )
                            st.write(
                                "Please verify the ticker symbol (e.g., SAGILITY.NS for NSE or 544282.BO for BSE) or check your Tavily API key. For news, try checking Yahoo Finance, NSE India, or Economic Times."
                            )
                        else:
                            # Display raw response as fallback
                            st.write("Raw Response:", response)
                            # Attempt to parse sections
                            sections = response.split("\n\n")
                            if not sections or all(not s.strip() for s in sections):
                                st.write("No detailed data available. Raw response above.")
                            else:
                                for section in sections:
                                    if section.startswith("**Company Profile**"):
                                        with st.expander("Company Profile", expanded=True):
                                            st.write(section.replace("**Company Profile**: ", "") or "No company profile data.")
                                    elif section.startswith("**Recent News**"):
                                        with st.expander("Recent News", expanded=True):
                                            st.write(section.replace("**Recent News**: ", "") or "No news data available.")
                                    elif section.startswith("**Current Stock Price**"):
                                        with st.expander("Current Stock Price", expanded=True):
                                            st.write(section.replace("**Current Stock Price**: ", "") or "No price data available.")
                                    elif section.startswith("**Current Situation**"):
                                        with st.expander("Current Situation", expanded=True):
                                            st.write(section.replace("**Current Situation**: ", "") or "No situation data available.")
                                    elif section.startswith("**Investment Recommendation**"):
                                        with st.expander("Investment Recommendation", expanded=True):
                                            section_content = section.replace("**Investment Recommendation**: ", "")
                                            section_content = section_content.replace(
                                                "strong financials", '<span class="positive">strong financials</span>'
                                            ).replace(
                                                "high valuation", '<span class="negative">high valuation</span>'
                                            ).replace(
                                                "client concentration risks", '<span class="negative">client concentration risks</span>'
                                            )
                                            st.markdown(section_content or "No recommendation data available.", unsafe_allow_html=True)
                                    elif section.startswith("**Conclusion**"):
                                        with st.expander("Conclusion", expanded=True):
                                            st.write(section.replace("**Conclusion**: ", "") or "No conclusion data available.")

                except Exception as e:
                    st.markdown(
                        f'<div class="error-box"><b>Error:</b> Error processing request: {str(e)}</div>',
                        unsafe_allow_html=True
                    )
                    st.write("Please check your API keys, internet connection, or try a different ticker.")
                    print(f"Exception occurred: {e}")  # Debug
        else:
            st.markdown(
                '<div class="error-box"><b>Error:</b> Please enter a valid stock ticker.</div>',
                unsafe_allow_html=True
            )
