
import pandas as pd
import random
from datetime import datetime, timedelta
import os
from faker import Faker

# Ensure data directory exists
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

def generate_star_schema_data():
    print("Generating fresh retail data for Star Schema...")
    fake = Faker()

    # --- Configuration ---
    num_stores = 50
    num_products = 50
    num_sales_transactions = 15000
    sales_days_back = 30
    inventory_days_back = 60 # To allow for some historical inventory snapshots

    end_date = datetime.now()
    start_date_sales = end_date - timedelta(days=sales_days_back)
    start_date_inventory = end_date - timedelta(days=inventory_days_back)

    # --- 1. Dimension Tables ---

    # dim_store
    print("Generating dim_store data...")
    store_data = []
    for i in range(1, num_stores + 1):
        store_data.append({
            'store_id': i,
            'city': fake.city(),
            'state': fake.state_abbr(),
            'manager_name': fake.name(),
            'square_footage': random.randint(1000, 20000)
        })
    dim_store_df = pd.DataFrame(store_data)
    dim_store_df.to_csv(os.path.join(data_dir, 'dim_store.csv'), index=False)
    print(f"SUCCESS: Generated {len(dim_store_df)} dim_store records.")

    # dim_product
    print("Generating dim_product data...")
    product_categories = ['Electronics', 'Apparel', 'Home Goods', 'Books', 'Groceries', 'Beauty', 'Sports']
    product_brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']
    product_data = []
    for i in range(1, num_products + 1):
        category = random.choice(product_categories)
        brand = random.choice(product_brands)
        unit_cost = round(random.uniform(5.0, 100.0), 2)
        product_data.append({
            'product_id': 1000 + i,
            'product_name': f"{fake.word().capitalize()} {category[:-1] if category.endswith('s') else category} Item",
            'category': category,
            'brand': brand,
            'supplier_id': random.randint(1, 10),
            'unit_cost': unit_cost
        })
    dim_product_df = pd.DataFrame(product_data)
    dim_product_df.to_csv(os.path.join(data_dir, 'dim_product.csv'), index=False)
    print(f"SUCCESS: Generated {len(dim_product_df)} dim_product records.")

    # --- 2. Fact Tables ---

    # fact_sales
    print("Generating fact_sales data...")
    sales_data = []
    all_store_ids = dim_store_df['store_id'].tolist()
    all_product_ids = dim_product_df['product_id'].tolist()

    for i in range(1, num_sales_transactions + 1):
        random_days = random.randint(0, sales_days_back)
        transaction_date = end_date - timedelta(days=random_days)
        
        units_sold = random.randint(1, 10)
        # Randomly select a product and get its unit cost for sales_amount calculation
        product_id = random.choice(all_product_ids)
        # Note: In a real scenario, you'd join with dim_product to get unit_cost.
        # For mock data generation, we'll use a simplified random price or the generated unit_cost
        # For simplicity, let's just make up a sales price slightly higher than a base cost.
        sales_price = round(random.uniform(dim_product_df[dim_product_df['product_id'] == product_id]['unit_cost'].iloc[0] * 1.1, 
                                          dim_product_df[dim_product_df['product_id'] == product_id]['unit_cost'].iloc[0] * 1.5), 2)
        sales_amount = round(units_sold * sales_price, 2)

        sales_data.append({
            'transaction_id': i,
            'date': transaction_date.strftime('%Y-%m-%d'),
            'store_id': random.choice(all_store_ids),
            'product_id': product_id,
            'units_sold': units_sold,
            'sales_amount': sales_amount
        })
    fact_sales_df = pd.DataFrame(sales_data)
    fact_sales_df.to_csv(os.path.join(data_dir, 'fact_sales.csv'), index=False)
    print(f"SUCCESS: Generated {len(fact_sales_df)} fact_sales records.")

    # fact_inventory
    print("Generating fact_inventory data...")
    inventory_data = []
    for s_id in all_store_ids:
        for p_id in all_product_ids:
            # Generate inventory snapshots for multiple historical days
            for days_ago in range(inventory_days_back + 1):
                snapshot_date = end_date - timedelta(days=days_ago)
                inventory_data.append({
                    'snapshot_date': snapshot_date.strftime('%Y-%m-%d'),
                    'store_id': s_id,
                    'product_id': p_id,
                    'units_on_hand': random.randint(0, 200)
                })
    fact_inventory_df = pd.DataFrame(inventory_data)
    fact_inventory_df.to_csv(os.path.join(data_dir, 'fact_inventory.csv'), index=False)
    print(f"SUCCESS: Generated {len(fact_inventory_df)} fact_inventory records.")

    print("Star Schema data generation completed.")

if __name__ == "__main__":
    # Replace the call to the old generate_data with the new one
    generate_star_schema_data()
