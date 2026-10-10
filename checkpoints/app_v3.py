# ---------------------------------------------------------------
# CHECKPOINT 3  (2:15 PM) — filters + charts
# Goal: sidebar filters that drive everything; two charts.
# ---------------------------------------------------------------
import streamlit as st
import pandas as pd

st.title("Superstore Sales Dashboard")

# --- Load data ---
orders = pd.read_csv("data/superstore.csv")
orders["Order Date"] = pd.to_datetime(orders["Order Date"], format="%m/%d/%Y")

# --- Sidebar filters ---
st.sidebar.header("Filters")
all_regions = sorted(orders["Region"].unique())
all_categories = sorted(orders["Category"].unique())
regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)
categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)

# Apply filters — same isin pattern as the notebook's filter, Part 2.6
filtered = orders[orders["Region"].isin(regions) & orders["Category"].isin(categories)]

# --- KPIs (computed on the FILTERED data) ---
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
order_count = filtered["Order ID"].nunique()
avg_order = total_sales / order_count if order_count else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total sales", f"${total_sales:,.0f}")
col2.metric("Total profit", f"${total_profit:,.0f}")
col3.metric("Orders", f"{order_count:,}")
col4.metric("Avg order value", f"${avg_order:,.2f}")

# --- Charts ---
st.subheader("Monthly sales")
monthly = filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"].sum()
monthly.index = monthly.index.to_timestamp()      # periods → real dates so the chart can plot them
st.line_chart(monthly)

st.subheader("Profit by sub-category")
by_subcat = filtered.groupby("Sub-Category")["Profit"].sum().sort_values()
st.bar_chart(by_subcat, horizontal=True)

# --- Raw data ---
st.subheader("Order lines")
st.dataframe(filtered)
