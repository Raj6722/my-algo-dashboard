import streamlit as st
import pandas as pd
import pymongo
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# पेज सेटअप
st.set_page_config(page_title="Covered Call Dashboard V3", layout="wide")
st.title("📈 Delta Exchange: Covered Call Accumulation V3 (Cloud Synced)")

# ऑटो रिफ्रेश (हर 60 सेकंड)
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 60 seconds", value=True)
if auto_refresh:
    st_autorefresh(interval=60 * 1000, key="data_refresh")

st.sidebar.markdown("---")
st.sidebar.info("यह डैशबोर्ड सीधे आपके VPS से MongoDB के ज़रिए जुड़ा है।")

# MongoDB से कनेक्शन
@st.cache_resource(ttl=30)
def init_connection():
    try:
        return pymongo.MongoClient(st.secrets["mongo_uri"], tlsAllowInvalidCertificates=True)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

client = init_connection()

# स्ट्रिंग को DataFrame में बदलने का फंक्शन
def get_df(csv_string):
    if not csv_string or len(csv_string.strip()) == 0:
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(csv_string))

if client:
    db = client.AlgoDashboard
    # क्लाउड से अपना सिंक किया हुआ डेटा मंगाएं
    cloud_data = db.Strategy_Data.find_one({"strategy_name": "Covered_Call_V3"})

    if not cloud_data:
        st.warning("⚠️ क्लाउड पर अभी कोई डेटा नहीं है। कृपया अपने VPS पर 'Bot.py' चलाएं।")
    else:
        st.success(f"✅ Last Synced from VPS: {cloud_data.get('last_updated', 'Unknown')}")
        
        # डेटाफ्रेम बनाना
        btc_df = get_df(cloud_data.get('btc_csv', ''))
        opt_df = get_df(cloud_data.get('opt_csv', ''))
        pnl_df = get_df(cloud_data.get('pnl_csv', ''))

        st.divider()
        st.header("📜 Trade History Logs")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Bitcoin (BTC) Trades")
            if not btc_df.empty:
                st.dataframe(btc_df.sort_values(by=btc_df.columns[0], ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("No BTC trades found.")
                
        with col_b:
            st.subheader("Options Trades (Entry & Exit)")
            if not opt_df.empty:
                st.dataframe(opt_df.sort_values(by=opt_df.columns[0], ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("No Option trades found.")

        st.divider()
        st.subheader("📊 Option PnL Logs")
        if not pnl_df.empty:
            st.dataframe(pnl_df, use_container_width=True, hide_index=True)
        else:
            st.info("No PnL data found.")
