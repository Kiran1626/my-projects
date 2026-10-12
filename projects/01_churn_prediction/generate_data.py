"""Generate a synthetic telecom customer dataset (7,000 rows) for the churn project.

The data is SYNTHETIC. Churn is driven by tenure, contract type, monthly charges
and tech support, plus random noise, and a few values are blanked out so that the
project has real cleaning work to do. To use real data instead, download the
"Telco Customer Churn" dataset from Kaggle and save it as data/customer_churn.csv
with the same column names.
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N = 7000

def build() -> pd.DataFrame:
    gender = RNG.choice(["Male", "Female"], N)
    senior = RNG.choice([0, 1], N, p=[0.84, 0.16])
    partner = RNG.choice(["Yes", "No"], N)
    tenure = np.clip(RNG.gamma(2.2, 14, N).astype(int), 1, 72)
    contract = RNG.choice(["Month-to-month", "One year", "Two year"], N, p=[0.55, 0.25, 0.20])
    internet = RNG.choice(["DSL", "Fiber optic", "No"], N, p=[0.35, 0.45, 0.20])
    tech_support = np.where(internet == "No", "No internet service",
                            RNG.choice(["Yes", "No"], N, p=[0.35, 0.65]))
    payment = RNG.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], N,
                         p=[0.34, 0.22, 0.22, 0.22])

    base = np.select([internet == "DSL", internet == "Fiber optic"], [45, 80], default=20)
    monthly = np.round(base + RNG.normal(0, 8, N) + senior * 3, 2).clip(18, 120)
    total = np.round(monthly * tenure + RNG.normal(0, 20, N), 2).clip(18, None)

    # Churn probability (logistic) built from realistic drivers
    z = (-0.6
         - 0.045 * tenure
         + 0.022 * (monthly - 65)
         + np.select([contract == "Month-to-month", contract == "One year"], [1.4, 0.0], default=-1.2)
         + 0.45 * (tech_support == "No")
         + 0.35 * (payment == "Electronic check")
         + 0.30 * senior
         + RNG.normal(0, 0.6, N))
    churn = (RNG.random(N) < 1 / (1 + np.exp(-z))).astype(int)

    df = pd.DataFrame({
        "customerID": [f"CUST-{i:05d}" for i in range(N)],
        "gender": gender, "SeniorCitizen": senior, "Partner": partner, "tenure": tenure,
        "Contract": contract, "InternetService": internet, "TechSupport": tech_support,
        "PaymentMethod": payment, "MonthlyCharges": monthly, "TotalCharges": total,
        "Churn": np.where(churn == 1, "Yes", "No"),
    })
    # Inject messy values so cleaning is needed
    blank_idx = RNG.choice(N, 40, replace=False)
    df["TotalCharges"] = df["TotalCharges"].astype(object)
    df.loc[blank_idx, "TotalCharges"] = " "
    df.loc[RNG.choice(N, 25, replace=False), "MonthlyCharges"] = np.nan
    return df

if __name__ == "__main__":
    out = Path(__file__).parent / "data"
    out.mkdir(exist_ok=True)
    df = build()
    df.to_csv(out / "customer_churn.csv", index=False)
    print(f"Saved {len(df)} rows -> {out / 'customer_churn.csv'}")
    print(df["Churn"].value_counts(normalize=True).round(3).to_dict())
