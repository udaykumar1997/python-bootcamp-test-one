# ---------------------------------------------------------------
# CHECKPOINT 2  (1:45 PM) — KPI tiles
# Goal: four metrics in a row, then the data.
# ---------------------------------------------------------------
import streamlit as st
import pandas as pd

st.title("Superstore Sales Dashboard")

# --- Load data ---
orders = pd.read_csv("data/superstore.csv")

# --- KPIs (same math as notebook Part 2.7) ---
total_sales = orders["Sales"].sum()
total_profit = orders["Profit"].sum()
order_count = orders["Order ID"].nunique()      # distinct orders, not rows
avg_order = total_sales / order_count

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total sales", f"${total_sales:,.0f}")
col2.metric("Total profit", f"${total_profit:,.0f}")
col3.metric("Orders", f"{order_count:,}")
col4.metric("Avg order value", f"${avg_order:,.2f}")

# --- Raw data ---
st.subheader("Order lines")
st.dataframe(orders)
