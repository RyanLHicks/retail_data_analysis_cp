
# Retail Pulse Dashboard

<img width="2553" height="1259" alt="Screenshot 2026-01-07 181302" src="https://github.com/user-attachments/assets/d56c3205-8cce-4efe-9fd0-6c9160f4fdc5" />


##  Overview

The Retail Pulse Dashboard is a comprehensive, data-driven command center built with Python and Streamlit. It provides retail managers and analysts with a suite of powerful tools to monitor performance, optimize inventory, and make informed strategic decisions. By connecting directly to a centralized SQL database, this dashboard offers real-time insights into sales, inventory, and merchandising, bridging the gap between raw data and actionable intelligence.

This project was designed to solve common retail challenges, such as identifying dead stock, planning for promotions, ensuring planogram compliance, and forecasting future demand. It serves as a testament to the power of combining data engineering, analytics, and modern development practices to create a practical, business-oriented solution.

---

## 🚀 Features

This dashboard is organized into several strategic modules, each designed to address a specific area of retail operations.

### 📉 Liability Manager
The Liability Manager identifies "dead stock" or orphaned inventory—products that are no longer part of the active assortment but still have units on hand. It calculates the financial liability associated with this dead stock, helping managers prioritize markdowns and clear out unproductive inventory.

![Animation](https://github.com/user-attachments/assets/ad75327c-c8dc-4a27-84ae-009ecfba06d0)


### 🛠️ Scenario Planner
This interactive tool allows users to simulate the financial impact of promotional events. By adjusting the price discount and expected sales uplift, managers can project the potential revenue and net impact of a promotion before committing to it. This helps in designing more effective and profitable marketing campaigns.

![Animation1](https://github.com/user-attachments/assets/54e83bcf-1cd9-48fb-9917-0ee13ec706af)


### 📦 Reset Readiness
The Reset Readiness module is crucial for managing assortment transitions. It monitors the inventory levels of new and incoming products to ensure they are adequately stocked for an upcoming modular reset. The tool flags any items that are at risk of being out-of-stock, preventing lost sales and ensuring a smooth transition.

![Animation2](https://github.com/user-attachments/assets/ca205906-9cf5-46ad-ab08-b7612062c9cf)


### 📏 Planogram Validator
The Planogram Validator is a merchandising tool that ensures a proposed product assortment will physically fit on the shelf. It compares the total required shelf space (based on product widths and facings) against the available fixture space for a given category. This prevents costly and time-consuming errors in assortment planning.

![Animation3](https://github.com/user-attachments/assets/83c7e096-c174-499f-8b63-2ca9afe08b0a)


### 🔮 AI Forecasting
Leveraging a machine learning model, the AI Forecasting module predicts future demand for a selected product category. It uses historical sales data to train a linear regression model and projects the next 7 days of sales, along with the expected revenue. This provides a data-driven basis for inventory replenishment and demand planning.

![Animation5](https://github.com/user-attachments/assets/d1eba675-4e9a-46da-a8f5-db34e6631678)


---

## 🛠️ Technical Skills Showcase

This project was an opportunity to apply a diverse set of technical skills to solve real-world business problems.

### 🐍 Python
Python was the core programming language for this project. Its extensive ecosystem of libraries was instrumental in building the dashboard.
- **Streamlit:** Used to create the interactive and user-friendly web application interface.
- **Pandas:** The backbone of the data manipulation and analysis, used for cleaning, transforming, and analyzing the data from the SQL database.
- **Scikit-learn:** Employed to build the linear regression model for the AI Demand Forecasting feature.
- **SQLAlchemy:** Used to create a robust and efficient connection to the SQLite database.

### 📊 SQL
The entire dashboard is powered by a SQLite database. SQL queries were used to efficiently extract, aggregate, and filter the data needed for the various modules. This project demonstrates the ability to write clean, performant SQL queries to retrieve data from a relational database and to model data in a way that supports business analytics.

### 📈 Excel
While the dashboard itself is built in Python, the project required skills often associated with advanced Excel usage. The data was initially explored and modeled in a way that is familiar to business users who rely on Excel for their day-to-day work. The concepts of data aggregation, scenario planning, and metric calculation are all directly transferable from an advanced Excel skillset. This project essentially automates and scales the kind of analysis that is often done manually in spreadsheets.

### 💻 IDE (Integrated Development Environment)
The development of this project was done within a professional IDE (like VS Code). This allowed for efficient code writing, debugging, and version control. The use of an IDE was crucial for managing the project's structure, dependencies, and for ensuring a high standard of code quality. It demonstrates the ability to work in a modern development environment and to follow software engineering best practices.

---

## 💡 Problem Solving & Commercial Awareness

This section details specific challenges encountered during development and how they were resolved, showcasing a blend of technical problem-solving and business acumen.

### Scenario 1: Diagnosing a Data Latency Issue

**The Problem** Faced significant development issues and data misalignment. During the development of the Retail Pulse dashboard, I encountered a discrepancy where the frontend metrics showed zero despite the backend logic being correct.

**The Solution:**  After investigating, I diagnosed the issue as a data latency in the ETL pipeline. The data generation script wasn't creating records within the dashboard's 'Last 30 Days' temporal window. To fix this, I re-designed the script to enforce strict, rolling time windows, ensuring the dashboard always reflected a real-time, decision-making scenario.

### Scenario 2: Handling Unexpected Database Outputs

**The Problem:** I encountered a runtime error where a SQL aggregation was returning NULL for products with no recent sales, which subsequently crashed the dashboard.

**The Solution:** To resolve this, I implemented defensive coding logic in the Python backend. This logic cleans the database outputs by converting any NULL values to zero integers *before* they are passed to the frontend for processing, making the application more robust and resilient to intermittent data gaps.


