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

        # Handle invalid date formats
        df["From Date"] = pd.to_datetime(df["From Date"], errors="coerce")
        df["Until Date"] = pd.to_datetime(df["Until Date"], errors="coerce")

        bad_rows = df[df["From Date"].isna() | df["Until Date"].isna()]
        if not bad_rows.empty:
            st.warning(f"⚠️ Skipped {len(bad_rows)} row(s) due to invalid dates.")

        df = df.dropna(subset=["From Date", "Until Date"])
        df["Name_City"] = df["Name"] + " - " + df["City"]

        st.success("✅ File loaded successfully!")

        # Filters
        with st.sidebar:
            st.header("📅 Filter by Date")
            min_date = df["From Date"].min().date()
            max_date = df["Until Date"].max().date()
            date_range = st.date_input(
                "Show requests between:", 
                value=[min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )

            st.header("🌍 Filter by Country")
            countries = st.multiselect(
                "Choose countries:", 
                options=sorted(df["Country"].unique()), 
                default=sorted(df["Country"].unique())
            )

        # Apply filters - handle both single date and date range
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range[0]

        filtered_df = df[
            (df["From Date"] >= pd.to_datetime(start_date)) &
            (df["Until Date"] <= pd.to_datetime(end_date)) &
            (df["Country"].isin(countries))
        ]

        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Requests", len(filtered_df))
        with col2:
            st.metric("Countries", filtered_df["Country"].nunique())
        with col3:
            st.metric("Date Range", f"{filtered_df['From Date'].min().strftime('%b %Y')} - {filtered_df['Until Date'].max().strftime('%b %Y')}")

        # Timeline chart
        st.subheader("📊 Timeline View")
        if not filtered_df.empty:
            fig = px.timeline(
                filtered_df,
                x_start="From Date",
                x_end="Until Date",
                y="Name_City",
                color="Country",
                labels={"Name_City": "Exchange"},
                title="Home Exchange Requests Timeline",
                height=max(400, len(filtered_df) * 30)
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Guest - City",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No requests match the selected filters.")

        # Table view
        st.subheader("📋 Data Table")
        if not filtered_df.empty:
            # Format dates for display
            display_df = filtered_df.copy()
            display_df["From Date"] = display_df["From Date"].dt.strftime("%Y-%m-%d")
            display_df["Until Date"] = display_df["Until Date"].dt.strftime("%Y-%m-%d")
            
            st.dataframe(
                display_df[[
                    "Name", "City", "Country", "From Date", "Until Date", 
                    "Bedroom", "Bathrooms", "Max People", "Sqr Meters", "Stars"
                ]].reset_index(drop=True),
                use_container_width=True
            )
            
            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"homeexchange_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data to display.")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.exception(e)
else:
    st.info("👈 Upload an Excel file to begin.")
