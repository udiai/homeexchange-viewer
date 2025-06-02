import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="HomeExchange Viewer", layout="wide")
st.title("🏠 HomeExchange Request Viewer")

uploaded_file = st.file_uploader("Upload your HomeExchange Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Basic cleaning
        df = df.dropna(subset=["Name", "City", "Country", "From Date", "Until Date"])
        df["From Date"] = pd.to_datetime(df["From Date"])
        df["Until Date"] = pd.to_datetime(df["Until Date"])
        df["Name_City"] = df["Name"] + " - " + df["City"]

        st.success("✅ File loaded successfully!")

        # Filters
        with st.sidebar:
            st.header("📅 Filter by Date")
            min_date = df["From Date"].min()
            max_date = df["Until Date"].max()
            date_range = st.date_input("Show requests between:", [min_date, max_date])

            st.header("🌍 Filter by Country")
            countries = st.multiselect("Choose countries:", options=sorted(df["Country"].unique()), default=sorted(df["Country"].unique()))

        # Apply filters
        filtered_df = df[
            (df["From Date"] >= pd.to_datetime(date_range[0])) &
            (df["Until Date"] <= pd.to_datetime(date_range[1])) &
            (df["Country"].isin(countries))
        ]

        # Timeline chart
        st.subheader("📊 Timeline View")
        fig = px.timeline(
            filtered_df,
            x_start="From Date",
            x_end="Until Date",
            y="Name_City",
            color="Country",
            labels={"Name_City": "Exchange"},
            title="Home Exchange Requests Timeline"
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

        # Table view
        st.subheader("📋 Data Table")
        st.dataframe(filtered_df.reset_index(drop=True))

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("👈 Upload an Excel file to begin.")
