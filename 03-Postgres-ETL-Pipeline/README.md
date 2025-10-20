Automated Sales Analytics Pipeline

This project automates the ETL process for the Superstore dataset using Apache Airflow.

## Objective
To extract data from a CSV, transform it using Python/Pandas, load it into a PostgreSQL database, and orchestrate the pipeline using Airflow.

## Process
1.  **ETL Script (`etl_to_postgres.py`):** Reads `Superstore.csv`, cleans column names, fixes date formats, handles missing postal codes, and loads the data into the `orders` table in the `sales_db` PostgreSQL database using SQLAlchemy.
2.  **Airflow DAG (`sales_etl_dag.py`):** Defines a simple pipeline with one task that executes the `etl_to_postgres.py` script using a `BashOperator`. The DAG is scheduled to run daily.
3.  **Setup:** Requires PostgreSQL running on the host machine (Windows) configured to accept connections from WSL, and Airflow running within WSL.

## Tech Stack
* Python
* Pandas
* SQLAlchemy
* Psycopg2 (Postgres Driver)
* PostgreSQL (Database)
* Apache Airflow (Orchestrator)
* WSL2 (Linux Environment)

## Local Setup Notes (WSL <-> Windows Postgres)
* PostgreSQL must be configured (`postgresql.conf`) to listen on all IPs (`listen_addresses = '*'`).
* PostgreSQL access control (`pg_hba.conf`) must allow connections from the specific WSL IP address.
* Windows Firewall must have an inbound rule allowing connections to `postgres.exe` or TCP port `5432` from public/private networks.
* The Python script needs to use the host machine's IP address (found via `ip route | grep default | awk '{print $3}'` in WSL) in the database connection string, not `localhost`.