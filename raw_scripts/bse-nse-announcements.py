import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd

# Try to import optional dependencies
try:
    from bse import BSE
    # Create downloads directory for BSE data
    bse_download_folder = os.path.join(os.getcwd(), "bse_downloads")
    os.makedirs(bse_download_folder, exist_ok=True)
    b = BSE(download_folder=bse_download_folder)
    BSE_AVAILABLE = True
except ImportError:
    BSE_AVAILABLE = False
    b = None
except Exception as e:
    BSE_AVAILABLE = False
    b = None

try:
    from nse import NSE
    # Create downloads directory for NSE data
    nse_download_folder = os.path.join(os.getcwd(), "nse_downloads")
    os.makedirs(nse_download_folder, exist_ok=True)
    nse_client = NSE(download_folder=nse_download_folder)
    NSE_AVAILABLE = True
except ImportError:
    NSE_AVAILABLE = False
    nse_client = None
except Exception as e:
    NSE_AVAILABLE = False
    nse_client = None

def parse_watchlist(content):
    """Parse watchlist from content string"""
    if isinstance(content, str):
        return [line.strip() for line in content.split('\n') if line.strip()]
    return []

def compute_score(tags, sentiment):
    """Compute alert score based on tags and sentiment"""
    return int(sentiment * len(tags))

def heatmap_level(score):
    """Convert score to heatmap emoji"""
    return "🔥" if score >= 80 else "⚠️" if score >= 60 else "🧊"

def fetch_news(ticker):
    """Fetch news for a ticker from external API"""
    url = f"https://scanx.trade/api/news?ticker={ticker}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"News API unavailable for {ticker}: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error fetching news for {ticker}: {str(e)}")
        return []

def fetch_bse_updates(ticker):
    """Fetch BSE corporate actions for a ticker"""
    if not BSE_AVAILABLE:
        return []
    
    try:
        scrip = b.getScripCode(ticker)
        if not scrip:
            return []
        actions = b.actions(scripcode=scrip)
        if actions and isinstance(actions, list):
            return [{"subject": a.get("subject", "No subject"), 
                    "date": a.get("exDate", a.get("date", "No date")), 
                    "url": a.get("attachmentUrl", "")} for a in actions[:5]]  # Limit to 5 recent actions
        return []
    except Exception as e:
        st.warning(f"BSE data unavailable for {ticker}: {str(e)}")
        return []

def fetch_nse_updates(ticker):
    """Fetch NSE corporate announcements for a ticker"""
    if not NSE_AVAILABLE or not nse_client:
        return []
    
    try:
        # Get corporate announcements
        announcements = nse_client.announcements(symbol=ticker.upper())
        if announcements and isinstance(announcements, list):
            return [{"subject": a.get("headline", a.get("subject", "No subject")), 
                    "date": a.get("date", a.get("announcementDate", "No date")), 
                    "url": a.get("link", a.get("url", ""))} for a in announcements[:5]]  # Limit to 5 recent
        
        # Fallback to corporate actions if announcements don't work
        actions = nse_client.actions(symbol=ticker.upper())
        if actions and isinstance(actions, list):
            return [{"subject": a.get("subject", a.get("purpose", "Corporate Action")), 
                    "date": a.get("exDate", a.get("date", "No date")), 
                    "url": a.get("link", "")} for a in actions[:5]]
        
        return []
    except Exception as e:
        st.warning(f"NSE data unavailable for {ticker}: {str(e)}")
        return []

def fetch_alert_stream():
    """Fetch alert stream from local API with fallback"""
    try:
        response = requests.get("http://localhost:8000/alerts", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.info("Local alert API not available. Using sample data.")
        # Return sample data structure
        return []
    except Exception as e:
        st.error(f"Error fetching alert stream: {str(e)}")
        return []

def generate_alerts(watchlist, stream):
    """Generate alerts from all data sources"""
    alerts = []
    
    if not watchlist:
        st.warning("No tickers in watchlist")
        return []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_tickers = len(watchlist)
    
    for i, ticker in enumerate(watchlist):
        status_text.text(f"Processing {ticker}... ({i+1}/{total_tickers})")
        progress_bar.progress((i + 1) / total_tickers)
        
        # Process stream matches
        matches = [s for s in stream if s.get("linked_ticker") == ticker]
        for m in matches:
            m["score"] = compute_score(m.get("tags", []), m.get("sentiment", 50))
            m["heatmap"] = heatmap_level(m["score"])
            alerts.append(m)

        # Fetch news
        for news in fetch_news(ticker):
            alerts.append({
                "linked_ticker": ticker,
                "timestamp": news.get("timestamp", datetime.now().isoformat()),
                "source": "News",
                "score": 70,
                "heatmap": "⚠️",
                "sentiment": 60,
                "message": news.get("headline", "No headline"),
                "tags": ["news"],
                "url": news.get("url", "")
            })

        # Fetch regulatory filings
        bse_filings = fetch_bse_updates(ticker)
        nse_filings = fetch_nse_updates(ticker)
        
        for filing in bse_filings + nse_filings:
            alerts.append({
                "linked_ticker": ticker,
                "timestamp": filing.get("date", datetime.now().isoformat()),
                "source": "Filings",
                "score": 75,
                "heatmap": "🔥",
                "sentiment": 70,
                "message": filing.get("subject", "No subject"),
                "tags": ["filing"],
                "url": filing.get("url", "")
            })
    
    progress_bar.empty()
    status_text.empty()
    
    return sorted(alerts, key=lambda x: x.get("score", 0), reverse=True)

def cleanup_resources():
    """Clean up resources when app closes"""
    try:
        if BSE_AVAILABLE and b:
            b.exit()
    except:
        pass
    
    try:
        if NSE_AVAILABLE and nse_client:
            nse_client.exit()
    except:
        pass

# Streamlit UI
st.set_page_config(layout="wide", page_title="Stock Alert Cockpit")
st.title("📡 Real-Time Alert Cockpit | NSE Watchlist")

# Installation instructions
with st.expander("📦 Installation Instructions", expanded=False):
    st.code("""
# Required libraries:
pip install streamlit requests

# For BSE data (corporate actions):
pip install bse

# For NSE data (corporate announcements & actions):
pip install nse

# After installation, restart the app
""")
    
    if not BSE_AVAILABLE and not NSE_AVAILABLE:
        st.error("⚠️ No stock exchange libraries installed! Please install BSE and/or NSE libraries using the commands above.")
    elif not BSE_AVAILABLE:
        st.warning("⚠️ BSE library not available. Install with: pip install bse")
    elif not NSE_AVAILABLE:
        st.warning("⚠️ NSE library not available. Install with: pip install nse")
    else:
        st.success("✅ Both BSE and NSE libraries are available!")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Watchlist input options
watchlist_option = st.sidebar.radio(
    "Choose watchlist source:",
    ["Upload file", "Enter manually", "Use sample data"]
)

watchlist = []

if watchlist_option == "Upload file":
    uploaded_file = st.sidebar.file_uploader(
        "Upload watchlist file (one ticker per line)", 
        type=['txt', 'csv']
    )
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        watchlist = parse_watchlist(content)
        st.sidebar.success(f"Loaded {len(watchlist)} tickers")

elif watchlist_option == "Enter manually":
    ticker_input = st.sidebar.text_area(
        "Enter stock tickers (one per line):",
        placeholder="RELIANCE\nTCS\nINFY\nHDFC"
    )
    if ticker_input:
        watchlist = parse_watchlist(ticker_input)
        st.sidebar.success(f"Added {len(watchlist)} tickers")

else:  # Use sample data
    watchlist = ["RELIANCE", "TCS", "INFOSYS", "HDFCBANK", "ICICIBANK"]
    st.sidebar.info(f"Using sample watchlist: {', '.join(watchlist)}")

# Main content
if not watchlist:
    st.warning("Please provide a watchlist to get started.")
    st.info("You can upload a file, enter tickers manually, or use sample data from the sidebar.")
else:
    st.write(f"Monitoring **{len(watchlist)}** stocks: {', '.join(watchlist)}")
    
    # Fetch data
    with st.spinner("Fetching alert data..."):
        alert_stream = fetch_alert_stream()
        all_alerts = generate_alerts(watchlist, alert_stream)
    
    if not all_alerts:
        st.info("No alerts found for the current watchlist.")
    else:
        st.success(f"Found {len(all_alerts)} alerts")
        
        # Display filters
        col1, col2, col3 = st.columns(3)
        with col1:
            min_score = st.slider("Minimum Score", 0, 100, 0)
        with col2:
            source_filter = st.multiselect(
                "Filter by Source", 
                options=list(set(alert.get("source", "Unknown") for alert in all_alerts)),
                default=list(set(alert.get("source", "Unknown") for alert in all_alerts))
            )
        with col3:
            ticker_filter = st.multiselect(
                "Filter by Ticker",
                options=watchlist,
                default=watchlist
            )
        
        # Apply filters
        filtered_alerts = [
            alert for alert in all_alerts
            if (alert.get("score", 0) >= min_score and
                alert.get("source", "Unknown") in source_filter and
                alert.get("linked_ticker", "") in ticker_filter)
        ]
        
        st.write(f"Showing {len(filtered_alerts)} alerts after filtering")
        
        # Display alerts
        for alert in filtered_alerts:
            with st.expander(f"{alert.get('linked_ticker', 'Unknown')} - {alert.get('message', 'No message')[:50]}..."):
                st.markdown(f"""
                **Ticker:** {alert.get('linked_ticker', 'Unknown')}  
                **Source:** {alert.get('source', 'Unknown')} | **Time:** {alert.get('timestamp', 'Unknown')}  
                **Score:** {alert.get('score', 0)} {alert.get('heatmap', '')} | **Sentiment:** {alert.get('sentiment', 0)}  
                **Message:** {alert.get('message', 'No message')}  
                **Tags:** {', '.join(alert.get('tags', []))}  
                """)
                
                if alert.get('url') and alert['url'] != '#':
                    st.link_button("View Details", alert['url'])

# Add refresh button
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Refresh Data"):
        st.rerun()

with col2:
    if st.button("🧹 Cleanup Resources"):
        cleanup_resources()
        st.success("Resources cleaned up successfully!")

# Display library status
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Data Source Status")
if BSE_AVAILABLE:
    st.sidebar.success("✅ BSE: Corporate actions available")
else:
    st.sidebar.error("❌ BSE: Not available")

if NSE_AVAILABLE:
    st.sidebar.success("✅ NSE: Announcements & actions available")
else:
    st.sidebar.error("❌ NSE: Not available")

# Add cleanup on script rerun
import atexit
atexit.register(cleanup_resources)