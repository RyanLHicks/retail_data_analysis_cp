# 🛒 Retail Pulse: Vendor Control Tower



### *AI-Assisted Supply Chain Analytics Platform*



!\[Python](https://img.shields.io/badge/Python-3.10%2B-blue) !\[Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red) !\[SQLite](https://img.shields.io/badge/Data-SQLite-green) !\[Status](https://img.shields.io/badge/Status-Prototype-orange)



## 📄 Executive Summary

**Retail Pulse** is a decision-support system designed for CPG vendors (e.g., Kenvue, Unilever) operating in large-scale retail environments (e.g., Walmart, Target). 



Unlike static Excel reports, this application provides a live "Control Tower" view of supply chain health. It automates the detection of \*\*Phantom Inventory\*\* (stock that exists in the system but isn't selling) and includes a \*\*Scenario Planning Engine\*\* to model the financial impact of price promotions before they are launched.



---



## 🚀 Key Technical Features



### 1. Automated ETL Pipeline 🔄

**Data Ingestion:** Custom Python scripts (`etl\_pipeline.py`) ingest raw Point-of-Sale (POS) and Inventory CSV files.

**Data Warehouse:** Structuring data into a **SQLite** relational database with indexed tables for efficient querying.

**Resiliency:** Built-in logic to handle data freshness latency, ensuring only "Last 30 Days" data drives the dashboard.



### 2. Scenario Planning Engine 🔮

**"What-If" Analysis:** Interactive tool allowing Category Managers to simulate price cuts.

**Elasticity Modeling:** Calculates projected Revenue by balancing **Price Discount %** against **Volume Uplift %**.

**Real-Time Visualization:** Streamlit widgets provide instant visual feedback (Green/Red indicators) on Net Revenue Impact.



### 3. Risk \& Anomaly Detection 🛡️

**Phantom Inventory Algorithm:** SQL logic that flags stores/SKUs with `Inventory > 10` but `Sales (7-day) = 0`.

**Defensive Coding:** Python logic implements null-handling to prevent dashboard crashes when SQL queries return empty datasets.



---



## 🤖 The AI-Agentic Workflow

This project was developed using an **"Agent-in-the-Loop"** methodology, demonstrating how AI can accelerate software development while maintaining human architectural oversight.



***Human Role (Lead Architect):** Defined the business requirements (OTIF, WOS), debugged logic errors (such as data freshness bugs), and designed the UI/UX.

***AI Agent Role (Code Puppy):** Executed boilerplate code generation, optimized SQL syntax, and assisted in refactoring Python scripts for error handling.

***Outcome:** Reduced development lifecycle by ~60% compared to traditional coding methods.



---



## 🛠️ Installation \& Usage



**Prerequisites:** Python 3.8+



1. **Clone the Repository**

&nbsp;   ```bash

&nbsp;   git clone \[https://github.com/YOUR\_USERNAME/retail-pulse-dashboard.git](https://github.com/YOUR\_USERNAME/retail-pulse-dashboard.git)

&nbsp;   cd retail-pulse-dashboard

&nbsp;   ```



2. **Install Dependencies**

&nbsp;   ```bash

&nbsp;   pip install pandas streamlit faker

&nbsp;   ```



3.  **Initialize Data & Database**

&nbsp;   ```bash

&nbsp;   # Generate fresh mock data (Last 30 Days)

&nbsp;   python src/generate\_data.py

&nbsp;   

&nbsp;   # Load data into SQLite

&nbsp;   python src/etl\_pipeline.py

&nbsp;   ```



4.  **Launch the Dashboard**

&nbsp;   ```bash

&nbsp;   streamlit run src/dashboard.py

&nbsp;   ```



---



## 📊 Sample SQL Logic

*Snippet of the logic used to detect "Phantom Inventory":*



```sql

SELECT 

&nbsp;   s.store\_id, 

&nbsp;   p.product\_name, 

&nbsp;   i.units\_on\_hand 

FROM inventory i

JOIN sales\_summary s ON i.store\_id = s.store\_id

WHERE i.units\_on\_hand > 10 

AND s.total\_units\_sold\_7\_days = 0;


