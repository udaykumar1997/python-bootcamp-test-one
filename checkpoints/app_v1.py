import streamlit as st
import pandas as pd

st.title("Superstore Sales Dashboard")

# Same line as in the notebook
orders = pd.read_csv("data/superstore.csv")

st.dataframe(orders)
