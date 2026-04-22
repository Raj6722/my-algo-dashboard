import streamlit as st
import pymongo

st.title("My Algo Trading Dashboard")

client = pymongo.MongoClient("YOUR_MONGODB_CONNECTION_STRING")
db = client.AlgoDashboard
data = list(db.Strategy_Data.find())

for item in data:
    st.metric(label=item['strategy_name'], value=f"₹{item['pnl']}", delta=item['status'])

# Secrets से कनेक्ट करने का सही तरीका
client = pymongo.MongoClient(
    st.secrets["mongo_uri"], 
    serverSelectionTimeoutMS=5000  # 5 सेकंड का वेट करेगा
)
