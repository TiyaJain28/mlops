import argparse
import json
import logging
import time
import sys

import numpy as np
import pandas as pd
import yaml


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    return parser.parse_args()


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_config(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    required_fields = ["seed", "window", "version"]

    if not isinstance(config, dict):
        raise ValueError("Invalid config structure")

    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    return config


def load_data(input_file):
    try:
        df = pd.read_csv(input_file)

        # Handle quoted single-column CSV
        if len(df.columns) == 1:
            df = pd.read_csv(input_file, quotechar='"')
            df = df.iloc[:, 0].str.split(",", expand=True)

            df.columns = [
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume_btc",
                "volume_usd"
            ]

    except FileNotFoundError:
        raise ValueError("Input file not found")

    except Exception as e:
        raise ValueError(f"Invalid CSV format: {e}")

    if df.empty:
        raise ValueError("Input CSV is empty")

    if "close" not in df.columns:
        raise ValueError("Missing required column: close")

    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    return df


def process_data(df, window):
    logging.info("Computing rolling mean")

    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    logging.info("Generating signals")

    df["signal"] = np.where(
        df["rolling_mean"].isna(),
        np.nan,
        (df["close"] > df["rolling_mean"]).astype(int)
    )

    return df


def write_metrics(output_file, metrics):
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)


def main():
    start_time = time.time()
    args = parse_args()

    setup_logging(args.log_file)

    logging.info("Job started")

    try:
        config = load_config(args.config)

        logging.info(
            f"Config loaded and validated | "
            f"seed={config['seed']} "
            f"window={config['window']} "
            f"version={config['version']}"
        )

        np.random.seed(config["seed"])

        df = load_data(args.input)

        logging.info(f"Rows loaded: {len(df)}")

        df = process_data(df, config["window"])

        signal_rate = float(df["signal"].dropna().mean())

        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": config["version"],
            "rows_processed": len(df),
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        write_metrics(args.output, metrics)

        logging.info(f"Metrics Summary: {metrics}")
        logging.info("Job completed successfully")

        print(json.dumps(metrics, indent=2))

        sys.exit(0)

    except Exception as e:
        logging.exception("Job failed")

        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        write_metrics(args.output, error_metrics)

        print(json.dumps(error_metrics, indent=2))

        sys.exit(1)


if __name__ == "__main__":
    main()