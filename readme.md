Aave Wallet Credit Scoring 
 What’s this project about?
This project is all about building a simple, rule-based credit scoring system for wallets interacting with Aave V2. It looks at how people behave on-chain and assigns them a score between 0 to 1000 — higher means healthier behavior!

 Why this?
Identify wallet behavior patterns.

Score wallets without any external APIs — fully offline.

Build a transparent, explainable credit scoring system anyone can understand.

How It Works :
1.  Input Data:
We start with a JSON file of Aave transactions (deposits, borrows, repays, liquidations, etc.).

2. Feature Engineering:
For every wallet, we calculate:

Total transactions

Deposits, borrows, repays, liquidations

USD amounts deposited/borrowed/repaid

Ratios like repay-to-borrow, borrow-to-deposit, etc.

Active days & asset diversity

3.  Scoring:
We normalize everything using sklearn’s MinMaxScaler.
Scoring focuses on:

 More repayments → higher score

 More liquidations → lower score

 More active days & asset diversity → higher score
Final result = Score between 0 to 1000.