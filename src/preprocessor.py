import pandas as pd

def get_and_merge_data(data_dir: str = "data", merge_colname: str = "client_id") -> pd.DataFrame:
    """get data from filepaths and merge them together

    Args:
        data_dir (str): _description_
        merge_colname (str, optional): key column for the merge. Defaults to "client_id".

    Returns:
        pd.DataFrame: merged dataframe
    """
    df_actions = pd.read_csv(f"{data_dir}/actions.csv")
    df_clients = pd.read_csv(f"{data_dir}/clients.csv")
    df_transactions = pd.read_csv(f"{data_dir}/transactions.csv")
    df_transactions = aggregate_transactions(df_transactions)
    df = pd.merge(df_transactions, df_clients, on=merge_colname, how="left")
    df = pd.merge(df, df_actions, on=merge_colname, how="left")
    return df


def aggregate_transactions(df_transactions) -> pd.DataFrame:
    """aggregate transactions data

    Args:
        df_transactions (pd.DataFrame): transactions data

    Returns:
        pd.DataFrame: transactions data aggregated
    """
    trans_gr = df_transactions.groupby(["client_id", "transaction_date"]).agg({
    'product_quantity': 'sum',
    'gross_amount_euro':'sum',
    'product_category': [lambda x: x.mode().iloc[0], lambda x: len(x.value_counts())],
    'product_style': [lambda x: x.mode(), lambda x: len(x.value_counts())],
    })

    trans_gr.columns = ["nr_items_purchased", "money_spent", 
                        "favorite_category", "nr_categories_purchased", 
                        "favorite_style", "nr_styles_purchased"
                        ]
    return trans_gr.reset_index(drop=False)

