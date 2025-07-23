
## Project Overview

This project develops a credit-like scoring model to assess the reliability and behavior of wallet addresses interacting with the Aave V2 protocol. The model processes raw transaction data and generates a score ranging from 0 to 1000 for each wallet, reflecting its financial behavior, engagement, and risk profile.

The primary objective is to differentiate responsible users from exploitative or low-quality users based solely on historical interactions with the protocol.


## Data Summary

The dataset comprises 100,000 raw transaction records, each representing a user’s action on the Aave V2 protocol, including:

* `deposit`
* `borrow`
* `repay`
* `redeemunderlying`
* `liquidationcall`

Each transaction includes metadata such as wallet address, asset amount, timestamp, asset price in USD, and action type.

---

## Feature Engineering

Wallet-level features were aggregated from transaction-level logs using grouping and summarization techniques. The following derived metrics were used as inputs to the scoring model:

| Feature                | Description                                          |
| ---------------------- | ---------------------------------------------------- |
| `repay_ratio`          | Total repaid / Total borrowed                        |
| `borrow_deposit_ratio` | Total borrowed / Total deposited                     |
| `redeem_deposit_ratio` | Number of redeems / Number of deposits               |
| `tx_per_day`           | Average number of transactions per active day        |
| `num_transactions`     | Total number of transactions made by the wallet      |
| `active_days`          | Number of unique days with activity                  |
| `num_unique_assets`    | Number of distinct assets the wallet interacted with |

All features were normalized to the \[0, 1] range using `MinMaxScaler`.



## Scoring Logic

### Weighted Formula Score

The score was calculated using a weighted combination of behavioral indicators, scaled to a range of 0–1000. Higher scores indicate more stable, responsible, and engaged users.

```python
score = (
    repay_ratio * 0.3 +
    (1 - redeem_deposit_ratio) * 0.2 +
    (1 - borrow_deposit_ratio) * 0.2 +
    tx_per_day * 0.1 +
    num_transactions * 0.1 +
    active_days * 0.05 +
    num_unique_assets * 0.05
) * 1000
```

#### Weighting Rationale

* **Repayment behavior (30%)**: Critical indicator of financial reliability.
* **Redemption and borrowing moderation (40%)**: Discourages risky or extractive behavior.
* **Engagement and diversity (30%)**: Rewards consistent and diversified protocol use.



## Real-World Scoring Insights

### Score Distribution (Based on 3497 Wallets)

| Score Range | Number of Wallets |
| ----------- | ----------------- |
| 0–200       | 1                 |
| 201–400     | 1,575             |
| 401–600     | 1,912             |
| 601–800     | 9                 |
| 801–1000    | 0                 |

The majority of wallets score between 400 and 600, suggesting moderate to average engagement and responsibility. The model currently outputs very few high scores, which may reflect conservative thresholds in the formula or a generally cautious user base.



### Statistical Summary

| Metric             | Value |
| ------------------ | ----- |
| Mean Score         | 433.7 |
| Median Score       | 407.0 |
| Min Score          | 197.0 |
| Max Score          | 712.0 |
| Standard Deviation | 48.97 |

The score distribution is left-skewed, with a clustering of users around the 400–500 range. No wallets currently achieve a perfect or near-perfect score, indicating potential room to adjust weighting or thresholds for broader score distribution.



### Top 5 High-Scoring Wallets

| Wallet Address    | Score |
| ----------------- | ----- |
| 0x04be2a942c10... | 712   |
| 0x05c9db563db8... | 642   |
| 0x02e4ac7c366c... | 633   |
| 0x05ed9694f8f1... | 619   |
| 0x049675d578af... | 615   |

These wallets show strong repayment patterns, moderate borrowing, diversified asset usage, and sustained activity across days.



### Bottom 5 Low-Scoring Wallets

| Wallet Address    | Score |
| ----------------- | ----- |
| 0x05be4b528e49... | 197   |
| 0x01977c44632e... | 227   |
| 0x03ea93102dbd... | 269   |
| 0x0102b4bf6272... | 282   |
| 0x04b12ef29de9... | 316   |

These users likely show limited interaction, low repayment activity, high withdrawal tendencies, or potential bot-like behavior.


### Current Limitations

* All features are equally normalized; sensitive behaviors might benefit from transformations (e.g., log scale).
* No temporal weighting (recent behavior is not prioritized).
* No use of external trust indicators or identity linking (e.g., verified addresses, KYC, ENS).
* High scoring wallets are rare, possibly indicating overly harsh thresholds.


## Conclusion

This scoring framework provides a scalable, explainable method to rank wallet reliability using only on-chain behavior. It is flexible, interpretable, and can be integrated into DeFi systems for credit risk management, airdrop targeting, or incentive schemes. Ongoing refinement and data feedback can improve both fairness and predictive utility over time.

