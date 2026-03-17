"""
evaluate_forecast.py
====================
Evaluates the Prophet forecasting model against real order data from the
procurement database. Computes MAE, RMSE, and MAPE on a held-out test period.

Usage:
    python scripts/evaluate_forecast.py
    python scripts/evaluate_forecast.py --test-days 30
"""

import argparse
import math
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from prophet import Prophet

# ── Database path (mirrors backend/forecast.py) ─────────────────────────────
DB_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"
DB_NAME = str(DB_DIR / "procurement.db")

# ── Metrics ──────────────────────────────────────────────────────────────────

def mae(actual: pd.Series, predicted: pd.Series) -> float:
    """Mean Absolute Error."""
    return (actual - predicted).abs().mean()


def rmse(actual: pd.Series, predicted: pd.Series) -> float:
    """Root Mean Squared Error."""
    return math.sqrt(((actual - predicted) ** 2).mean())


def mape(actual: pd.Series, predicted: pd.Series) -> float:
    """Mean Absolute Percentage Error (skips zero actuals to avoid division by zero)."""
    mask = actual != 0
    if mask.sum() == 0:
        return float("nan")
    return ((actual[mask] - predicted[mask]).abs() / actual[mask]).mean() * 100


# ── Data Loading ─────────────────────────────────────────────────────────────

def load_daily_order_qty() -> pd.DataFrame:
    """
    Loads order data from the procurement DB and returns a daily-aggregated
    DataFrame with columns ['ds', 'y'] ready for Prophet.
    """
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT o.created_at AS order_date, o.qty
        FROM orders o
        JOIN items i ON o.item_id = i.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        raise ValueError("No orders found in the database. Cannot evaluate.")

    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
    daily = (
        df.groupby(df["order_date"].dt.date)["qty"]
        .sum()
        .reset_index()
        .rename(columns={"order_date": "ds", "qty": "y"})
    )
    daily["ds"] = pd.to_datetime(daily["ds"])
    daily = daily.sort_values("ds").reset_index(drop=True)
    return daily


# ── Evaluation ───────────────────────────────────────────────────────────────

def evaluate(test_days: int = 30) -> dict:
    """
    Fits Prophet on all data except the last `test_days` days, then predicts
    over that held-out period and computes evaluation metrics.

    Returns a dict of results suitable for printing and report inclusion.
    """
    daily = load_daily_order_qty()

    total_days = len(daily)
    min_required = test_days + 14  # need ≥14 training rows for Prophet
    if total_days < min_required:
        raise ValueError(
            f"Not enough data. Have {total_days} days; need ≥{min_required} "
            f"(test_days={test_days} + 14 minimum training rows)."
        )

    split_idx = total_days - test_days
    train_df = daily.iloc[:split_idx].copy()
    test_df = daily.iloc[split_idx:].copy()

    train_start = train_df["ds"].min().strftime("%Y-%m-%d")
    train_end = train_df["ds"].max().strftime("%Y-%m-%d")
    test_start = test_df["ds"].min().strftime("%Y-%m-%d")
    test_end = test_df["ds"].max().strftime("%Y-%m-%d")

    # Fit
    m = Prophet(daily_seasonality=False, yearly_seasonality=False)
    m.fit(train_df)

    # Predict over the test period
    forecast = m.predict(test_df[["ds"]])

    actual = test_df["y"].reset_index(drop=True)
    predicted = forecast["yhat"].clip(lower=0).reset_index(drop=True)

    results = {
        "model": "Facebook Prophet",
        "dataset_info": {
            "total_days": total_days,
            "train_period": f"{train_start} → {train_end}",
            "test_period": f"{test_start} → {test_end}",
            "train_rows": len(train_df),
            "test_rows": len(test_df),
        },
        "metrics": {
            "MAE": round(mae(actual, predicted), 4),
            "RMSE": round(rmse(actual, predicted), 4),
            "MAPE": round(mape(actual, predicted), 4),
        },
    }
    return results


# ── Report Printer ────────────────────────────────────────────────────────────

def print_report(results: dict) -> None:
    """Prints results in a structured, report-ready format."""
    sep_thick = "=" * 60
    sep_thin = "-" * 60

    print()
    print(sep_thick)
    print("  PROPHET FORECASTING MODEL — EVALUATION REPORT")
    print(sep_thick)

    ds = results["dataset_info"]
    print()
    print("  DATASET SUMMARY")
    print(sep_thin)
    print(f"  Total Days Observed  : {ds['total_days']}")
    print(f"  Training Period      : {ds['train_period']}  ({ds['train_rows']} rows)")
    print(f"  Test Period          : {ds['test_period']}  ({ds['test_rows']} rows)")
    print()

    print("  MODEL EVALUATION METRICS")
    print(sep_thin)
    m = results["metrics"]
    print(f"  {'Metric':<35} {'Value':>10}")
    print(f"  {sep_thin[2:]}")
    print(f"  {'Mean Absolute Error (MAE)':<35} {m['MAE']:>10.4f}")
    print(f"  {'Root Mean Squared Error (RMSE)':<35} {m['RMSE']:>10.4f}")
    print(f"  {'Mean Absolute Percentage Error (MAPE)':<35} {m['MAPE']:>9.2f}%")
    print()

    print("  METRIC DEFINITIONS")
    print(sep_thin)
    print("  MAE   – Average absolute difference between actual and predicted qty.")
    print("  RMSE  – Square-root of mean squared errors; penalises large deviations.")
    print("  MAPE  – Percentage error relative to actual demand (excludes zero days).")
    print()
    print(sep_thick)
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate the Prophet forecasting model on procurement order data."
    )
    parser.add_argument(
        "--test-days",
        type=int,
        default=30,
        help="Number of most-recent days to hold out as the test set (default: 30).",
    )
    args = parser.parse_args()

    try:
        results = evaluate(test_days=args.test_days)
        print_report(results)
    except ValueError as e:
        print(f"\n[ERROR] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
