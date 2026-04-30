import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import base64
import re

def main():
    # Page configuration for a clean, full-width look
    st.set_page_config(
        page_title="Wahba EGX Trading Terminal",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 1. Branding and Full Logo Section with SVG
    # We combine the graphics (shield) and text into a single SVG unit for iOS/Android rendering
    logo_svg = """
    <svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
      <g id="WahbaShield" transform="translate(130, 20) scale(0.6)">
        <path d="M50 0 L100 20 L95 85 Q90 95 50 95 Q10 95 5 85 L0 20 Z" fill="#007bff" />
        <path d="M5 21 L95 21 M5 21 L5 22 M95 21 L95 22 M40 90 L60 90 Q65 90 65 85" stroke="white" stroke-width="1.5" fill="none"/>
        <g id="candles" transform="translate(15, 30)">
          <rect x="0" y="25" width="5" height="15" fill="white" />
          <rect x="10" y="20" width="5" height="20" fill="white" />
          <rect x="20" y="15" width="5" height="25" fill="white" />
          <rect x="30" y="10" width="5" height="30" fill="white" />
          <rect x="40" y="5" width="5" height="35" fill="white" />
          <rect x="50" y="0" width="5" height="40" fill="white" />
        </g>
        <path id="arrow" d="M15 70 Q35 60 45 40 Q55 20 65 10 L70 15 L65 5 L55 10 L60 15 Q50 25 40 45 Q30 65 15 70 Z" fill="white" />
      </g>
      
      <text x="50%" y="230" text-anchor="middle" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-weight="900" font-size="48" fill="black">WAHBA EGX</text>
      
      <text x="50%" y="270" text-anchor="middle" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" fill="black">INSTITUTIONAL MARKET TERMINAL</text>
    </svg>
    """
    
    # Render the combined logo unit at the top of the page
    st.markdown(
        f'<div style="text-align: center; width: 100%; display: flex; justify-content: center; margin-bottom: 20px;">{logo_svg}</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 2. Information and Quantitative Parameters
    # As requested, text from image_0.png
    st.markdown(
        '<div style="color: black; font-size: 18px; margin-bottom: 30px;">'
        'Quantitative Parameters: Price Action > SMA(10) | RSI(14) > 40'
        '</div>',
        unsafe_allow_html=True
    )

    # 3. Main Scanner Interface
    st.header("Egyptian Market Scanner")
    st.write("Scan the Egyptian Exchange (EGX) for institutional-grade opportunities.")

    # Target indices/stocks for the EGX
    target_stocks = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY"] # Example stocks

    # Create the full screener symbol list
    symbols = [f"EGYPT:{stock}" for stock in target_stocks]

    # SCAN BUTTON - The focus from image_0.png and image_9.png
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_scan = st.button("START INSTITUTIONAL MARKET SCAN")

    # Scan logic (if button is pressed)
    if start_scan:
        st.write("Fetching technical data...")
        results_data = []

        with st.spinner("Analyzing market structure..."):
            for symbol in symbols:
                try:
                    # Parse symbol to get only the stock name
                    stock_name = symbol.split(":")[1]
                    
                    handler = TA_Handler(
                        symbol=stock_name,
                        screener="egypt",
                        exchange="EGYPT",
                        interval=Interval.INTERVAL_1_DAY
                    )
                    analysis = handler.get_analysis()
                    
                    if analysis:
                        indicators = analysis.indicators
                        sma10 = indicators["SMA10"]
                        rsi14 = indicators["RSI"]
                        close = indicators["close"]
                        
                        # Calculate criteria
                        is_close_above_sma = close > sma10
                        is_rsi_gt_40 = rsi14 > 40
                        
                        # Institutional Criteria match
                        criteria_met = is_close_above_sma and is_rsi_gt_40
                        
                        results_data.append({
                            "Stock": stock_name,
                            "Close Price": f"{close:.2f}",
                            "RSI(14)": f"{rsi14:.2f}",
                            "SMA(10)": f"{sma10:.2f}",
                            "Close > SMA(10)": "✅" if is_close_above_sma else "❌",
                            "RSI(14) > 40": "✅" if is_rsi_gt_40 else "❌",
                            "Scan Result": "Met 🚀" if criteria_met else "Not Met"
                        })
                except Exception as e:
                    st.error(f"Error analyzing {symbol}: {e}")

        # Display results in a clean table
        if results_data:
            df = pd.DataFrame(results_data)
            st.success("Market analysis complete.")
            
            # Format the table display
            st.table(df)
            
            # Highlight met criteria in data
            st.info("Results highlighted in green indicate stocks that meet the parameters.")
        else:
            st.warning("No data retrieved.")

if __name__ == "__main__":
    main()
