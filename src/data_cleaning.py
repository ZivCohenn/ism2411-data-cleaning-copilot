# This script loads a messy sales CSV, cleans it, and saves a cleaned CSV.

import pandas as pd

# What: Load a CSV file and return it as a DataFrame.
# Why: Centralizing file loading makes the script easier to reuse and test.
def load_data(file_path: str):
    """Load a CSV file into a pandas DataFrame.

    Tries several common read options (different separators and encodings)
    and returns the first successful read. Raises helpful errors if file
    cannot be found or parsed.
    """
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Try read options to handle messy CSVs
    read_attempts = [
        {},
        {"sep": ";"},
        {"encoding": "latin-1"},
        {"sep": ";", "encoding": "latin-1"},
    ]

    last_exc = None
    for opts in read_attempts:
        try:
            # Copilot suggested this, I modified variable names and logic
            data = pd.read_csv(file_path, **opts)
            return data
        except Exception as e:
            last_exc = e

    # Fallback: allow skipping bad lines for extremely messy files
    try:
        data = pd.read_csv(file_path, engine="python", on_bad_lines="skip")
        return data
    except Exception as e:
        raise ValueError(f"Unable to read CSV '{file_path}': {e}. Last attempt error: {last_exc}")

# What:Standardize column names (strip spaces, lowercase, replace spaces and hyphens).
# Why:Consistent column access and avoids errors caused by formatting differences.
def clean_column_names(df):
    """Normalize DataFrame column names."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return df

# What: Remove leading or trailing whitespace from selected text columns.
# Why: No mismatched values like "Shirt" vs "Shirt ".
def strip_whitespace(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df

# What: Drop rows missing price or quantity.
# Why: These fields are critical for analysis and cannot be inferred.
def handle_missing_values(df):
    required_cols = ["price", "quantity"]
    existing_cols = [col for col in required_cols if col in df.columns]
    return df.dropna(subset=existing_cols)

# What: Remove rows with negative price or quantity.
# Why: These are data entry errors.
def remove_invalid_rows(df):
    if "price" in df.columns and "quantity" in df.columns:
        # Convert to numeric safely
        df["price"] = pd.to_numeric(df["price"], errors='coerce')
        df["quantity"] = pd.to_numeric(df["quantity"], errors='coerce')
        df = df[(df["price"] >= 0) & (df["quantity"] >= 0)]
    return df

if __name__ == "__main__":
    raw_path = "data/raw/sales_data_raw.csv"
    cleaned_path = "data/processed/sales_data_clean.csv"

    # Load and clean the data step-by-step
    df = load_data(raw_path)              # Copilot generated + modified
    df = clean_column_names(df)           # Copilot generated + modified

    # Fix column names to match cleaning functions
    df = df.rename(columns={"prodname": "product", "qty": "quantity"})

    # Remove quotes from categories
    if "category" in df.columns:
        df["category"] = df["category"].str.replace('"', '').str.strip()

    df = strip_whitespace(df, ["product", "category"])
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)

    # What: Save cleaned dataset to processed/ folder.
    # Why: Makes sure project has a reproducible output file.
    import os
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(cleaned_path, index=False)

    print("Cleaning complete — saved to", cleaned_path)
    print(df.head())
