import streamlit as st
import pandas as pd

# ---------- Page setup (must be the first Streamlit call) ----------
st.set_page_config(page_title="Superstore Sales", page_icon="📊", layout="wide")


# ---------- Load data ----------
@st.cache_data  # remembers the result so the CSV isn't re-read on every click
def load_data():
    df = pd.read_csv("data/superstore.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df


orders = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

all_regions = sorted(orders["Region"].unique())
all_categories = sorted(orders["Category"].unique())
all_segments = sorted(orders["Segment"].unique())

regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)
categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)
segments = st.sidebar.multiselect("Segment", all_segments, default=all_segments)

min_date = orders["Order Date"].min().date()
max_date = orders["Order Date"].max().date()
date_range = st.sidebar.date_input("Order date range", (min_date, max_date), min_value=min_date, max_value=max_date)

# date_input returns a single date while the user is mid-selection; handle both cases
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = orders[
    orders["Region"].isin(regions)
    & orders["Category"].isin(categories)
    & orders["Segment"].isin(segments)
    & (orders["Order Date"].dt.date >= start_date)
    & (orders["Order Date"].dt.date <= end_date)
]

# ---------- Header ----------
st.title("📊 Superstore Sales Dashboard")
st.caption(
    f"{len(filtered):,} of {len(orders):,} order lines · "
    f"{start_date:%b %d, %Y} – {end_date:%b %d, %Y}"
)

if filtered.empty:
    st.warning("No orders match these filters. Try widening the date range or adding a region.")
    st.stop()

# ---------- KPIs ----------
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
margin = total_profit / total_sales if total_sales else 0
order_count = filtered["Order ID"].nunique()           # distinct orders, not rows
avg_order = total_sales / order_count if order_count else 0
avg_discount = filtered["Discount"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total sales", f"${total_sales:,.0f}")
k2.metric("Total profit", f"${total_profit:,.0f}", f"{margin:.1%} margin")
k3.metric("Orders", f"{order_count:,}")
k4.metric("Avg order value", f"${avg_order:,.2f}")
k5.metric("Avg discount", f"{avg_discount:.1%}")

st.divider()

# ---------- Charts ----------
left, right = st.columns([3, 2])

with left:
    st.subheader("Monthly sales")
    monthly = filtered.groupby("Month")["Sales"].sum()
    st.line_chart(monthly, height=300)

with right:
    st.subheader("Sales and profit by category")
    by_category = (
        filtered.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
    )
    st.bar_chart(by_category, height=300, stack=False)   # side-by-side bars, not stacked

c1, c2 = st.columns(2)

with c1:
    st.subheader("Profit by sub-category")
    st.caption("Negative bars are sub-categories that lose money.")
    by_subcat = filtered.groupby("Sub-Category")["Profit"].sum().sort_values()
    st.bar_chart(by_subcat, height=420, horizontal=True)

with c2:
    st.subheader("Top 10 products by sales")
    top_products = (
        filtered.groupby("Product Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum"))
        .sort_values("Sales", ascending=False)
        .head(10)
    )
    st.dataframe(
        top_products,
        column_config={
            "Product Name": st.column_config.TextColumn(width="medium"),
            "Sales": st.column_config.NumberColumn(format="$%,.0f"),
            "Profit": st.column_config.NumberColumn(format="$%,.0f"),
        },
    )

st.divider()

# ---------- Raw data + download ----------
st.subheader("Order lines")
show_cols = ["Order ID", "Order Date", "Customer Name", "Segment", "Region", "State",
             "Category", "Sub-Category", "Product Name", "Quantity", "Discount", "Sales", "Profit"]
st.dataframe(
    filtered[show_cols].sort_values("Order Date", ascending=False),
    column_config={
        "Order Date": st.column_config.DateColumn(format="MMM D, YYYY"),
        "Discount": st.column_config.NumberColumn(format="%.0f%%"),
        "Sales": st.column_config.NumberColumn(format="$%.2f"),
        "Profit": st.column_config.NumberColumn(format="$%.2f"),
    },
    hide_index=True,
)

st.download_button(
    "⬇️ Download filtered data (CSV)",
    data=filtered[show_cols].to_csv(index=False).encode("utf-8"),
    file_name="superstore_filtered.csv",
    mime="text/csv",
)

st.caption("Built at the Stevens Python Bootcamp 2026 · Streamlit + pandas · Data: Tableau Sample – Superstore.")
