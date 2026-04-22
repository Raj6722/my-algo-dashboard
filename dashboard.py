import streamlit as st
import pymongo

st.title("My Algo Trading Dashboard")

client = pymongo.MongoClient("YOUR_MONGODB_CONNECTION_STRING")
db = client.AlgoDashboard
data = list(db.Strategy_Data.find())

for item in data:
    st.metric(label=item['strategy_name'], value=f"₹{item['pnl']}", delta=item['status'])