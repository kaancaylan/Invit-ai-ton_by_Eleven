import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupShuffleSplit
from xgboost import XGBRegressor
from sklearn.metrics import root_mean_squared_error
from src.preprocessor import get_and_merge_data

df = get_and_merge_data()

as_idx = ["action_id", "client_id"]
to_drop = [
    "transaction_date",
    "action_start_date",
    "action_end_date",
    "client_is_invited",
    "transaction_id",
    "gross_amount_euro_before",
    "gross_amount_euro_after",
]
categorical_cols = [
    "action_type_label",
    "action_subcategory_label",
    "action_collection",
    "action_universe",
    "action_category_label",
    "action_channel",
    "action_label",
    "product_category",
    "product_subcategory",
    "product_style",
    "client_country",
    "client_city",
]

df = df.set_index(as_idx, drop=True)
df = df.drop(to_drop, axis=1)
df["action_duration"] = df["action_duration"].dt.total_seconds() / (60 * 60 * 24)
# Set the maximum number of categories for OneHotEncoder

max_categories = 15

# Set the threshold frequency for merging less frequent categories
threshold_frequency = 2

# Create the pipeline
pipeline = Pipeline(
    [
        (
            "preprocessor",
            ColumnTransformer(
                transformers=[
                    (
                        "cat",
                        Pipeline(
                            [
                                (
                                    "onehot",
                                    OneHotEncoder(
                                        handle_unknown="ignore",
                                        max_categories=max_categories,
                                    ),
                                ),
                            ]
                        ),
                        categorical_cols,
                    )
                ],
                remainder="passthrough",
            ),
        ),
        ("classifier", XGBRegressor()),
    ]
)

# Split the data into features and target
X = df.drop("incremental_sales", axis=1)
y = df["incremental_sales"]

# Use GroupShuffleSplit for a group-wise split
groups = df.index.get_level_values(0)
group_splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

for train_index, test_index in group_splitter.split(X, y, groups=groups):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
# Fit the pipeline on the training data
pipeline.fit(X_train, y_train)

# Predict on the test data
y_pred = pipeline.predict(X_test)

# Evaluate the model
rmse = root_mean_squared_error(y_test, y_pred)
print(f"RMSE: {rmse:.2f}")
