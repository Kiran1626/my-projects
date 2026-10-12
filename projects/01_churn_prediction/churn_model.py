"""Customer churn prediction: cleaning, EDA, model training and evaluation."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE = Path(__file__).parent
DATA = BASE / "data" / "customer_churn.csv"
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)
SEED = 42

# 1. Load and clean -----------------------------------------------------------
df = pd.read_csv(DATA)
print("Raw shape:", df.shape)

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")  # blanks -> NaN
missing = df.isna().sum()
print("Missing values before cleaning:\n", missing[missing > 0])

df["MonthlyCharges"] = df["MonthlyCharges"].fillna(df["MonthlyCharges"].median())
df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])
df = df.drop(columns=["customerID"]).drop_duplicates()
df["Churn"] = (df["Churn"] == "Yes").astype(int)
print("Clean shape:", df.shape, "| churn rate:", round(df["Churn"].mean(), 3))

# 2. EDA ---------------------------------------------------------------------
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
sns.barplot(data=df, x="Contract", y="Churn", ax=ax[0], errorbar=None, color="#1F3864")
ax[0].set_title("Churn rate by contract"); ax[0].set_ylabel("Churn rate")
sns.histplot(data=df, x="tenure", hue="Churn", bins=30, ax=ax[1], multiple="stack")
ax[1].set_title("Tenure distribution by churn")
sns.boxplot(data=df, x="Churn", y="MonthlyCharges", ax=ax[2], color="#8FAADC")
ax[2].set_title("Monthly charges vs churn")
plt.tight_layout(); plt.savefig(OUT / "eda_churn_drivers.png", dpi=130); plt.close()

# 3. Preprocess + split ------------------------------------------------------
X, y = df.drop(columns="Churn"), df["Churn"]
num_cols = X.select_dtypes(include="number").columns.tolist()
cat_cols = X.select_dtypes(exclude="number").columns.tolist()
pre = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=SEED)

# 4. Train and compare -------------------------------------------------------
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=SEED),
    "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                            random_state=SEED, n_jobs=-1),
}
results, fitted = {}, {}
for name, clf in models.items():
    pipe = Pipeline([("prep", pre), ("model", clf)]).fit(X_train, y_train)
    pred, proba = pipe.predict(X_test), pipe.predict_proba(X_test)[:, 1]
    results[name] = {
        "accuracy": round(accuracy_score(y_test, pred), 4),
        "precision": round(precision_score(y_test, pred), 4),
        "recall": round(recall_score(y_test, pred), 4),
        "f1": round(f1_score(y_test, pred), 4),
        "roc_auc": round(roc_auc_score(y_test, proba), 4),
    }
    fitted[name] = (pipe, pred)
    print(f"\n=== {name} ===")
    print(classification_report(y_test, pred, target_names=["Stayed", "Churned"]))

best = max(results, key=lambda k: results[k]["roc_auc"])
print("Best model by ROC-AUC:", best)
(OUT / "metrics.json").write_text(json.dumps({"results": results, "best_model": best}, indent=2))

# 5. Confusion matrix + feature importance for the best model -----------------
pipe, pred = fitted[best]
cm = confusion_matrix(y_test, pred)
plt.figure(figsize=(4.5, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
            xticklabels=["Stayed", "Churned"], yticklabels=["Stayed", "Churned"])
plt.title(f"Confusion matrix – {best}"); plt.xlabel("Predicted"); plt.ylabel("Actual")
plt.tight_layout(); plt.savefig(OUT / "confusion_matrix.png", dpi=130); plt.close()

rf_pipe = fitted["Random Forest"][0]
names = rf_pipe.named_steps["prep"].get_feature_names_out()
imp = pd.Series(rf_pipe.named_steps["model"].feature_importances_, index=names).nlargest(10)
plt.figure(figsize=(7, 4.5))
imp[::-1].plot(kind="barh", color="#1F3864")
plt.title("Top 10 features – Random Forest"); plt.tight_layout()
plt.savefig(OUT / "feature_importance.png", dpi=130); plt.close()
print("\nSaved charts and metrics to", OUT)
