# AEF (AI Event Finder) Benchmark

This project provides a collection of tools to evaluate various AI models based on their
ability to identify events within a specific time range and geographic area. The goal is to accurately measure how well
the models can recognize real events compared to a reference dataset, analyzing their quality and accuracy.

## Getting Started

1. **Install [uv](https://docs.astral.sh/uv/getting-started/installation/#pypi)**:
   uv is used to manage the virtual environment and necessary packages.

2. **Install necessary packages from `requirements.txt`**

   ```bash
   uv pip install -r requirements.txt
   ```

3. **Environment Setup**: Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

4. Insert all the required API keys for the services used (e.g., LocationIQ and AI model APIs) into the `.env` file.

### Generating the Events Dataset using PredictHQ

Create a dataset of real events using the dedicated script by specifying latitude,
longitude, date range, and
distance from an address:

```bash
uv run python generate_dataset.py \
    --lat 41.902782 \
    --lon 12.496366 \
    --start 2025-01-01 \
    --end 2025-12-31 \
    --distance 50
```

### Evaluating AI Models

Run the evaluation to compare the events found by the AI models with those in the generated
dataset:

```bash
uv run python evaluate_models.py \
    --path "path/to/dataset.csv" \
    --address "address-to-search-events" \
    --start 2025-01-01 \
    --end 2025-12-31 \
    --distance 50
```

The evaluation results include the number of events matched with the dataset, the events identified by the models but
not present in the dataset, and corresponding quality scores. This data is saved for further comparative analysis
between models.

### Evaluation Dashboard

If you want to compare multiple exports, you can launch the dashboard via the following command:

```bash
uv run streamlit run dashboard.py
```
