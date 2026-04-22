import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime
import ssl

# पेज सेटअप
st.set_page_config(page_title="Algo Monitor", layout="wide")

# CSS - सुंदर दिखाने के लिए
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_index=True)

st.title("📊 My Algo Trading Dashboard")

# MongoDB से सुरक्षित कनेक्शन
@st.cache_resource
def init_connection():
    try:
        # Secrets से URL उठाना
        conn_str = st.secrets["mongo_uri"]
        # SSL और Timeout सेटिंग्स के साथ कनेक्शन
        return pymongo.MongoClient(
            conn_str,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
    except Exception as e:
        st.error(f"❌ Connection Failed: {e}")
        return None

client = init_connection()

if client:
    try:
        # डेटाबेस और कलेक्शन (अपनी मर्ज़ी से नाम बदल सकते हैं)
        db = client.AlgoDashboard 
        collection = db.Strategy_Data
        
        # डेटा फेच करना
        data = list(collection.find().sort("last_updated", -1))

        if not data:
            st.info("🕒 अभी कोई लाइव डेटा नहीं है। कृपया अपने VPS अल्गो से डेटा भेजें।")
        else:
            df = pd.DataFrame(data)
            
            # टॉप मैट्रिक्स
            col1, col2, col3 = st.columns(3)
            with col1:
                total_pnl = df['pnl'].sum() if 'pnl' in df.columns else 0
                st.metric("Net P&L", f"₹{total_pnl}", delta_color="normal")
            with col2:
                st.metric("Total Strategies", len(df))
            with col3:
                last_time = datetime.now().strftime("%H:%M:%S")
                st.metric("Last Sync", last_time)

            st.divider()

            # डेटा टेबल और कार्ड्स
            st.subheader("Live Strategy Status")
            
            # डिस्प्ले के लिए ज़रूरी कॉलम्स चुनना
            display_cols = ['strategy_name', 'pnl', 'status', 'last_updated']
            available_cols = [c for c in display_cols if c in df.columns]
            
            # सुंदर टेबल दिखाना
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

            # विज़ुअल कार्ड्स (Grid View)
            st.write("---")
            grid = st.columns(3)
            for i, row in df.iterrows():
                with grid[i % 3]:
                    color = "green" if row.get('pnl', 0) >= 0 else "red"
                    st.markdown(f"""
                        <div style="border: 1px solid #444; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                            <h3 style="margin:0;">{row.get('strategy_name', 'N/A')}</h3>
                            <p style="color:{color}; font-size: 20px; font-weight: bold; margin:5px 0;">
                                P&L: ₹{row.get('pnl', 0)}
                            </p>
                            <p style="margin:0; opacity: 0.8;">Status: {row.get('status', 'Running')}</p>
                            <small>Updated: {row.get('last_updated', 'N/A')}</small>
                        </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ डेटा लोड करने में समस्या: {e}")

# ऑटो रिफ्रेश के लिए बटन
if st.button('🔄 Refresh Data'):
    st.rerun()

st.caption("Developed for Algo Monitoring | Lucknow, UP")
