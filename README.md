# Personal Expense Tracker and Budget Manager

&lt;p align="center"&gt;
  &lt;img src="images/screenshot_1.png" alt="Dashboard Screenshot" width="100%"/&gt;
&lt;/p&gt;

## Project Overview

This Streamlit-based expense tracker and budget management application helps users monitor their spending, set budgets, and analyze their financial habits. It provides an intuitive interface for tracking expenses, generating reports, and visualizing spending patterns.

## Features

### Expense Tracking:

* Easy expense input with customizable categories
* Receipt image upload and processing
* Multiple currency support
* Transaction history with filtering options

### Budget Management:

* Monthly budget setting and tracking
* Category-wise budget allocation
* Alert system for budget thresholds
* Customizable spending categories

### Analytics and Reporting:

* Interactive spending visualizations
* Monthly and yearly comparison charts
* Category-wise expense breakdown
* Exportable reports in multiple formats (CSV, Excel, JSON)

&lt;p align="left"&gt;
  &lt;img src="images/analytics_screen.png" alt="Analytics Screenshot" width="57%"/&gt;
&lt;/p&gt;

### Additional Features:

* Dark/Light mode toggle
* Data backup and restore
* PDF report generation
* Multi-format export options

&lt;p align="left"&gt;
  &lt;img src="images/features_screen.png" alt="Features Screenshot" width="57%"/&gt;
&lt;/p&gt;

## Tech Stack

* Python: Core programming language
* Streamlit: Web interface framework
* Pandas: Data manipulation and analysis
* Plotly: Interactive visualizations
* Pillow: Image processing
* SQLite: Data storage

## Setup and Installation

### Prerequisites

* Python 3.7 or higher
* pip package manager

### Steps

1. Clone the repository:
```console
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```

2. Install dependencies:
```console
pip install -r requirements.txt
```

3. Run the application:
```console
streamlit run Main.py
```

## How to Use

### Adding Expenses

* Navigate to the "Add Expense" section
* Enter expense details (amount, category, date)
* Upload receipt image (optional)
* Submit the expense

### Viewing Reports

* Access the "Analytics" section
* Select date range for analysis
* View interactive charts and spending breakdowns
* Export reports in desired format

### Managing Budgets

* Go to "Budget Settings"
* Set monthly budgets by category
* Monitor spending against budgets
* Receive alerts when approaching limits

## Known Issues

* Receipt image processing may be slow for large files
* Some charts may not render properly in mobile view
* Export functionality limited in size for free tier

## Future Enhancements

* Mobile app development
* Cloud sync capabilities
* AI-powered expense categorization
* Multiple user accounts support

## Contributors

* Julian Hernandez: [Github](https://github.com/investinjuju)