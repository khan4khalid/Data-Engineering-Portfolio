# Phase 2, Project 1: Automated Sales Analytics Pipeline

This project builds an automated ETL pipeline that extracts data from a CSV file, transforms it using Python/Pandas, loads it into a PostgreSQL database running on the Windows host, and orchestrates the process using Apache Airflow running in WSL2 (Ubuntu).

---

## 🎯 Objective

To create a scheduled, automated workflow that processes sales data from a CSV file (`Superstore.csv`) and loads the cleaned data into a PostgreSQL database, simulating a basic data engineering pipeline.

---

## 🛠️ Tech Stack

* **Orchestration:** Apache Airflow (running in WSL2)
* **ETL Scripting:** Python 3.12 (using Pandas for transformation, SQLAlchemy & Psycopg2 for DB connection)
* **Database:** PostgreSQL (running on Windows host)
* **Environment:** Windows 11 with WSL2 (Ubuntu)
* **Code Editor:** VS Code

---

## ⚙️ Setup Guide (Windows Host + WSL2 Client)

This setup involves configuring communication between the Linux environment (WSL2) where the ETL script and Airflow run, and the PostgreSQL database running on the Windows host.

### 1. PostgreSQL Installation (on Windows)

* Download and install PostgreSQL for Windows from the [official website](https://www.postgresql.org/download/).
* During installation, set a password for the `postgres` superuser. **Remember this password.**
* Install the accompanying pgAdmin tool.

### 2. Configure PostgreSQL for WSL Connections (on Windows)

* **Find Data Directory:** Usually `C:\Program Files\PostgreSQL\<version>\data`.
* **Edit `postgresql.conf` (as Administrator):**
    * Open Notepad **as Administrator**.
    * `File > Open...` > Change dropdown to "All Files (\*.\*)" > Navigate to the data directory > Open `postgresql.conf`.
    * Find the line `#listen_addresses = 'localhost'`.
    * Change it to `listen_addresses = '*'`.
    * Save the file.
* **Edit `pg_hba.conf` (as Administrator):**
    * Open `pg_hba.conf` using Notepad (as Admin).
    * Go to the **bottom** of the file.
    * Add a line to allow connections from your specific WSL IP address (replace `YOUR_WSL_IP_HERE`):
        ```
        # Allow connections from WSL
        host    all             all             YOUR_WSL_IP_HERE/32       scram-sha-256
        ```
        *(To find `YOUR_WSL_IP_HERE`, run `ip route | grep default | awk '{print $3}'` in your WSL terminal).*
    * Save the file.
* **Restart PostgreSQL Service:**
    * Open the **Services** app on Windows.
    * Find the `postgresql-x64-<version>` service.
    * Right-click -> **Restart**.

### 3. Configure Windows Firewall (on Windows)

* Open **"Windows Defender Firewall with Advanced Security"**.
* Click **"Inbound Rules"** -> **"New Rule..."**.
* Select **"Program"** -> Next.
* Select **"This program path:"** -> Browse to `C:\Program Files\PostgreSQL\<version>\bin\postgres.exe` -> Open -> Next.
* Select **"Allow the connection"** -> Next.
* Check all three boxes: **Domain**, **Private**, **Public** -> Next.
* Give it a name (e.g., `PostgreSQL_Program_Allow`) -> Finish.

### 4. Create Database and Table (using pgAdmin on Windows)

* Open pgAdmin and connect to your local server (using the `postgres` password).
* Right-click **Databases** -> Create -> Database -> Name: `sales_db`.
* Select `sales_db`, open the **Query Tool**.
* Paste and run the following SQL to create the `orders` table:
    ```sql
    CREATE TABLE IF NOT EXISTS orders (
        row_id INT, order_id VARCHAR(50) PRIMARY KEY, order_date DATE, ship_date DATE,
        ship_mode VARCHAR(50), customer_id VARCHAR(50), customer_name VARCHAR(100),
        segment VARCHAR(50), country VARCHAR(50), city VARCHAR(50), state VARCHAR(50),
        postal_code VARCHAR(10), region VARCHAR(50), product_id VARCHAR(50),
        category VARCHAR(50), subcategory VARCHAR(50), product_name VARCHAR(255),
        sales NUMERIC(10, 2), quantity INT, discount NUMERIC(4, 2), profit NUMERIC(10, 2)
    );
    ```

### 5. Set up ETL Project (in WSL)

* Open your WSL (Ubuntu) terminal.
* Navigate to your desired projects directory (e.g., `cd ~`).
* Create the project folder: `mkdir etl_project && cd etl_project`.
* Copy the necessary files from your Windows host:
    ```bash
    # Copy script, requirements, and data file
    cp "/mnt/c/Users/khanv/Desktop/data engineering/03-Postgres-ETL-Pipeline/etl_to_postgres.py" .
    cp "/mnt/c/Users/khanv/Desktop/data engineering/03-Postgres-ETL-Pipeline/requirements.txt" .
    cp "/mnt/c/Users/khanv/Desktop/data engineering/03-Postgres-ETL-Pipeline/Superstore.csv" .
    ```
* **Edit `etl_to_postgres.py`:**
    ```bash
    code etl_to_postgres.py
    ```
    * Update the `db_string` variable with your `postgres` password and the correct WSL host IP address found earlier:
        ```python
        # Example:
        db_string = 'postgresql://postgres:YOUR_PASSWORD@YOUR_WSL_IP_HERE:5432/sales_db'
        ```
    * Ensure `if_exists='replace'` is used in the `df.to_sql(...)` call for idempotency during testing.
    * Save the file.
* **Create and activate virtual environment:**
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```
* **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
* **Test the script:**
    ```bash
    python etl_to_postgres.py
    ```
    *(Should print "ETL Pipeline Complete...")*

### 6. Set up Airflow Project (in WSL)

* Open a **separate** WSL terminal.
* Navigate to your desired projects directory (e.g., `cd ~`).
* Create the Airflow project folder: `mkdir airflow_project && cd airflow_project`.
* **Create and activate virtual environment:**
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```
* **Install Airflow with Postgres provider:**
    ```bash
    pip install "apache-airflow[postgres]"
    ```
* **Create Airflow Home sub-directory:**
    ```bash
    mkdir airflow_home
    mkdir airflow_home/dags
    ```
* **Set `AIRFLOW_HOME` environment variable:**
    ```bash
    export AIRFLOW_HOME=$(pwd)/airflow_home
    ```
    *(Remember to run this `export` command every time you start a new terminal session for Airflow).*
* **Create the DAG file:**
    ```bash
    cd airflow_home/dags
    code sales_etl_dag.py
    ```
* **Paste the DAG definition** into `sales_etl_dag.py` (ensure `schedule` is used, not `schedule_interval`):
    ```python
    from airflow import DAG
    from airflow.operators.bash import BashOperator
    from datetime import datetime

    with DAG(
        dag_id='sales_etl_pipeline',
        start_date=datetime(2025, 10, 20),
        schedule='@daily', # Use 'schedule' not 'schedule_interval'
        catchup=False,
        description='A simple ETL pipeline for the Superstore sales data.'
    ) as dag:
        run_etl_script = BashOperator(
            task_id='run_etl_script',
            # Correct path to your etl_project and script
            bash_command='cd /home/khan/etl_project && source venv/bin/activate && python etl_to_postgres.py'
        )
        run_etl_script # Defines task order (only one task here)
    ```
* Save the DAG file.

---

## 🚀 Running the Pipeline with Airflow

1.  **Start Airflow:**
    * In your Airflow project terminal (`~/airflow_project` with `venv` active):
        ```bash
        export AIRFLOW_HOME=$(pwd)/airflow_home # Set if not already set
        airflow standalone
        ```
    * Note the auto-generated `admin` password printed in the logs.
2.  **Access Airflow UI:** Open a web browser to `http://localhost:8080`.
3.  **Log In:** Use username `admin` and the password from the logs.
4.  **Find and Unpause DAG:** Locate `sales_etl_pipeline` on the dashboard. Click the toggle switch to unpause it.
5.  **Trigger Manually (for testing):** Click the play button (▶️) -> "Trigger DAG".
6.  **Monitor:** Click the DAG name to view the Grid or Graph view and monitor the `run_etl_script` task turning green (success).

---

## ⚠️ Challenges & Solutions Encountered

* **`Connection refused` Error:** This was the main challenge. It occurred because the PostgreSQL server (Windows) was not configured to accept connections from the WSL client (Linux), or the firewall was blocking it.
    * **Solution:**
        1.  Edited `postgresql.conf` to set `listen_addresses = '*'`.
        2.  Found the correct WSL client IP using `ip route | grep default | awk '{print $3}'`.
        3.  Edited `pg_hba.conf` to add a `host` rule specifically allowing the WSL client IP.
        4.  Created a Windows Defender Firewall rule to allow connections for the `postgres.exe` program across **Public**, Private, and Domain networks.
        5.  Ensured the PostgreSQL service was restarted after config changes.
        6.  Updated the Python script's connection string to use the correct WSL host IP, not `localhost`.
* **Airflow Version Differences:** Initial commands (`airflow db init`, `airflow users create`, `schedule_interval`) were for older Airflow versions.
    * **Solution:** Used the correct newer commands: `airflow db migrate`, relied on `airflow standalone` for user creation, and used `schedule` in the DAG definition.
* **WSL File System Paths:** Remembering to use `/mnt/c/Users/...` when copying files from Windows to WSL.
* **Virtual Environments:** Ensuring the correct `venv` was active in the correct terminal for each component (ETL script vs. Airflow). Accidentally installing Airflow in the ETL venv required cleanup (`deactivate`, `rm -rf venv`, recreate venv, reinstall requirements).