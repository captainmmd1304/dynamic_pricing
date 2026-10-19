"""Demand aggregation and forecasting."""

from __future__ import annotations

import math


class DemandForecaster:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None
        self.columns = None
        self.fallback = {}
        self.global_mean = 0.0
        self.metrics = {}

    def fit(self, transactions):
        import pandas as pd
        data = transactions.copy()
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        data = data.dropna(subset=["date"])
        data["month"] = data["date"].dt.month.astype(int)
        data["year"] = data["date"].dt.year.astype(int)
        grouped = data.groupby(["product", "city", "year", "month"], as_index=False)["quantity"].sum()
        self.global_mean = float(grouped["quantity"].mean()) if len(grouped) else 0.0
        self.fallback = grouped.groupby(["product", "city"])["quantity"].mean().to_dict()
        if len(grouped) < 4:
            return self
        try:
            from sklearn.compose import ColumnTransformer
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_squared_error
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import OneHotEncoder
            x = grouped[["product", "city", "year", "month"]]
            y = grouped["quantity"]
            categorical = ["product", "city"]
            preprocess = ColumnTransformer([( "categorical", OneHotEncoder(handle_unknown="ignore"), categorical)], remainder="passthrough")
            self.model = __import__("sklearn.pipeline", fromlist=["Pipeline"]).Pipeline([
                ("preprocess", preprocess),
                ("model", RandomForestRegressor(n_estimators=150, random_state=self.random_state, min_samples_leaf=1, n_jobs=-1)),
            ])
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=self.random_state)
            self.model.fit(x_train, y_train)
            self.metrics["mse"] = float(mean_squared_error(y_test, self.model.predict(x_test)))
        except Exception:
            self.model = None
        return self

    def predict(self, product: str, city: str, date) -> float:
        import pandas as pd
        dt = pd.to_datetime(date)
        if self.model is not None:
            value = self.model.predict(pd.DataFrame([{"product": product, "city": city, "year": dt.year, "month": dt.month}]))[0]
            return max(0.0, float(value))
        return max(0.0, float(self.fallback.get((product, city), self.global_mean)))
