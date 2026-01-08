
import pandas as pd
import numpy as np
import sqlalchemy

def calculate_inventory_metrics(engine, lead_time=7, z_score=1.65):
    """
    Calculates advanced inventory metrics for each store/product combination.

    Args:
        engine: SQLAlchemy engine connected to the retail.db.
        lead_time (int): Fixed lead time in days for inventory replenishment.
        z_score (float): Z-score for the desired service level (e.g., 1.65 for 95%).

    Returns:
        pd.DataFrame: A DataFrame containing store_id, product_id,
                      current_inventory, avg_daily_sales, lead_time_demand,
                      std_dev_demand, safety_stock, and reorder_point.
    """

    # 1. Get daily sales data for the last 30 days for each product/store
    print("Fetching daily sales data...")
    sales_query = f"""
    SELECT
        date,
        store_id,
        product_id,
        SUM(units_sold) AS daily_units_sold
    FROM
        fact_sales
    WHERE
        date >= DATE('now', '-30 days')
    GROUP BY
        date, store_id, product_id
    ORDER BY
        date, store_id, product_id;
    """
    df_daily_sales = pd.read_sql(sales_query, engine)

    # Ensure all store/product combinations have a record for each day in the last 30 days
    # to correctly calculate average and standard deviation of demand, even if sales were zero.
    # This is crucial for accurate volatility measurement.
    all_dates = pd.date_range(end=pd.to_datetime('now'), periods=30, freq='D').strftime('%Y-%m-%d').tolist()
    all_store_products = df_daily_sales[['store_id', 'product_id']].drop_duplicates()

    if all_store_products.empty:
        print("No sales data found for the last 30 days. Cannot calculate inventory metrics.")
        return pd.DataFrame(columns=['store_id', 'product_id', 'current_inventory',
                                     'avg_daily_sales', 'lead_time_demand', 'std_dev_demand',
                                     'safety_stock', 'reorder_point', 'flagged_for_reorder'])

    # Create a Cartesian product of all dates and all store-product combinations
    df_master = pd.MultiIndex.from_product([all_dates, 
                                            all_store_products['store_id'].unique(), 
                                            all_store_products['product_id'].unique()], 
                                           names=['date', 'store_id', 'product_id']).to_frame(index=False)
    df_master['date'] = pd.to_datetime(df_master['date'])
    df_daily_sales['date'] = pd.to_datetime(df_daily_sales['date'])

    df_demand = pd.merge(df_master, df_daily_sales, on=['date', 'store_id', 'product_id'], how='left')
    df_demand['daily_units_sold'] = df_demand['daily_units_sold'].fillna(0) # Fill NaN for no sales days with 0
    
    # Calculate metrics per store_id, product_id
    print("Calculating average daily sales and standard deviation...")
    df_metrics = df_demand.groupby(['store_id', 'product_id']).agg(
        avg_daily_sales=('daily_units_sold', 'mean'),
        std_dev_demand=('daily_units_sold', 'std')
    ).reset_index()

    # Handle cases where std_dev_demand might be NaN (e.g., only one sales record, or all zeros)
    df_metrics['std_dev_demand'] = df_metrics['std_dev_demand'].fillna(0)

    # Lead Time Demand
    df_metrics['lead_time_demand'] = df_metrics['avg_daily_sales'] * lead_time

    # Safety Stock: Z * StdDev * sqrt(Lead Time)
    # Using .clip(lower=0) to ensure safety stock is not negative
    df_metrics['safety_stock'] = (z_score * df_metrics['std_dev_demand'] * np.sqrt(lead_time)).clip(lower=0)

    # Reorder Point: Lead Time Demand + Safety Stock
    df_metrics['reorder_point'] = df_metrics['lead_time_demand'] + df_metrics['safety_stock']
    
    # 2. Get current inventory levels (latest snapshot for each store/product)
    print("Fetching current inventory levels...")
    inventory_query = """
    SELECT
        store_id,
        product_id,
        units_on_hand AS current_inventory
    FROM
        fact_inventory
    WHERE
        snapshot_date = (SELECT MAX(snapshot_date) FROM fact_inventory)
    """
    df_current_inventory = pd.read_sql(inventory_query, engine)
    
    # Merge with calculated metrics and product names
    df_final_metrics = pd.merge(df_metrics, df_current_inventory,
                                on=['store_id', 'product_id'], how='left')

    # Fetch product names and merge them
    print("Fetching product names...")
    product_names_query = "SELECT product_id, product_name FROM dim_product;"
    df_product_names = pd.read_sql(product_names_query, engine)
    df_final_metrics = pd.merge(df_final_metrics, df_product_names, on='product_id', how='left')
    
    # Fill current_inventory with 0 for store/product combos not found in inventory (or if it's NaN after merge)
    df_final_metrics['current_inventory'] = df_final_metrics['current_inventory'].fillna(0)

    # Calculate Weeks of Supply
    # Handle cases where avg_daily_sales might be zero to avoid division by zero
    df_final_metrics['weeks_of_supply'] = np.where(
        df_final_metrics['avg_daily_sales'] > 0,
        df_final_metrics['current_inventory'] / (df_final_metrics['avg_daily_sales'] * 7),
        np.inf # If avg_daily_sales is 0, weeks of supply is infinite
    )

    # Flag for reorder
    df_final_metrics['flagged_for_reorder'] = df_final_metrics['current_inventory'] < df_final_metrics['reorder_point']

    print("Inventory metrics calculation completed.")
    return df_final_metrics


if __name__ == "__main__":
    # Example usage (assuming retail.db exists and is populated)
    # This part can be removed or adapted if a more formal test is created.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    database_path = os.path.join(base_dir, "retail.db")
    engine = sqlalchemy.create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})

    metrics_df = calculate_inventory_metrics(engine)
    if not metrics_df.empty:
        print("\nInventory Metrics Summary (first 5 rows):\n")
        print(metrics_df.head())
        print("\nProducts Flagged for Reorder (first 5 rows):\n")
        print(metrics_df[metrics_df['flagged_for_reorder']].head())
