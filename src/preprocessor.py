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
    df = pd.merge(df_transactions, df_clients, on=merge_colname, how="left")
    df = pd.merge(df, df_actions, on=merge_colname, how="left")
    return df



