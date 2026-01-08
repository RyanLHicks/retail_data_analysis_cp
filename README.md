
# Retail Pulse Dashboard

![Main Dashboard](pictures/Screenshot%202026-01-07%20181302.png)

##  Overview

The Retail Pulse Dashboard is a comprehensive, data-driven command center built with Python and Streamlit. It provides retail managers and analysts with a suite of powerful tools to monitor performance, optimize inventory, and make informed strategic decisions. By connecting directly to a centralized SQL database, this dashboard offers real-time insights into sales, inventory, and merchandising, bridging the gap between raw data and actionable intelligence.

This project was designed to solve common retail challenges, such as identifying dead stock, planning for promotions, ensuring planogram compliance, and forecasting future demand. It serves as a testament to the power of combining data engineering, analytics, and modern development practices to create a practical, business-oriented solution.

---

## 🚀 Features

This dashboard is organized into several strategic modules, each designed to address a specific area of retail operations.

### 📉 Liability Manager
The Liability Manager identifies "dead stock" or orphaned inventory—products that are no longer part of the active assortment but still have units on hand. It calculates the financial liability associated with this dead stock, helping managers prioritize markdowns and clear out unproductive inventory.

![Liability Manager](pictures/Animation.gif)

### 🛠️ Scenario Planner
This interactive tool allows users to simulate the financial impact of promotional events. By adjusting the price discount and expected sales uplift, managers can project the potential revenue and net impact of a promotion before committing to it. This helps in designing more effective and profitable marketing campaigns.

![Scenario Planner](pictures/Animation1.gif)

### 📦 Reset Readiness
The Reset Readiness module is crucial for managing assortment transitions. It monitors the inventory levels of new and incoming products to ensure they are adequately stocked for an upcoming modular reset. The tool flags any items that are at risk of being out-of-stock, preventing lost sales and ensuring a smooth transition.

![Reset Readiness](pictures/Animation2.gif)

### 📏 Planogram Validator
The Planogram Validator is a merchandising tool that ensures a proposed product assortment will physically fit on the shelf. It compares the total required shelf space (based on product widths and facings) against the available fixture space for a given category. This prevents costly and time-consuming errors in assortment planning.

![Planogram Validator](pictures/Animation3.gif)

### 🔮 AI Forecasting
Leveraging a machine learning model, the AI Forecasting module predicts future demand for a selected product category. It uses historical sales data to train a linear regression model and projects the next 7 days of sales, along with the expected revenue. This provides a data-driven basis for inventory replenishment and demand planning.

![AI Forecasting](pictures/Animation5.gif)

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

## 🏃‍♀️ How to Run

To run the Retail Pulse Dashboard on your local machine, please follow these steps:

**Prerequisites:**
- Python 3.8+
- Pip (Python package installer)

**1. Clone the repository:**
```bash
git clone <repository-url>
cd <repository-directory>
```

**2. Install the required packages:**
```bash
pip install -r requirements.txt
```
*(Note: You may need to create a `requirements.txt` file if one is not already present. Based on the `dashboard.py` script, the required libraries are `streamlit`, `pandas`, `sqlalchemy`, `altair`, `scikit-learn`, and `plotly`.)*

**3. Run the Streamlit application:**
```bash
streamlit run code/dashboard.py
```

The application should now be open in your web browser!
