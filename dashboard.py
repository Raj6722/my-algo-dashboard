import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime

# पेज की सेटिंग्स
st.set_page_config(page_title="Raj Algo Dashboard", layout="wide")

st.title("📊 My Algo Trading Dashboard")
st.write(f"Last Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# MongoDB से कनेक्ट करने का फंक्शन
@st.cache_resource
def get_database_connection():
    try:
        # Secrets से URI उठाना
        uri = st.secrets["mongo_uri"]
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        # कनेक्शन चेक करना
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

client = get_database_connection()

if client:
    db = client.AlgoDashboard  # आपके डेटाबेस का नाम
    collection = db.Strategy_Data # आपकी कलेक्शन का नाम

    # डेटा फेच करना
    try:
        data = list(collection.find())
        
        if not data:
            st.warning("⚠️ डेटाबेस में अभी कोई डेटा नहीं मिला। अपने VPS अल्गो से डेटा भेजें।")
            st.info("डेटा भेजने के लिए अपने Python स्क्रिप्ट में `collection.update_one()` का उपयोग करें।")
        else:
            # डेटा को सुंदर टेबल या कार्ड्स में दिखाना
            df = pd.DataFrame(data)
            
            # ऊपर मुख्य समरी (Metrics) दिखाना
            col1, col2, col3 = st.columns(3)
            total_pnl = df['pnl'].sum() if 'pnl' in df.columns else 0
            active_algos = len(df)
            
            col1.metric("Total P&L", f"₹{total_pnl}")
            col2.metric("Active Strategies", active_algos)
            col3.metric("Market Status", "LIVE" if 9 <= datetime.now().hour < 16 else "CLOSED")

            st.divider()

            # हर स्ट्रैटेजी के लिए अलग कार्ड
            st.subheader("Strategy Wise Performance")
            cols = st.columns(3)
            for index, row in df.iterrows():
                with cols[index % 3]:
                    st.info(f"**Strategy: {row.get('strategy_name', 'Unknown')}**")
                    st.write(f"Status: {row.get('status', 'N/A')}")
                    st.write(f"Current P&L: ₹{row.get('pnl', 0)}")
                    st.caption(f"Last Updated: {row.get('last_updated', 'N/A')}")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# ऑटो रिफ्रेश बटन
if st.button('🔄 Manual Refresh'):
    st.rerun()

# ऑटो रिफ्रेश के लिए निर्देश
st.sidebar.markdown("---")
st.sidebar.write("💡 **Tip:** अपनी VPS स्क्रिप्ट में डेटा भेजते समय `strategy_name` को Unique रखें।")
