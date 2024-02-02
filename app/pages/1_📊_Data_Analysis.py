"""The module to display data analysis in the app."""
import os
import io
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from zipfile import ZipFile
import matplotlib.pyplot as plt
from streamlit_extras.switch_page_button import switch_page


st.set_page_config(page_title="Data Analysis", page_icon="📊")


@st.cache_data()
def read_zip_file(zip_file: str) -> tuple:
    """Read three CSV files from a zip archive and return them as DataFrames.

    Parameters:
    - zip_file (str): The path to the zip file.

    Returns:
    - tuple: A tuple containing three DataFrames read from the CSV files.
    """
    with ZipFile(zip_file, "r") as z:
        dataframes = {}
        for name in z.namelist():
            if name.endswith(".csv"):
                # Extract DataFrame name from CSV file name
                dataframe_name = os.path.splitext(os.path.basename(name))[0] + "_df"
                with z.open(name) as f:
                    df = pd.read_csv(io.TextIOWrapper(f, "utf-8"))
                dataframes[dataframe_name] = df
    return tuple(dataframes.values())


@st.cache_data()
def preloaded():
    actions_df = pd.read_csv("data/actions.csv")
    clients_df = pd.read_csv("data/clients.csv")
    transactions_df = pd.read_csv("data/transactions.csv")

    return actions_df, clients_df, transactions_df


@st.cache_data()
def display_kpis(kpi_names, kpi_values):
    """
    Display KPIs using st.metric().

    Parameters:
        kpi_names (list): List of KPI names.
        kpi_values (list): List of corresponding KPI values.

    Returns:
        None
    """
    col1, col2, col3 = st.columns(3)

    # Display KPIs
    for name, value, col in zip(kpi_names, kpi_values, [col1, col2, col3]):
        col.metric(label=name, value=value)


st.title("Analytics Dashboard")

zip_file = st.file_uploader(
    "Upload a zip file", type="zip", accept_multiple_files=False
)

actions_df, clients_df, transactions_df = preloaded()

if st.button("Use pre-loaded file"):
    pass
else:
    if zip_file:
        # Display success message
        st.success("File uploaded successfully!")

        actions_df, clients_df, transactions_df = read_zip_file(zip_file)


if (
    (actions_df is not None)
    and (clients_df is not None)
    and (transactions_df is not None)
):

    st.subheader("Key Metrics")

    # Merge dataframes on client_id
    merged_df = pd.merge(actions_df, clients_df, on="client_id", how="left")
    merged_df = pd.merge(merged_df, transactions_df, on="client_id", how="left")

    # Sidebar filters
    st.sidebar.header("Filters")

    # Start and end date filter
    merged_df["transaction_date"] = pd.to_datetime(merged_df["transaction_date"])
    min_date = merged_df["transaction_date"].min()
    max_date = merged_df["transaction_date"].max()
    start_date = pd.Timestamp(
        st.sidebar.date_input(
            "Start date",
            min_date.date(),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    )
    end_date = pd.Timestamp(
        st.sidebar.date_input(
            "End date",
            max_date.date(),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    )

    # Client attendance filter
    client_attendance_options = ["All"] + list(actions_df["client_is_present"].unique())
    selected_client_attendance = st.sidebar.selectbox(
        "Client Attendance", client_attendance_options
    )

    # Event type filter
    event_type_options = ["All"] + list(actions_df["action_label"].unique())
    selected_event_type = st.sidebar.selectbox("Event Type", event_type_options)

    # Countries filter
    country_options = ["All"] + list(clients_df["client_country"].unique())
    selected_country = st.sidebar.selectbox("Country", country_options)

    # Client premium status filter
    premium_status_options = ["All"] + list(
        clients_df["client_premium_status"].unique()
    )
    selected_premium_status = st.sidebar.selectbox(
        "Premium Status", premium_status_options
    )

    # Apply filters
    filtered_df = merged_df[
        (
            (selected_client_attendance == "All")
            | (merged_df["client_is_present"] == selected_client_attendance)
        )
        & (
            (selected_event_type == "All")
            | (merged_df["action_label"] == selected_event_type)
        )
        & (
            (selected_country == "All")
            | (merged_df["client_country"] == selected_country)
        )
        & (
            (selected_premium_status == "All")
            | (merged_df["client_premium_status"] == selected_premium_status)
        )
        & (
            (merged_df["transaction_date"] >= start_date)
            & (merged_df["transaction_date"] <= end_date)
        )
    ]

    # Calculate the total gross amount in millions with the Euro symbol
    total_gross_amount_millions = filtered_df["gross_amount_euro"].sum() / 1e6
    total_gross_amount_formatted = f"{total_gross_amount_millions:.2f}M €"

    # Calculate the attendance rate and format it
    attendance_rate = filtered_df["client_is_present"].mean() * 100
    attendance_rate_formatted = f"{attendance_rate:.2f}%"

    # Calculate the number of contactable clients
    contactable_clients = filtered_df[filtered_df["client_is_contactable"] == 1][
        "client_id"
    ].nunique()

    # Example KPIs with emojis
    kpi_names = [
        ":money_with_wings: Total Gross Amount",
        ":bar_chart: Attendance Rate",
        ":busts_in_silhouette: Number of Contactable Clients",
    ]
    kpi_values = [
        total_gross_amount_formatted,
        attendance_rate_formatted,
        contactable_clients,
    ]

    display_kpis(kpi_names, kpi_values)

    st.write("\n")
    st.write("\n")

    st.subheader("📈 Monthly Evolution of Gross Amount")

    # Group by month and sum the 'gross_amount_euro'
    filtered_df["transaction_date"] = filtered_df["transaction_date"].dropna()
    monthly_gross_amount = (
        filtered_df.groupby(pd.Grouper(key="transaction_date", freq="M"))[
            "gross_amount_euro"
        ]
        .sum()
        .reset_index()
    )

    # Plot the monthly evolution
    plt.figure(figsize=(12, 8))
    sns.lineplot(x="transaction_date", y="gross_amount_euro", data=monthly_gross_amount)
    plt.xlabel("Month")
    plt.ylabel("Gross Amount (Euro)")
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    st.pyplot(plt)

    st.write("\n")
    st.subheader("⭐ Client Attendance per Country (Top 10)")

    # Calculate total attendance across all countries
    total_attendance = filtered_df["client_is_present"].sum()

    # Calculate attendance per country
    attendance_per_country = (
        filtered_df.groupby("client_country")["client_is_present"].sum().reset_index()
    )

    # Sort by attendance rate and select the top 10 countries
    top_countries = attendance_per_country.nlargest(10, "client_is_present")

    # Calculate percentage of attendance for each country based on the total attendance
    top_countries["attendance_percentage"] = (
        top_countries["client_is_present"] / total_attendance
    ) * 100

    # Plot donut chart
    plt.figure(figsize=(8, 6))

    # Outer pie chart (actual data)
    plt.pie(
        top_countries["client_is_present"],
        labels=top_countries["client_country"],
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.85,
        wedgeprops=dict(width=0.3, edgecolor="w"),
    )
    # Inner pie chart (empty center)
    plt.pie([1], colors="white", radius=0.6)
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis("equal")
    st.pyplot(plt)

    st.write("\n")
    # st.write(filtered_df)

    # Display filtered dataframe
    st.subheader("🕒 Average Duration of Each Type of Event")

    filtered_df["action_start_date"] = pd.to_datetime(filtered_df["action_start_date"])
    filtered_df["action_end_date"] = pd.to_datetime(filtered_df["action_end_date"])

    # Calculate event durations in days
    filtered_df["action_duration_days"] = (
        filtered_df["action_end_date"] - filtered_df["action_start_date"]
    ).dt.days

    filtered_df.loc[
        filtered_df["action_duration_days"] == 0, "action_duration_days"
    ] = 1

    # Group by action label and calculate the average duration
    avg_duration_per_action = (
        filtered_df.groupby("action_label")["action_duration_days"].mean().reset_index()
    )

    # Sort the DataFrame by average duration in descending order
    avg_duration_per_action = avg_duration_per_action.sort_values(
        by="action_duration_days", ascending=False
    )

    # Create a color palette for each action label
    palette = sns.color_palette("husl", len(avg_duration_per_action))

    # Plot the bar plot
    plt.figure(figsize=(12, 6))
    sns.barplot(
        x="action_label",
        y="action_duration_days",
        data=avg_duration_per_action,
        palette=palette,
    )
    plt.xlabel("Event Type")
    plt.ylabel("Average Event Duration (days)")
    plt.xticks(rotation=90)
    st.pyplot(plt)

    # Button to navigate to the inner page
    get_clients_button = st.button("Suggest clients now!")

    if get_clients_button:
        switch_page("client_suggestion")
