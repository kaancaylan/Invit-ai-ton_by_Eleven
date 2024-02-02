import streamlit as st
import pandas as pd

st.set_page_config(page_title="Client Suggestion", page_icon="🧑🏻‍💼")

st.markdown(
    """
<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
    <h3 style='color:green; font-size: 24px;'>Welcome to client suggester</h3>
    <p style='color:green;font-size: 18px;'>Just select an action ID and
    number of clients you want to invite.
    Sit back and relax while we do the work for you!</p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("\n")
st.write("\n")


@st.cache_data()
def load_prev_clients():
    """
    Load and cache the DataFrame containing previous client data from a CSV file.

    Returns:
        DataFrame: DataFrame containing previous client data.
    """
    return pd.read_csv("data/df_with_preds.csv")


@st.cache_data()
def load_new_clients():
    """
    Load and cache the DataFrame containing new client data from a CSV file.

    Returns:
        DataFrame: DataFrame containing new client data.
    """
    return pd.read_csv("data/best_new_clients.csv")



prev_clients = load_prev_clients()
new_clients = load_new_clients()

prev_clients.drop("Unnamed: 0", axis=1, inplace=True)
new_clients.drop("Unnamed: 0", axis=1, inplace=True)


# Get unique action IDs from prev_clients
unique_action_ids = prev_clients["action_id"].unique()

# Create a layout with two columns of equal width
col1, col2 = st.columns(2)

# Place the selectbox in one of the columns
with col1:
    st.write("Select Action ID:")
    action_id = st.selectbox(" ", options=unique_action_ids)

# Place other elements in the other column
with col2:
    st.write("No of Clients to Invite:")
    top_clients = st.number_input(" ", value=10, min_value=1, step=1)

get_old_clients_button = st.button("Invite existing clients")
get_new_clients_button = st.button("Invite new clients")

if get_old_clients_button:
    st.write("Getting a list of our loyal clients")

    # Filter prev_clients based on action ID
    filtered_prev_clients = prev_clients[prev_clients["action_id"] == action_id]

    filtered_prev_clients = filtered_prev_clients.drop_duplicates(subset=["client_id"])
    filtered_prev_clients = filtered_prev_clients[
        filtered_prev_clients["uplift_pred"] > 0
    ]

    # Get top X client IDs based on highest uplift_pred values
    top_clients = filtered_prev_clients.nlargest(top_clients, "uplift_pred")[
        ["client_id", "uplift_pred"]
    ]

    # Display the DataFrame
    st.write(
        top_clients.rename(
            columns={"client_id": "Client ID", "uplift_pred": "Predicted Uplift"}
        ).reset_index(drop=True)
    )

elif get_new_clients_button:
    st.write("Let's invite some amazing new clients")

    # Filter new_clients based on action ID
    filtered_new_clients = new_clients[new_clients["action_id"] == action_id]

    # Get top X client IDs from new_clients
    top_clients = filtered_new_clients.nlargest(top_clients, "uplift_pred")[
        ["best_new_clients"]
    ].drop_duplicates()

    # Display the Dataframe
    st.write(
        top_clients.rename(columns={"best_new_clients": "Client ID"}).reset_index(
            drop=True
        )
    )
