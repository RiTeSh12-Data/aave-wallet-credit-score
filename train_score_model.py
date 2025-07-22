# train_score_model.py

import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from joblib import dump
from tqdm import tqdm

# Load JSON
with open("user-wallet-transactions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Parse `actionData` dict into separate columns
action_df = pd.json_normalize(df["actionData"])
df = pd.concat([df.drop(columns=["actionData"]), action_df], axis=1)

# Convert numeric columns
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["assetPriceUSD"] = pd.to_numeric(df["assetPriceUSD"], errors="coerce")
df["amount_usd"] = df["amount"] * df["assetPriceUSD"]

# Extract date for active days calculation
df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
df["date"] = df["datetime"].dt.date

# Compute wallet-level features
grouped = df.groupby("userWallet")

features = []

for wallet, group in tqdm(grouped):
    d = {}
    d["userWallet"] = wallet
    d["num_transactions"] = len(group)
    d["num_deposits"] = (group["action"] == "deposit").sum()
    d["num_redeems"] = (group["action"] == "redeemunderlying").sum()
    d["num_borrows"] = (group["action"] == "borrow").sum()
    d["num_repays"] = (group["action"] == "repay").sum()
    d["num_liquidations"] = (group["action"] == "liquidationcall").sum()
    d["total_deposited_usd"] = group.loc[group["action"] == "deposit", "amount_usd"].sum()
    d["total_borrowed_usd"] = group.loc[group["action"] == "borrow", "amount_usd"].sum()
    d["total_repaid_usd"] = group.loc[group["action"] == "repay", "amount_usd"].sum()
    d["num_unique_assets"] = group["assetSymbol"].nunique()
    d["active_days"] = group["date"].nunique()
    features.append(d)

wallet_features = pd.DataFrame(features).set_index("userWallet")

# Derived metrics
wallet_features["repay_ratio"] = wallet_features["total_repaid_usd"] / wallet_features["total_borrowed_usd"].replace(0, np.nan)
wallet_features["borrow_deposit_ratio"] = wallet_features["total_borrowed_usd"] / wallet_features["total_deposited_usd"].replace(0, np.nan)
wallet_features["redeem_deposit_ratio"] = wallet_features["num_redeems"] / wallet_features["num_deposits"].replace(0, np.nan)
wallet_features["tx_per_day"] = wallet_features["num_transactions"] / wallet_features["active_days"].replace(0, np.nan)

# Replace inf/nan with zeros
wallet_features.replace([np.inf, -np.inf], np.nan, inplace=True)
wallet_features.fillna(0, inplace=True)

# Save features
wallet_features.to_csv("wallet_features.csv")

# ------------------------------
# Normalize & Score
# ------------------------------
features_to_use = [
    "repay_ratio",
    "borrow_deposit_ratio",
    "redeem_deposit_ratio",
    "tx_per_day",
    "num_transactions",
    "num_unique_assets",
    "active_days"
]

scaler = MinMaxScaler()
normalized = pd.DataFrame(
    scaler.fit_transform(wallet_features[features_to_use]),
    columns=features_to_use,
    index=wallet_features.index
)

# Save scaler
dump(scaler, "scaler.pkl")

# Scoring formula (weighted)
wallet_features["score"] = (
    normalized["repay_ratio"] * 0.3 +
    (1 - normalized["redeem_deposit_ratio"]) * 0.2 +
    (1 - normalized["borrow_deposit_ratio"]) * 0.2 +
    normalized["tx_per_day"] * 0.1 +
    normalized["num_transactions"] * 0.1 +
    normalized["active_days"] * 0.05 +
    normalized["num_unique_assets"] * 0.05
) * 1000

wallet_features["score"] = wallet_features["score"].round().astype(int)

# Save scores
wallet_features[["score"]].to_csv("wallet_scores.csv")

print("✅ Training complete. Scores saved to `wallet_scores.csv`, scaler saved as `scaler.pkl`.")
