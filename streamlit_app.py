import streamlit as st
import pandas as pd
from app.service import get_data

intervals = {
    "Latest": "latest",
    "Last Week": "lastweek",
    "Custom Period": "period"
}

now = pd.Timestamp.now().tz_localize(None)

# Initialize session state for fetched data if it doesn't exist
if "fetched_data" not in st.session_state:
    st.session_state.fetched_data = None

def create_chart(df):
    """
    Creates the line or bar chart based on the number of unique MTU Start timestamps in the DataFrame. If there is only one unique timestamp, a bar chart is created; otherwise, a line chart is created.
    Input: df - a pandas DataFrame containing the data to be visualized, with columns 'MTU Start', 'Area', and 'Value'
    Output: renders a line or bar chart in the Streamlit app based on the processed DataFrame

    Chart:
        - X axis represents 'MTU Start' timestamps
        - Y axis represents 'Value'
        - Different lines or bars represent different 'Area' values
    """
    chart_df = df.copy()
    chart_df["MTU Start"] = pd.to_datetime(chart_df["MTU Start"])
    chart_df = chart_df.sort_values("MTU Start")

    chart_df = chart_df.groupby(["MTU Start", "Area"], as_index=False)["Value"].first()
    chart_df = chart_df.pivot(index="MTU Start", columns="Area", values="Value")

    st.subheader("Market Values Chart")

    if len(chart_df) == 1:
        st.bar_chart(chart_df)
    else:
        st.line_chart(chart_df)

# Simple Title and text for the app
st.title("Energy Market Data Dashboard")
st.markdown("Real-Time Electricity Market Data Visualization")


mode = st.selectbox("Select Data Retrieval Mode", list(intervals.keys()), index=0)
start_date = None
end_date = None

mode = intervals[mode]

# Checking the mode and showing the date input fields if the user selects "Custom Period"
if mode == "period":
    start_date = st.datetime_input("Start Date", value=now - pd.Timedelta(days=2), max_value=now - pd.Timedelta(minutes=1))
    end_date = st.datetime_input("End Date", value=now - pd.Timedelta(days=1), max_value=now - pd.Timedelta(minutes=1))

# Button to trigger data fetching based on the selected mode and date inputs
# Saving the fetched data in session state to persist it across interactions and avoid refetching on every change
if st.button("Fetch Data"):
    with st.spinner("Fetching data from the API..."):
        try:
            if mode == "period":
                if end_date < start_date:
                    st.error("End date must be greater than or equal to start date.")
                    st.stop()

                start_date = start_date.isoformat()
                end_date = end_date.isoformat()
                
            data = get_data(mode=mode, start=start_date, end=end_date)
            st.session_state.fetched_data = data

        except Exception as exc:
            st.error(f"An error occurred while fetching data: {exc}")


# Display the fetched data in a table and create a chart if data is available, with options to filter by Area and Value range
if st.session_state.fetched_data:
    df = pd.DataFrame(st.session_state.fetched_data)


    area_filter = st.selectbox(
        "Filter by Area",
        ["All"] + sorted(df["Area"].dropna().unique().tolist())
    )
    
    if area_filter != "All":
        df = df[df["Area"] == area_filter]

    value_filter = st.slider(
        "Filter by Value",
        int(df["Value"].min()),
        int(df["Value"].max()),
        (int(df["Value"].min()), int(df["Value"].max()))
    )

    if value_filter:
        df = df[(df["Value"] >= value_filter[0]) & (df["Value"] <= value_filter[1])]

    if df.empty:
        st.warning("No data available for the selected filter.")
    else:
        st.dataframe(df)
        st.write("Total Items Fetched:", len(df))
        st.write("Last Fetch Time:", now.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            create_chart(df)
        except Exception as exc:
            st.error(f"An error occurred while creating the chart: {exc}")

