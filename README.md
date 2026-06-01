

## Overview

This project implements a minimal MLOps-style batch processing pipeline in Python.

The application:

* Loads configuration from a YAML file
* Validates input data and configuration
* Computes a rolling mean on the `close` price
* Generates binary trading signals
* Produces structured metrics in JSON format
* Creates detailed execution logs
* Runs locally and inside Docker

The solution emphasizes:

* **Reproducibility** through configuration and fixed random seed
* **Observability** through structured metrics and logging
* **Deployment Readiness** through Docker support

---

## Project Structure

```text
mlops-task/
│
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
├── metrics.json
├── run.log
└── .gitignore
```

---

## Configuration

`config.yaml`

```yaml
seed: 42
window: 5
version: "v1"
```

---

## Processing Workflow

### 1. Configuration Validation

The application validates:

* `seed`
* `window`
* `version`

and initializes NumPy's random seed for deterministic execution.

### 2. Dataset Validation

The application checks for:

* Missing input file
* Invalid CSV format
* Empty dataset
* Missing `close` column

### 3. Rolling Mean Calculation

Rolling mean is computed using the configured window size.

```python
rolling_mean = close.rolling(window=5).mean()
```

### 4. Signal Generation

Signal logic:

```python
signal = 1 if close > rolling_mean else 0
```

Rows without sufficient history for the rolling window are excluded from signal-rate calculations.

### 5. Metrics Generation

The application computes:

* Rows Processed
* Signal Rate
* Runtime Latency (ms)

---

## Local Setup

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Local Execution

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Docker Build

```bash
docker build -t mlops-task .
```

---

## Docker Run

```bash
docker run --rm mlops-task
```

---

## Example Output

### metrics.json

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 78,
  "seed": 42,
  "status": "success"
}
```

---

## Logging

Execution details are written to:

```text
run.log
```

Example log entries:

```text
Job started
Config loaded and validated
Rows loaded: 10000
Computing rolling mean
Generating signals
Metrics Summary
Job completed successfully
```

---

## Error Handling

The application gracefully handles:

* Missing input files
* Invalid CSV files
* Empty datasets
* Missing required columns
* Invalid configuration structures

Even in failure scenarios, a valid `metrics.json` file is generated:

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of what went wrong"
}
```

---

## Technologies Used

* Python 3
* Pandas
* NumPy
* PyYAML
* Docker
* Python Logging

---

## Author

Technical Assessment Submission for the ML/MLOps Engineering Internship.
