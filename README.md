# AEF (AI Event Finder) Benchmark

This project provides a collection of tools to evaluate various AI models based on their
ability to identify events within a specific time range and geographic area. The goal is to accurately measure how well
the models can recognize real events compared to a reference dataset, analyzing their quality and accuracy.

## Prerequisites

- Valid API keys for:
    - [PredictHQ](https://www.predicthq.com/products/events) (for event data generation)
    - [LocationIQ](https://locationiq.com/) (for geocoding services)
    - AI model providers (OpenAI, Perplexity, etc.)

## Getting Started

1. **Install [uv](https://docs.astral.sh/uv/getting-started/installation/#pypi)**:
   uv is used to manage the virtual environment and necessary packages.

2. **Create virtual environment**:
   uv will automatically read the `.python-version` file and install the correct Python version:

   ```bash
   uv venv
   ```

3. **Install necessary packages from `requirements.txt`**

   ```bash
   uv sync
   ```

4. **Environment Setup**: Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

5. Add all required API keys for the services used (e.g., LocationIQ and AI model APIs) into the `.env` file.

## Generating the Events Dataset using PredictHQ

Create a dataset of real events using the dedicated script by specifying latitude,
longitude, date range, and
distance from an address:

```bash
uv run generate_dataset.py \
    --lat 41.902782 \
    --lon 12.496366 \
    --start 2025-01-01 \
    --end 2025-12-31 \
    --distance 50
```

### Parameters:

- `--lat`: Latitude coordinate (decimal degrees)
- `--lon`: Longitude coordinate (decimal degrees)
- `--start`: Start date in YYYY-MM-DD format
- `--end`: End date in YYYY-MM-DD format
- `--distance`: Search radius in kilometers

## Evaluating AI Models

Run the evaluation to compare the events found by the AI models with those in the generated
dataset:

```bash
uv run evaluate_models.py \
    --path "path/to/dataset.csv" \
    --address "address-to-search-events" \
    --start 2025-01-01 \
    --end 2025-12-31 \
    --distance 50
```

### Parameters:

- `--path`: Path to the reference dataset CSV file
- `--address`: Target location address for event search
- `--start`: Start date in YYYY-MM-DD format
- `--end`: End date in YYYY-MM-DD format
- `--distance`: Search radius in kilometers

The evaluation results include the number of events matched with the dataset, the events identified by the models but
not present in the dataset, and corresponding quality scores. This data is saved for further comparative analysis
between models.

### Scoring

The evaluation system uses a point-based scoring mechanism to determine whether an AI model has successfully identified
an event from the reference dataset.

#### Heuristics

- The reference dataset (PredictHQ) is always considered the ground truth
- Events are evaluated bidirectionally: dataset events are checked against AI results, and AI results are checked
  against the dataset
- **AVG Matching Score (distance > 2km)**: Calculated as the average of scores obtained for matched events, excluding
  those within 2km (which are considered certain matches)
- **AVG Non-Matching Score**: Calculated as the average of scores obtained for non-matched events

#### Scoring System

Events are evaluated using a point-based system:

- **Location within 2km**: +2 points (considered certain match)
- **Location within 5km**: +1 point
- **Date within 5 days**: +1 point

**Match Threshold:** ≥2 points required to consider an event as found.
**Priority:** Location accuracy is weighted higher than temporal accuracy.

**Evaluation Process:**

1. Check each dataset event against AI-generated events (coverage analysis)
2. Check each AI-generated event against the dataset (precision analysis)
3. Generate metrics showing:
    - Events successfully found by the AI
    - Events missed by the AI
    - Events identified by AI but not in the reference dataset

### Evaluation Dashboard

If you want to compare multiple exports, you can launch the dashboard via the following command:

```bash
uv run streamlit run dashboard.py
```
