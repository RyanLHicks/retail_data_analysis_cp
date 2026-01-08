
import pandas as pd
import sqlalchemy
import os

def run_etl_star_schema():
    # Define the base directory for the project dynamically
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, "data")
    
    # Define database path
    database_path = os.path.join(base_dir, "retail.db")

    # Create a SQLAlchemy engine to connect to the SQLite database
    engine = sqlalchemy.create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})

    print(f"Connecting to database: {database_path}")

    try:
        with engine.connect() as connection:
            # Drop old tables/views if they exist
            print("Dropping old tables and views...")
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS fact_inventory;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS fact_sales;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS dim_product;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS dim_store;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS sales;")) # Old tables
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS inventory;")) # Old tables
            connection.execute(sqlalchemy.text("DROP VIEW IF EXISTS daily_store_performance;")) # Old view
            connection.commit()
            print("Old tables and views dropped.")

            # --- 1. Create Dimension Tables with Schema and Constraints ---

            # dim_store
            print("Creating dim_store table...")
            connection.execute(sqlalchemy.text('''
                CREATE TABLE IF NOT EXISTS dim_store (
                    store_id INTEGER PRIMARY KEY,
                    city TEXT,
                    state TEXT,
                    manager_name TEXT,
                    square_footage INTEGER
                );
            '''))
            connection.commit()
            print("dim_store table created.")

            # dim_product
            print("Creating dim_product table...")
            connection.execute(sqlalchemy.text('''
                CREATE TABLE IF NOT EXISTS dim_product (
                    product_id INTEGER PRIMARY KEY,
                    product_name TEXT,
                    category TEXT,
                    brand TEXT,
                    supplier_id INTEGER,
                    unit_cost REAL
                );
            '''))
            connection.commit()
            print("dim_product table created.")

            # --- 2. Create Fact Tables with Schema and Constraints ---

            # fact_sales
            print("Creating fact_sales table...")
            connection.execute(sqlalchemy.text('''
                CREATE TABLE IF NOT EXISTS fact_sales (
                    transaction_id INTEGER PRIMARY KEY,
                    date TEXT,
                    store_id INTEGER,
                    product_id INTEGER,
                    units_sold INTEGER,
                    sales_amount REAL,
                    FOREIGN KEY (store_id) REFERENCES dim_store(store_id),
                    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
                );
            '''))
            connection.commit()
            print("fact_sales table created.")

            # fact_inventory
            print("Creating fact_inventory table...")
            # Combined primary key for fact_inventory since it's a snapshot fact
            connection.execute(sqlalchemy.text('''
                CREATE TABLE IF NOT EXISTS fact_inventory (
                    snapshot_date TEXT,
                    store_id INTEGER,
                    product_id INTEGER,
                    units_on_hand INTEGER,
                    PRIMARY KEY (snapshot_date, store_id, product_id),
                    FOREIGN KEY (store_id) REFERENCES dim_store(store_id),
                    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
                );
            '''))
            connection.commit()
            print("fact_inventory table created.")

            # --- 3. Load Data into Tables ---

            print("Loading data into dim_store...")
            dim_store_df = pd.read_csv(os.path.join(data_dir, 'dim_store.csv'))
            dim_store_df.to_sql('dim_store', engine, if_exists='append', index=False)
            print(f"Loaded {len(dim_store_df)} records into dim_store.")

            print("Loading data into dim_product...")
            dim_product_df = pd.read_csv(os.path.join(data_dir, 'dim_product.csv'))
            dim_product_df.to_sql('dim_product', engine, if_exists='append', index=False)
            print(f"Loaded {len(dim_product_df)} records into dim_product.")

            print("Loading data into fact_sales...")
            fact_sales_df = pd.read_csv(os.path.join(data_dir, 'fact_sales.csv'))
            fact_sales_df['date'] = pd.to_datetime(fact_sales_df['date'])
            fact_sales_df.to_sql('fact_sales', engine, if_exists='append', index=False)
            print(f"Loaded {len(fact_sales_df)} records into fact_sales.")

            print("Loading data into fact_inventory...")
            fact_inventory_df = pd.read_csv(os.path.join(data_dir, 'fact_inventory.csv'))
            fact_inventory_df['snapshot_date'] = pd.to_datetime(fact_inventory_df['snapshot_date'])
            fact_inventory_df.to_sql('fact_inventory', engine, if_exists='append', index=False)
            print(f"Loaded {len(fact_inventory_df)} records into fact_inventory.")

            # --- 4. Create Reporting View ---
            print("Creating vw_daily_sales reporting view...")
            connection.execute(sqlalchemy.text("""
                CREATE VIEW IF NOT EXISTS vw_daily_sales AS
                SELECT
                    fs.transaction_id,
                    fs.date,
                    fs.store_id,
                    ds.city,
                    ds.state,
                    ds.manager_name,
                    fs.product_id,
                    dp.product_name,
                    dp.category,
                    dp.brand,
                    fs.units_sold,
                    fs.sales_amount
                FROM
                    fact_sales AS fs
                JOIN
                    dim_store AS ds ON fs.store_id = ds.store_id
                JOIN
                    dim_product AS dp ON fs.product_id = dp.product_id;
            """))
            connection.commit()
            print("vw_daily_sales view created successfully.")

    except FileNotFoundError as e:
        print(f"Error: One of the CSV files was not found. Please ensure they are in the 'data/' directory. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\nETL process for Star Schema completed. Summary of loaded rows:")
    with engine.connect() as connection:
        num_dim_store = connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM dim_store;")).scalar()
        num_dim_product = connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM dim_product;")).scalar()
        num_fact_sales = connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM fact_sales;")).scalar()
        num_fact_inventory = connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM fact_inventory;")).scalar()

        print(f"  dim_store: {num_dim_store} rows")
        print(f"  dim_product: {num_dim_product} rows")
        print(f"  fact_sales: {num_fact_sales} rows")
        print(f"  fact_inventory: {num_fact_inventory} rows")


if __name__ == "__main__":
    run_etl_star_schema()
