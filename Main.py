import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import hashlib
from PIL import Image
import io
import base64
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import time
from pathlib import Path

def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Page configuration must be the first Streamlit command
st.set_page_config(page_title="Financial Takeover", layout="wide")

if 'welcome_completed' not in st.session_state:
    st.session_state.welcome_completed = False

if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'financial_history' not in st.session_state:
    st.session_state.financial_history = []

if 'recent_activities' not in st.session_state:
    st.session_state.recent_activities = []

# Initialize session state for financial metrics
if 'total_balance' not in st.session_state:
    st.session_state.total_balance = 0
if 'monthly_spend' not in st.session_state:
    st.session_state.monthly_spend = 0
if 'budget_used' not in st.session_state:
    st.session_state.budget_used = 0
if 'recalled_data' not in st.session_state:
    st.session_state.recalled_data = None
if 'current_data' not in st.session_state:
    st.session_state.current_data = None

# Update financial metrics function
def update_financial_metrics():
    data = load_data()
    if not data.empty:
        st.session_state.total_balance = data["Amount"].sum()
        st.session_state.monthly_spend = data[
            pd.to_datetime(data["Date"]).dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")
        ]["Amount"].sum()
        budget = sum(BUDGET_LIMITS.values())
        st.session_state.budget_used = (st.session_state.monthly_spend / budget) * 100 if budget > 0 else 0
        st.session_state.recent_activities = data.tail(5).to_dict('records')
        st.session_state.current_data = data
    else:
        st.session_state.total_balance = 0
        st.session_state.monthly_spend = 0
        st.session_state.budget_used = 0
        st.session_state.recent_activities = []

# Recall functionality
def recall_financial_history(index):
    if 0 <= index < len(st.session_state.financial_history):
        recalled_data = pd.DataFrame(st.session_state.financial_history[index]['transactions'])
        recalled_data['Date'] = pd.to_datetime(recalled_data['Date']).dt.strftime('%Y-%m-%d')
        
        # Update all session state variables before saving
        st.session_state.current_data = recalled_data
        st.session_state.recalled_data = recalled_data
        st.session_state.total_balance = recalled_data["Amount"].sum()
        st.session_state.monthly_spend = recalled_data[
            pd.to_datetime(recalled_data["Date"]).dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")
        ]["Amount"].sum()
        budget = sum(BUDGET_LIMITS.values())
        st.session_state.budget_used = (st.session_state.monthly_spend / budget) * 100 if budget > 0 else 0
        st.session_state.recent_activities = recalled_data.tail(5).to_dict('records')
        st.session_state.force_refresh = True
        
        # Save to file
        recalled_data.to_csv("expenses.csv", index=False)
        
        # Clear all caches
        load_data.clear()
        st.cache_data.clear()
        
        return recalled_data
    return None

# Helper functions
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("expenses.csv")
        st.session_state.current_data = data  # Update session state when loading data
        return data
    except:
        return pd.DataFrame(columns=["Date", "Amount", "Category", "Receipt"])



# Custom CSS for enhanced visual appeal
st.markdown("""
    <style>
    .welcome-header {
        text-align: center;
        color: #000000;
        font-size: 3.5em;
        margin-bottom: 2em;
        animation: fadeIn 2s;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .feature-container {
        display: flex;
        justify-content: space-around;
        margin: 2em 0;
        animation: slideIn 2s;
    }
    .feature-box {
        background: rgba(0, 0, 0, 0.1);
        padding: 2em;
        border-radius: 15px;
        text-align: center;
        margin: 1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: rgba(0, 0, 0, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton > button {
        border-radius: 25px;
        transition: all 0.3s ease;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(187,134,252,0.2);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { transform: translateX(-50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .chart-container {
        border-radius: 15px;
        padding: 20px;
        background: rgba(255,255,255,0.05);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .sidebar .stButton > button {
        width: 100%;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

if not st.session_state.welcome_completed:
    set_png_as_page_bg('images/picture_2.webp')  
    st.markdown("""
    <style>
    .welcome-header {
        text-align: center;
        color: #BB86FC;
        font-size: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)


# Welcome screen
if not st.session_state.welcome_completed:
    st.markdown("""
    <style>
    .welcome-header {
        text-align: center;
        color: #BB86FC;
        font-size: 3.5em;
        margin-bottom: 2em;
        animation: fadeIn 2s;
    }
    .feature-container {
        display: flex;
        justify-content: space-around;
        margin: 2em 0;
        animation: slideIn 2s;
    }
    .feature-box {
        background: rgba(0, 0, 0, 0.1);
        padding: 2em;
        border-radius: 10px;
        text-align: center;
        margin: 1em;
        transition: transform 0.3s;
    }
    .feature-box:hover {
        transform: scale(1.05);
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideIn {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="welcome-header">Welcome to your Financial Takeover</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; font-size: 1.5em; margin-bottom: 2em;'>
        Your Journey to Financial Freedom Starts Here
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Smart Tracking", key="smart_tracking", use_container_width=True):
            st.session_state.welcome_completed = True
            st.rerun()
        st.markdown("""
        <div class='feature-box'>
            <p>Monitor your expenses with intelligent categorization and real-time insights</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        if st.button("🎯 Goal Setting", key="goal_setting", use_container_width=True):
            st.session_state.welcome_completed = True
            st.rerun()
        st.markdown("""
        <div class='feature-box'>
            <p>Set and achieve your financial goals with personalized budgeting tools</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        if st.button("📈 Visual Analytics", key="visual_analytics", use_container_width=True):
            st.session_state.welcome_completed = True
            st.rerun()
        st.markdown("""
        <div class='feature-box'>
            <p>Understand your spending patterns with beautiful, interactive visualizations</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; margin-top: 3em;'>
        <p style='font-size: 1.2em; margin-bottom: 2em;'>Ready to take control of your financial future?</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Get Started →", key="welcome_button"):
        st.session_state.welcome_completed = True
        st.rerun()
    st.stop()

# Disclaimer
if not st.session_state.disclaimer_accepted:
    st.warning("⚠️ DISCLAIMER")
    st.write("""
    Financial Takeover is a financial assistant tool, NOT a financial advisor. This application:
    - Does not provide professional financial advice
    - Should not be used as a substitute for professional financial guidance
    - Is designed for personal expense tracking and budgeting assistance only
    - Makes no guarantees about the accuracy of financial calculations or predictions
    
    Please consult with qualified financial professionals for investment advice and important financial decisions.
    """)
    if st.button("I Understand and Accept"):
        st.session_state.disclaimer_accepted = True
        st.rerun()
    st.stop()

# Theme CSS
def get_theme_css():
    return '''
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stTitle {
        color: #000000;
    }
    div[data-testid="stMetricValue"] {
        transition: color 0.3s ease;
    }
    div[data-testid="stMetricValue"].positive {
        color: #4CAF50 !important;
    }
    div[data-testid="stMetricValue"].negative {
        color: #FF5252 !important;
    }
    div.stDataFrame {
        background-color: #2D2D2D;
    }
    div.stSidebar {
        background-color: #000000;
    }
    .stButton > button {
    background-color: #000080;  /* Red color */
    color: #FFFFFF;  /* White text for better contrast */
}
    .stSelectbox > div > div {
        background-color: #2D2D2D;
    }
    .stNumberInput > div > div {
        background-color: #2D2D2D;
    }
    .stDateInput > div > div {
    background-color: #2D2D2D;
}
.stDateInput > div {
    background-color: #2D2D2D !important;
}
.stNumberInput > div {
    background-color: #2D2D2D !important;
}
.stSelectbox > div {
    background-color: #2D2D2D !important;
}
input {
    background-color: #2D2D2D !important;
    color: white !important;
}
.stSidebarNav {
    background-color: #000000 !important;
}
.stSidebarNav-item {
    background-color: #000000 !important;
    color: white !important;
}
[data-testid="stSidebarNav"] {
    background-color: #000000 !important;
}
.st-emotion-cache-16idsys {
    background-color: #000000 !important;
}
.st-emotion-cache-1cypcdb {
    background-color: #000010 !important;
}
[data-testid="stSidebar"] {
    background-color: #000010 !important;
}
[data-testid="stSidebar"] > div {
    background-color: #000010 !important;
}
.st-emotion-cache-1d391kg {
    background-color: #000010 !important;
}
.stApp > header {
    background-color: #000010 !important;
}
[data-testid="stHeader"] {
    background-color: #000010 !important;
}
.st-emotion-cache-1erivf3 {
    background-color: #000010 !important;
}
.st-emotion-cache-5rimss {
    background-color: #000010 !important;
}
.stFileUploader > div {
    background-color: #000010 !important;
}
.stFileUploader > div > div {
    background-color: #000010 !important;
}
.stFileUploader label[data-baseweb="drag-drop-files"] {
    background-color: #000010 !important;
}
/* About Project Section Styles */
    .about-project {
        background-color: #000010;  /* Dark blue background */
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .about-project h2 {
        color: #00FF7F;  /* Spring green headers */
    }
    
    .about-project p {
        color: #F0F8FF;  /* Alice blue text */
    }
    
    /* Creators Section Styles */
    .creator-card {
        background: linear-gradient(45deg, #000010, #000033);  /* Navy blue gradient */
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .creator-name {
        color: #00;  /* Gold text for names */
        font-size: 1.2em;
        font-weight: bold;
    }
    
    .creator-role {
        color: #87CEEB;  /* Sky blue text for roles */
        font-style: italic;
    }
    
        '''

st.markdown(f'<style>{get_theme_css()}</style>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    set_png_as_page_bg('images/picture_1.jpg')

# Authentication
if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username.strip() and password.strip():
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Please enter both username and password")
    st.stop()

# Budget limits
BUDGET_LIMITS = {
    "Food": 500,
    "Transport": 200,
    "Utilities": 300,
    "Entertainment": 150,
    "Shopping": 300,
    "Healthcare": 200,
    "Education": 250,
    "Housing": 1000,
    "Savings": 400,
    "Insurance": 200,
    "Subscriptions": 100,
    "Personal Care": 150,
    "Gifts": 100,
    "Travel": 300,
    "Other": 200
}

# Helper functions
@st.cache_data
def load_data():
    try:
        return pd.read_csv("expenses.csv")
    except:
        return pd.DataFrame(columns=["Date", "Amount", "Category", "Receipt"])

def validate_input(date, amount, category):
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            st.error("Amount must be positive")
            return False
        if datetime.strptime(str(date), "%Y-%m-%d") > datetime.now():
            st.error("Date cannot be in the future")
            return False
        return True
    except ValueError:
        st.error("Invalid amount format")
        return False

def check_budget_alerts(amount, category):
    if category in BUDGET_LIMITS:
        data = load_data()
        monthly_category_spend = data[
            (data["Category"] == category) & 
            (pd.to_datetime(data["Date"]).dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m"))
        ]["Amount"].sum()
        if monthly_category_spend + amount > BUDGET_LIMITS[category]:
            st.warning(f"⚠️ This expense will exceed your {category} budget limit of ${BUDGET_LIMITS[category]}!")

def generate_pdf_report(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Expense Report")
    y = 700
    for _, row in data.iterrows():
        c.drawString(100, y, f"{row['Date']} - {row['Category']}: ${row['Amount']:.2f}")
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

def clear_financial_data():
    if st.session_state.get('show_clear_confirm', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Clear Everything"):
                try:
                    # Get current data before clearing
                    current_data = load_data()
                    if not current_data.empty:
                        # Save current state to history
                        current_history = {
                            'date_cleared': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'transactions': current_data.to_dict('records')
                        }
                        if 'financial_history' not in st.session_state:
                            st.session_state.financial_history = []
                        st.session_state.financial_history.insert(0, current_history)
                        st.session_state.financial_history = st.session_state.financial_history[:5]
                    
                    # Create empty DataFrame and save
                    pd.DataFrame(columns=["Date", "Amount", "Category", "Receipt"]).to_csv("expenses.csv", index=False)
                    
                    # Reset session state
                    st.session_state.current_data = None
                    st.session_state.total_balance = 0
                    st.session_state.monthly_spend = 0
                    st.session_state.budget_used = 0
                    st.session_state.recent_activities = []
                    
                    # Clear caches
                    load_data.clear()
                    st.cache_data.clear()
                    
                    st.session_state.show_clear_confirm = False
                    st.success("All financial data has been cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing data: {str(e)}")
        with col2:
            if st.button("No, Keep My Data"):
                st.session_state.show_clear_confirm = False
                st.rerun()
    else:
        if st.button("Clear All Financial Data"):
            st.session_state.show_clear_confirm = True
            st.rerun()

def recall_financial_history(index):
    if 0 <= index < len(st.session_state.financial_history):
        return pd.DataFrame(st.session_state.financial_history[index]['transactions'])
    return None

# Sidebar navigation
st.sidebar.title('Navigation')
selected_page = st.sidebar.radio('Go to', ['Home', 'Transactions', 'Analytics', 'History', 'Settings', 'Creators'])


# Backup data
if st.sidebar.button("Backup Data"):
    data = load_data()
    st.sidebar.download_button(
        "Download Backup",
        data.to_json(),
        "expense_backup.json",
        "application/json"
    )

# Home Page (Dashboard)
if selected_page == 'Home':
    
    st.title('My Financial Dashboard')
    update_financial_metrics()
    clear_financial_data()
    
    
    
    if st.session_state.get('show_clear_confirm', False):
        st.warning("⚠️ Are you sure you want to clear all financial data? This action cannot be undone.")

        
    
    col1, col2, col3 = st.columns(3)
   # Data loading for dashboard
    if st.session_state.get('force_refresh', False):
        data = load_data()
        st.session_state.force_refresh = False
    else:
        data = (st.session_state.current_data 
            if st.session_state.current_data is not None 
            else load_data())
    total_balance = data["Amount"].sum() if not data.empty else 0
    monthly_spend = data[pd.to_datetime(data["Date"]).dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]["Amount"].sum() if not data.empty else 0
    budget = sum(BUDGET_LIMITS.values())
    remaining_budget = budget - monthly_spend
    
    with col1:
        st.markdown(
            f"""
            <div data-testid="stMetricValue" class="{'negative' if total_balance > 0 else 'positive'}">
                ${abs(total_balance):,.2f}
            </div>
            <div data-testid="stMetricLabel">Total Expenses</div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div data-testid="stMetricValue" class="{'negative' if monthly_spend > 0 else 'positive'}">
                ${monthly_spend:,.2f}
            </div>
            <div data-testid="stMetricLabel">Monthly Spend</div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        progress = min((monthly_spend / budget) * 100, 100)
        st.markdown(
            f"""
            <div data-testid="stMetricValue" class="{'negative' if remaining_budget < 0 else 'positive'}">
                {progress:.1f}%
            </div>
            <div data-testid="stMetricLabel">Budget Used</div>
            """,
            unsafe_allow_html=True
        )
    
    st.subheader("Recent Activity")
    data = st.session_state.current_data if st.session_state.current_data is not None else load_data()
    if not data.empty:
        st.dataframe(data.tail(5), use_container_width=True)
    
    st.subheader("Quick Add Expense")
    with st.form("quick_expense"):
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.01)
        category = st.selectbox("Category", list(BUDGET_LIMITS.keys()))
        receipt = st.file_uploader("Upload Receipt", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Add")
        
        if submitted:
            if validate_input(date, amount, category):
                check_budget_alerts(amount, category)
                receipt_data = None
                if receipt:
                    try:
                        receipt_data = base64.b64encode(receipt.getvalue()).decode()
                    except:
                        st.error("Error processing receipt image")
                        receipt_data = None
                
                new_expense = pd.DataFrame({
                    "Date": [date],
                    "Amount": [amount],
                    "Category": [category],
                    "Receipt": [receipt_data]
                })
                data = pd.concat([data, new_expense], ignore_index=True)
                data.to_csv("expenses.csv", index=False)
                load_data.clear()
                st.success("Expense added successfully!")
                st.rerun()


# Transactions Page
elif selected_page == 'Transactions':
    st.title('Transaction History')
    
    col1, col2 = st.columns(2)
    with col1:
        date_range = st.date_input("Date Range", [])
    with col2:
        category_filter = st.multiselect("Categories", list(BUDGET_LIMITS.keys()))
    
    data = load_data()
    if len(date_range) == 2:
        data = data[
            (pd.to_datetime(data['Date']) >= pd.to_datetime(date_range[0])) & 
            (pd.to_datetime(data['Date']) <= pd.to_datetime(date_range[1]))
        ]
    if category_filter:
        data = data[data['Category'].isin(category_filter)]
    
    if not data.empty:
        st.dataframe(data.drop('Receipt', axis=1), use_container_width=True)
        
        st.subheader("Manage Transactions")
        for idx, row in data.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
            with col1:
                st.write(f"Date: {row['Date']}")
            with col2:
                st.write(f"Amount: ${row['Amount']:.2f}")
            with col3:
                st.write(f"Category: {row['Category']}")
            with col4:
                if row['Receipt'] and isinstance(row['Receipt'], str):
                    try:
                        receipt_image = Image.open(io.BytesIO(base64.b64decode(row['Receipt'])))
                        st.image(receipt_image, width=100)
                    except:
                        st.error("Unable to load receipt image")
            with col5:
                if st.button(f"Delete", key=f"del_{idx}"):
                    full_data = load_data()
                    full_data = full_data.drop(idx)
                    full_data.to_csv("expenses.csv", index=False)
                    load_data.clear()
                    st.rerun()
    
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Export CSV", data.to_csv(), "transactions.csv")
        with col2:
            pdf = generate_pdf_report(data)
            st.download_button("Export PDF", pdf, "expense_report.pdf")


# Analytics Page
elif selected_page == 'Analytics':
    st.title('Spending Analytics')
    
    data = load_data()
    if not data.empty:
        # Add progress bar for data loading
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.01)
        progress_bar.empty()
        
        period = st.selectbox("Analysis Period", ["Monthly", "Yearly"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Spending by Category")
            fig1 = px.pie(data, values="Amount", names="Category", template="plotly_dark")
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(255,255,255,0.1)',
                    bordercolor='rgba(255,255,255,0.2)',
                    borderwidth=1
                )
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Spending Trend")
            if period == "Monthly":
                monthly_data = data.copy()
                monthly_data['Month'] = pd.to_datetime(monthly_data['Date']).dt.strftime('%Y-%m')
                monthly_data = monthly_data.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
                fig2 = px.line(monthly_data, x="Month", y="Amount", color="Category",
                              title="Monthly Spending Trend",
                              labels={"Amount": "Amount ($)", "Month": "Month"},
                              template="plotly_dark")
            else:
                yearly_data = data.copy()
                yearly_data['Year'] = pd.to_datetime(yearly_data['Date']).dt.year
                yearly_data = yearly_data.groupby(['Year', 'Category'])['Amount'].sum().reset_index()
                fig2 = px.line(yearly_data, x="Year", y="Amount", color="Category",
                              title="Yearly Spending Trend",
                              labels={"Amount": "Amount ($)", "Year": "Year"},
                              template="plotly_dark")
            
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(255,255,255,0.1)',
                    bordercolor='rgba(255,255,255,0.2)',
                    borderwidth=1
                )
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Budget vs Actual Spending")
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spending = data[pd.to_datetime(data['Date']).dt.strftime("%Y-%m") == current_month].groupby('Category')['Amount'].sum()
        
        budget_comparison = pd.DataFrame({
            'Category': BUDGET_LIMITS.keys(),
            'Budget': BUDGET_LIMITS.values(),
            'Actual': [monthly_spending.get(cat, 0) for cat in BUDGET_LIMITS.keys()]
        })
        
        fig3 = go.Figure(data=[
            go.Bar(name='Budget', x=budget_comparison['Category'], y=budget_comparison['Budget']),
            go.Bar(name='Actual', x=budget_comparison['Category'], y=budget_comparison['Actual'])
        ])
        
        fig3.update_layout(
            barmode='group',
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=0, l=0, r=0),
            showlegend=True,
            legend=dict(
                bgcolor='rgba(255,255,255,0.1)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.subheader("Top Expenses")
        st.dataframe(data.nlargest(5, "Amount").drop('Receipt', axis=1), use_container_width=True)


elif selected_page == 'History':
    st.title('Financial History')
    
    if st.session_state.financial_history:
        for idx, history in enumerate(st.session_state.financial_history):
            history_name = history.get('name', f"History from {history['date_cleared']}")
            st.subheader(f"{history_name}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Cleared on: {history['date_cleared']}")
            with col2:
                # Allow renaming existing histories
                new_name = st.text_input(f"Rename history {idx}", 
                                       value=history_name,
                                       key=f"rename_{idx}")
                if new_name != history_name:
                    st.session_state.financial_history[idx]['name'] = new_name
                    st.rerun()
                    
            history_df = pd.DataFrame(history['transactions'])
            st.dataframe(history_df.drop('Receipt', axis=1) if 'Receipt' in history_df.columns else history_df)
            st.divider()
    else:
        st.info("No financial history available yet.")

    # Update the recall section to use names
    st.subheader("Recall Previous History")
    if st.session_state.financial_history:
        history_index = st.selectbox(
            "Select history to recall",
            range(len(st.session_state.financial_history)),
            format_func=lambda x: st.session_state.financial_history[x].get('name', 
                f"History from {st.session_state.financial_history[x]['date_cleared']}")
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Selected History"):
                recalled_data = pd.DataFrame(st.session_state.financial_history[history_index]['transactions'])
                if recalled_data is not None:
                    st.success("Historical data loaded successfully!")
                    st.dataframe(recalled_data.drop('Receipt', axis=1) if 'Receipt' in recalled_data.columns else recalled_data)
        
        with col2:
            if st.button("Restore Selected History"):
                if history_index is not None and st.session_state.financial_history:
                    recalled_data = pd.DataFrame(st.session_state.financial_history[history_index]['transactions'])
            
                    # Update all metrics
                    st.session_state.total_balance = recalled_data["Amount"].sum()
                    st.session_state.monthly_spend = recalled_data[
                        pd.to_datetime(recalled_data["Date"]).dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")
                    ]["Amount"].sum()
                    budget = sum(BUDGET_LIMITS.values())
                    st.session_state.budget_used = (st.session_state.monthly_spend / budget) * 100 if budget > 0 else 0
                    st.session_state.recent_activities = recalled_data.tail(5).to_dict('records')
            
                    # Save and update current data
                    recalled_data.to_csv("expenses.csv", index=False)
                    st.session_state.current_data = recalled_data
            
                    #Clear caches and refresh
                    load_data.clear()
                    st.cache_data.clear()
                    st.rerun()


# Settings Page
elif selected_page == 'Settings':
    st.title('Settings')
    
    st.subheader("Budget Settings")
    new_budgets = {}
    for category, limit in BUDGET_LIMITS.items():
        new_budgets[category] = st.number_input(f"{category} Budget", value=limit, min_value=0)
    
    if st.button("Save Budget Settings"):
        with open('budget_limits.json', 'w') as f:
            json.dump(new_budgets, f)
        st.success("Budget settings saved!")
    
    st.subheader("Category Management")
    new_category = st.text_input("Add New Category")
    if st.button("Add Category") and new_category:
        BUDGET_LIMITS[new_category] = 0
        st.success(f"Added category: {new_category}")
        st.rerun()
    
    st.subheader("Display Settings")
    currency_options = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
    selected_currency = st.selectbox(
        "Select Currency",
        options=list(currency_options.keys()),
        format_func=lambda x: f"{x} ({currency_options[x]})"
    )
    st.session_state.currency = selected_currency
    
    st.subheader("Data Management")
    if st.button("Clear All Data"):
        if st.checkbox("I understand this will delete all my data"):
            try:
                os.remove("expenses.csv")
                load_data.clear()
                st.success("All data cleared!")
                st.rerun()
            except FileNotFoundError:
                st.warning("No data file found to clear.")

# Creators Page
elif selected_page == 'Creators':
    st.title('Meet the Creators')
    st.markdown("""
    <div style='padding: 20px; background-color: rgba(0, 0, 0, 0.1); border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color: #FFFFFF;'>About the Project</h3>
        <p>Financial Takeover is a comprehensive expense tracking and budgeting application developed using Streamlit, demonstrating advanced financial management capabilities through an intuitive web interface. Our mission is to empower users with tools that transform their financial management experience, making budget tracking and expense monitoring both accessible and efficient.
This project showcases robust features including real-time expense monitoring, multi-category budget tracking, and detailed financial analytics, all implemented with modern Python frameworks and best practices in financial software development.
The application serves diverse user needs, from individual budget management to small business expense tracking, incorporating secure data handling and interactive visualization components. Built with scalability and user experience in mind, it represents a practical solution to contemporary financial management challenges.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Team Members")
    
    team_members = [
        {"name": "Julian Hernandez", "pid": "6499226"},
        {"name": "Aiyana Estien", "pid": "6508895"},
        {"name": "Jose Aninat Brinck", "pid": "6182871"},
        {"name": "Buriel Noel", "pid": "6288675"},
        {"name": "Allyanna Payne", "pid": "6351781"},
        {"name": "Jesus Lara", "pid": "6470097"}
    ]

    # Creator 1
    st.markdown('''
        <div class="creator-card">
            <div class="creator-name">Julian Hernandez</div>
            <div class="creator-role">6499226</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Creator 2
    st.markdown('''
        <div class="creator-card">
            <div class="creator-name">Aiyana Estien</div>
            <div class="creator-role">6508895</div>
        </div>
    ''', unsafe_allow_html=True)
# Creator 1
    st.markdown('''
        <div class="creator-card">
            <div class="creator-name">Jose Aninat Brinck</div>
            <div class="creator-role">6182871</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Creator 2
    st.markdown('''
        <div class="creator-card">
            <div class="creator-name">Buriel Noel</div>
            <div class="creator-role">6288675</div>
        </div>
    ''', unsafe_allow_html=True)# Creator 1
    st.markdown('''
        <div class="creator-card">
            <div class="creator-name">Allyanna Payne</div>
            <div class="creator-role">6351781</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Creator 2
    st.markdown('''
        <div class="creator-card">
            <div class="creator-name">Jesus Lara</div>
            <div class="creator-role">6470097</div>
        </div>
    ''', unsafe_allow_html=True)


if selected_page == 'Creators':
    # Other creators page content here
    
    # Add this at the bottom of the creators page section
        st.image("images/Picture_3.png", caption="ORIGINALLY MADE BY JUJU THIS WASNT A ROBOT", use_container_width=True)
     
            