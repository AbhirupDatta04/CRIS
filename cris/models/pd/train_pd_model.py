"""
train_pd_model.py
Built an end-to-end credit risk pipeline where transactional data is transformed into behavioural features and used to train a baseline PD model. I used logistic regression for explainability, validated the model using ROC-AUC and KS, and ensured the risk drivers aligned with business intuition.
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
from default_event_simulator import generate_observed_default_flag

df = pd.read_parquet("/workspaces/CRIS/cris/datalake/models/pd_training_dataset")
df=generate_observed_default_flag(df)
print(df.head())
print(df.columns)

# Define features (X) and target (y)
feature_cols = [
    "spend_per_txn_30d",
    "txn_count_30d",
    "recency_days_is_inactive_30d",
    "behavioral_stress_flag"
]

X = df[feature_cols]
y = df["observed_default_flag"] # Target variable wrong.Seems fraud risk rather than default risk.


model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# Inspect coefficients-> underscores after the fitting of the model and/after training as per convention
coef_df = pd.DataFrame({
    "feature": feature_cols,
    "coefficient": model.coef_[0] #this is a list of math weights the model learned:
})

print("\nPD Model Coefficients:")
print(coef_df)

print("\nIntercept:", model.intercept_[0])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3, #keeping 30% of data for testing and now use 70% for training
    random_state=42, #Shuffle the deck the exact same way every time we run this code." (Ensures reproducibility).
    #When you set random_state=42, your code will produce the exact same random split of data or initializations every time it runs.
    #Consistency: It's crucial for debugging, sharing results, and comparing models
    
    stratify=y #It ensures the Test Set has the same percentage of Defaults (1s) as the Training Set. If you have very few defaults, this prevents the Test Set from having zero defaults by accident.

)
#Retraining and Predicting

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict probabilities (PD scores)
y_pred_proba = model.predict_proba(X_test)[:, 1] #Syntax: "Slice the data." "Take all rows (every customer)." "Take only column index 1." (Remember, computers count 0, 1). Column 0 is "Probability of Good", Column 1 is "Probability of Default."


#Grading the Model (AUC) Area under curve
auc = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC: {auc:.3f}") #3 decimal places

# KS statistic
# This block calculates the "Kolmogorov-Smirnov" stat, which measures how well the model separates Good customers from Bad customers.
df_eval = pd.DataFrame({
    "y_true": y_test,
    "y_score": y_pred_proba
})

# 1. Bucket the scores
df_eval["bucket"] = pd.qcut(df_eval["y_score"], 10, duplicates="drop") # Create 10 equal-sized buckets based on predicted scores Quantile Cut". Sorts all customers by their risk score and chops them into 10 equal-sized buckets (Deciles). Bucket 10 has the riskiest people; Bucket 1 has the safest.
#binning

# Sort by score descending (highest risk first)
df_eval = df_eval.sort_values("y_score", ascending=False)

# Total counts
total_defaults = (df_eval["y_true"] == 1).sum()
total_non_defaults = (df_eval["y_true"] == 0).sum()

# Cumulative distributions
df_eval["cum_defaults"] = (df_eval["y_true"] == 1).cumsum() / total_defaults
df_eval["cum_non_defaults"] = (df_eval["y_true"] == 0).cumsum() / total_non_defaults

# KS
ks = (df_eval["cum_defaults"] - df_eval["cum_non_defaults"]).abs().max()

print(f"KS Statistic: {ks:.3f}")
