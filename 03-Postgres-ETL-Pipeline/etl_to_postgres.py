import pandas as pd
from sqlalchemy import create_engine
import sys

def run_etl_pipeline():
    try:
        # --- EXTRACT ---
        print("Extracting data from Superstore.csv...")
        # Use latin1 encoding to handle special characters
        df = pd.read_csv('Superstore.csv', encoding='latin1')

        # --- TRANSFORM ---
        print("Transforming data...")
        # 1. Clean Column Names
        df.columns = df.columns.str.replace(' ', '_').str.lower()
        df.rename(columns={'sub-category': 'subcategory'}, inplace=True)
        
        # 2. Fix Data Types (Dates)
        df['order_date'] = pd.to_datetime(df['order_date'], format='mixed')
        df['ship_date'] = pd.to_datetime(df['ship_date'], format='mixed')
        
        # 3. Handle Missing/Wrong Data (Postal Code)
        df['postal_code'] = df['postal_code'].fillna('00000')
        df['postal_code'] = df['postal_code'].astype(int).astype(str)

        # --- LOAD ---
        print("Loading data into PostgreSQL database...")
        
        # Create the database connection string (Data Source Name or DSN)
        # ** EDIT THIS LINE with your password **
        db_string = 'postgresql://postgres:khan4khalid@localhost:5432/sales_db'
        
        # Create the SQLAlchemy engine
        engine = create_engine(db_string)
        
        # Load the DataFrame into the SQL table
        # We use 'append' because we already created the table.
        # 'index=False' means we don't save the pandas index as a column.
        df.to_sql('orders', engine, if_exists='replace', index=False)

        print("\nETL Pipeline Complete: Data successfully loaded into 'orders' table in 'sales_db'.")

    except FileNotFoundError:
        print(f"Error: Superstore.csv not found. Make sure it's in the same folder.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        # This will help debug connection or data-related errors

# --- Run the pipeline ---
run_etl_pipeline()