import pandas as pd

CLIENTS_SIMILARITY_RULES = {
    "same_country": 1,
    "same_nationality": 3,
    "same_city": 5,
    "same_gender": 3,
}


def filter_client_df(clients_df, transactions_df):
    """Filter client DataFrame to keep only contactable clients.

    Args:
        clients_df (DataFrame): DataFrame containing client information.
        transactions_df (DataFrame): DataFrame containing transaction information.

    Returns:
        DataFrame: Filtered DataFrame containing contactable clients with an additional column indicating whether they have already done a transaction.
    """
    filtered_clients_df = clients_df.query("client_is_contactable == 1").drop(
        [
            "client_is_phone_contactable",
            "client_is_email_contactable",
            "client_is_instant_messaging_contactable",
            "client_is_contactable",
        ],
        axis=1,
    )
    clients_with_transactions = transactions_df["client_id"].unique()
    filtered_clients_df["has_already_done_transaction"] = filtered_clients_df[
        "client_id"
    ].isin(clients_with_transactions)

    return filtered_clients_df


def similarity_score(row, client_data):
    """Compute a similarity score between clients based on country, nationality, city, and gender.

    Args:
        row (Series): Row of the DataFrame representing a client.
        client_data (dict): Dictionary containing data of the reference client.

    Returns:
        int: Similarity score between the current client and the reference client.
    """
    score = 0
    if row["client_country"] == client_data["client_country"]:
        score += CLIENTS_SIMILARITY_RULES["same_country"]

    if row["client_nationality"] == client_data["client_nationality"]:
        score += CLIENTS_SIMILARITY_RULES["same_nationality"]

    if row["client_city"] == client_data["client_city"]:
        score += CLIENTS_SIMILARITY_RULES["same_city"]

    if row["client_gender"] == client_data["client_gender"]:
        score += CLIENTS_SIMILARITY_RULES["same_gender"]

    return score


def get_closest_clients(client_id, filtered_clients_df):
    """Find the closest clients, among all clients that did no transaction, to a given input client.

    Args:
        client_id (str): ID of the client.
        filtered_clients_df (DataFrame): DataFrame containing filtered client data.

    Returns:
        dict: Dictionary containing closest clients and their similarity scores.
    """
    client_data = filtered_clients_df.query(f"client_id == '{client_id}'").iloc[0]

    same_segment = (
        filtered_clients_df["client_segment"] == client_data["client_segment"]
    )
    same_status = (
        filtered_clients_df["client_premium_status"]
        == client_data["client_premium_status"]
    )
    has_never_done_transaction = (
        filtered_clients_df["has_already_done_transaction"] == False
    )

    similar_clients = filtered_clients_df[
        same_segment & same_status & has_never_done_transaction
    ].copy()
    similar_clients["similarity_score"] = similar_clients.apply(
        lambda row: similarity_score(row, client_data), axis=1
    )

    closest_clients = similar_clients[similar_clients["similarity_score"] > 0]
    closest_clients = {
        client_id: score
        for client_id, score in closest_clients[
            ["client_id", "similarity_score"]
        ].values
    }

    return closest_clients


def generate_best_new_clients(client_id_list, clients_df, transactions_df):
    """Generate the best new clients, among all clients that did no transaction, for a given list of clients.
    For each client in the list, get the closest clients and their similarity score
    Then, sum the score of all the close clients.
    So, if a client is close to all clients in the input list, but his similarity score is weak for each client,
    at the end he will get a high similarity score, since he is close to all clients in the list

    Args:
        client_id_list (list): List of client IDs.
        clients_df (DataFrame): DataFrame containing client information.
        transactions_df (DataFrame): DataFrame containing transaction information.

    Returns:
        dict: Dictionary containing the best new clients and their combined similarity scores.
    """
    filtered_clients_df = filter_client_df(clients_df, transactions_df)

    all_closest_clients = []

    for client_id in client_id_list:
        closest_clients = get_closest_clients(client_id, filtered_clients_df)
        all_closest_clients.append(closest_clients)

    best_new_clients = {}
    for closest_clients in all_closest_clients:
        for client, score in closest_clients.items():
            if client in best_new_clients:
                best_new_clients[client] += score
            else:
                best_new_clients[client] = score

    best_new_clients = dict(
        sorted(best_new_clients.items(), key=lambda item: item[1], reverse=True)
    )

    return best_new_clients


if __name__ == "__main__":
    transactions_df = pd.read_csv("transactions.csv")
    clients_df = pd.read_csv("clients.csv")

    client_id_list = ["c39553611", "c43822182", "c26802244", "c87453410", "c06149453"]
    best_new_clients = generate_best_new_clients(
        client_id_list, clients_df, transactions_df
    )
