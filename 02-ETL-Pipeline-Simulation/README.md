ETL Pipeline Simulation

This project is a simple ETL (Extract, Transform, Load) pipeline.

## Objective
To extract data from a raw CSV file, perform transformations in Python, and load the cleaned data into a SQLite database.

## Process
* **Extract:** Read the `Superstore.csv` file into a pandas DataFrame.
* **Transform:**
    * Cleaned all column names (e.g., `Order ID` -> `order_id`).
    * Fixed mixed-format date columns (`order_date`, `ship_date`) using `pd.to_datetime`.
    * Handled missing `postal_code` data by filling nulls and converting the column to a string.
* **Load:** Loaded the final, clean DataFrame into a new table named `orders` in a SQLite database (`superstore.db`).

## Tech Stack
* **Python**
* **Pandas** (for Extract and Transform)
* **SQLite** (for Load)