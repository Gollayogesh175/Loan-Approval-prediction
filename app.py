import streamlit as st
import pandas as pd
import pickle as pk
import warnings
import sqlite3
import hashlib
from datetime import datetime
from fpdf import FPDF

warnings.filterwarnings('ignore')

model = pk.load(open('model.pkl','rb'))
scaler = pk.load(open('scaler.pkl','rb'))

st.set_page_config(page_title="Loan Prediction System", layout="wide")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('loan_predictions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT,
            username TEXT,
            time TEXT,
            loan_type TEXT,
            income REAL,
            loan_amount REAL,
            loan_term REAL,
            property_value REAL,
            result TEXT,
            probability REAL)''')
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                  ('admin', hash_password('admin123'), 'admin', str(datetime.now())))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('loan_predictions.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def register_user(username, password, role='user'):
    try:
        conn = sqlite3.connect('loan_predictions.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), role, str(datetime.now())))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_users():
    conn = sqlite3.connect('loan_predictions.db')
    df = pd.read_sql_query("SELECT id, username, role, created_at FROM users", conn)
    conn.close()
    return df

def delete_user(username):
    conn = sqlite3.connect('loan_predictions.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def change_password(username, new_password):
    conn = sqlite3.connect('loan_predictions.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?",
              (hash_password(new_password), username))
    conn.commit()
    conn.close()

def save_to_db(row, username):
    conn = sqlite3.connect('loan_predictions.db')
    c = conn.cursor()
    c.execute('''INSERT INTO predictions
        (prediction_id, username, time, loan_type, income, loan_amount, loan_term, property_value, result, probability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (row['Prediction ID'], username, str(row['Time']), row['Loan Type'],
         row['Income'], row['Loan Amount'], row['Loan Term'],
         row['Property Value'], row['Result'], row['Probability']))
    conn.commit()
    conn.close()

def load_from_db(username=None, role=None):
    conn = sqlite3.connect('loan_predictions.db')
    if role == 'admin':
        df = pd.read_sql_query("SELECT id, prediction_id, username, time, loan_type, income, loan_amount, loan_term, property_value, result, probability FROM predictions ORDER BY id DESC", conn)
    else:
        df = pd.read_sql_query("SELECT id, prediction_id, username, time, loan_type, income, loan_amount, loan_term, property_value, result, probability FROM predictions WHERE username = ? ORDER BY id DESC",
                               conn, params=(username,))
    conn.close()
    df.columns = ['ID', 'Prediction ID', 'Username', 'Time', 'Loan Type',
                  'Income', 'Loan Amount', 'Loan Term', 'Property Value', 'Result', 'Probability']
    return df

def delete_from_db(prediction_id):
    conn = sqlite3.connect('loan_predictions.db')
    c = conn.cursor()
    c.execute("DELETE FROM predictions WHERE prediction_id = ?", (prediction_id,))
    conn.commit()
    conn.close()

init_db()

def generate_single_pdf(row):
    file_path = f"{row['Prediction ID']}.pdf"
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Loan Prediction Report", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Prediction ID: {row['Prediction ID']}", ln=True)
    pdf.cell(0, 10, f"Result: {row['Result']}", ln=True)
    pdf.ln(3)

    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Time: {row['Time']}", ln=True)
    pdf.cell(0, 8, f"Loan Type: {row['Loan Type']}", ln=True)
    pdf.cell(0, 8, f"Income: Rs {row['Income']}", ln=True)
    pdf.cell(0, 8, f"Loan Amount: Rs {row['Loan Amount']}", ln=True)
    pdf.cell(0, 8, f"Loan Term: {row['Loan Term']} months", ln=True)
    pdf.cell(0, 8, f"Property Value: Rs {row['Property Value']}", ln=True)
    pdf.cell(0, 8, f"Probability: {row['Probability']:.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    if row['Result'] == "Approved":
        pdf.cell(0, 8, "Loan Approved!", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, "Congratulations! Your loan is approved.", ln=True)
        pdf.cell(0, 8, "Maintain good repayment history to keep credit score strong.", ln=True)
        pdf.cell(0, 8, "Ensure timely EMI payments to avoid penalties.", ln=True)
        pdf.cell(0, 8, "Loan will be disbursed within 3-5 working days.", ln=True)
        pdf.cell(0, 8, "Keep your documents ready for verification.", ln=True)
    else:
        pdf.cell(0, 8, "Loan Rejected!", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, "Possible reasons for rejection:", ln=True)
        pdf.cell(0, 8, "- Low CIBIL score (below 650)", ln=True)
        pdf.cell(0, 8, "- Insufficient income to cover loan repayment", ln=True)
        pdf.cell(0, 8, "- High number of dependents", ln=True)
        pdf.cell(0, 8, "- Unstable employment or self-employment risk", ln=True)
        pdf.cell(0, 8, "- Loan amount too high compared to income", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Tips to Improve Eligibility:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, "- Improve CIBIL score by paying bills on time", ln=True)
    pdf.cell(0, 8, "- Reduce existing debts", ln=True)
    pdf.cell(0, 8, "- Apply for a lower loan amount", ln=True)
    pdf.cell(0, 8, "- Add a co-applicant to strengthen application", ln=True)
    pdf.cell(0, 8, "- Maintain stable income for at least 6 months", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "How Your Loan Can Be Used:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, "Home Loan -> Purchase, construct, or renovate property", ln=True)
    pdf.cell(0, 8, "Car Loan -> Buy new or used vehicles", ln=True)
    pdf.cell(0, 8, "Education Loan -> Fund tuition, hostel, and study materials", ln=True)
    pdf.cell(0, 8, "Business Loan -> Expand business, buy equipment, manage cash flow", ln=True)
    pdf.cell(0, 8, "Personal Loan -> Medical emergencies, travel, or personal needs", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Loan Repayment Tips:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, "- Always pay EMI before the due date", ln=True)
    pdf.cell(0, 8, "- Avoid multiple loan applications at once", ln=True)
    pdf.cell(0, 8, "- Keep your debt-to-income ratio below 40%", ln=True)
    pdf.cell(0, 8, "- Set up auto-pay to never miss a payment", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "CIBIL Score Guide:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, "750 - 900 -> Excellent -> High approval chance", ln=True)
    pdf.cell(0, 8, "650 - 749 -> Good -> Moderate approval chance", ln=True)
    pdf.cell(0, 8, "550 - 649 -> Fair -> Low approval chance", ln=True)
    pdf.cell(0, 8, "300 - 549 -> Poor -> Very low approval chance", ln=True)

    pdf.output(file_path)
    return file_path

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "prediction_count" not in st.session_state:
    st.session_state.prediction_count = 1
if "page" not in st.session_state:
    st.session_state.page = "Home"

def set_page(page_name):
    st.session_state.page = page_name

def auth_page():
    st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🏦 Loan Prediction System</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        with tab1:
            st.markdown("### Login to your account")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[1]
                    st.session_state.role = user[3]
                    st.success(f"Welcome, {user[1]}! 👋")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        with tab2:
            st.markdown("### Create a new account")
            new_username = st.text_input("Choose Username", key="reg_user")
            new_password = st.text_input("Choose Password", type="password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            if st.button("Register", use_container_width=True):
                if not new_username or not new_password:
                    st.warning("⚠️ Please fill all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.warning("⚠️ Password must be at least 6 characters")
                else:
                    if register_user(new_username, new_password, role='user'):
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("❌ Username already exists")

def main_app():
    username = st.session_state.username
    role = st.session_state.role
    st.sidebar.title("🏦 Loan App")
    st.sidebar.markdown(f"👤 **{username}** (`{role}`)")
    st.sidebar.markdown("---")
    if st.sidebar.button("🏠 Home"):            set_page("Home")
    if st.sidebar.button("📊 Prediction"):      set_page("Prediction")
    if st.sidebar.button("📁 Reports"):         set_page("Reports")
    if st.sidebar.button("📊 Dashboard"):       set_page("Dashboard")
    if st.sidebar.button("🔑 Change Password"): set_page("ChangePassword")
    if role == 'admin':
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🛡️ Admin Panel")
        if st.sidebar.button("👥 Manage Users"): set_page("ManageUsers")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    page = st.session_state.page

    if page == "Home":
        st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🏦 Loan Prediction System</h1>", unsafe_allow_html=True)
        st.write(f"### Welcome back, {username}! 👋")
        st.image("https://images.unsplash.com/photo-1565514158740-064f34bd6cfd", use_container_width=True)

    elif page == "Prediction":
        st.markdown("<h2 style='color:#2E8B57;'>🔍 Loan Prediction</h2>", unsafe_allow_html=True)
        loan_type = st.selectbox("Select Loan Type", ["Home Loan", "Car Loan", "Personal Loan", "Business Loan"])
        col1, col2 = st.columns(2)
        with col1:
            Gender = st.selectbox('Gender', ['Male', 'Female'])
            Married = st.selectbox('Marital Status', ['Yes', 'No'])
            Dependents = st.selectbox('Dependents', ['0', '1', '2', '3+'])
            Education = st.selectbox('Education', ['Graduate', 'Not Graduate'])
            Property_Area = st.number_input('Property Value (in amount)', min_value=0)
        with col2:
            Self_Employed = st.selectbox('Self Employed', ['Yes', 'No'])
            ApplicantIncome = st.number_input('Applicant Income', min_value=0)
            LoanAmount = st.number_input('Loan Amount', min_value=0)
            Loan_Amount_Term = st.number_input('Loan Term (in months)', min_value=0)
            Credit_History = st.number_input('Credit Score (300 - 1000)', min_value=300, max_value=1000)
        Gender_e = 1 if Gender == 'Male' else 0
        Married_e = 1 if Married == 'Yes' else 0
        Dependents_e = 3 if Dependents == '3+' else int(Dependents)
        Education_e = 1 if Education == 'Graduate' else 0
        Self_Employed_e = 1 if Self_Employed == 'Yes' else 0
        Credit_History_e = 1 if Credit_History >= 700 else 0
        input_data = pd.DataFrame([[Gender_e, Married_e, Dependents_e, Education_e,
                                    Self_Employed_e, ApplicantIncome, LoanAmount,
                                    Credit_History_e, Loan_Amount_Term, Property_Area]])
        input_scaled = scaler.transform(input_data)
        if st.button("Predict Loan Status"):
            prediction = model.predict(input_scaled)
            prob = model.predict_proba(input_scaled)[0][1]
            result = "Approved" if prediction[0] == 1 else "Rejected"
            pred_id = f"PRED-{username.upper()}-{st.session_state.prediction_count}"
            st.session_state.prediction_count += 1
            if prediction[0] == 1:
                st.success(f"✅ {result} (ID: {pred_id}) | Probability: {prob:.2f}")
            else:
                st.error(f"❌ {result} (ID: {pred_id}) | Probability: {prob:.2f}")
            row = {"Prediction ID": pred_id, "Time": datetime.now(), "Loan Type": loan_type,
                   "Income": ApplicantIncome, "Loan Amount": LoanAmount,
                   "Loan Term": Loan_Amount_Term, "Property Value": Property_Area,
                   "Result": result, "Probability": prob}
            save_to_db(row, username)
            st.info("💾 Saved to Database!")

    elif page == "Reports":
        st.markdown("<h2 style='color:#2E8B57;'>📁 Prediction Reports</h2>", unsafe_allow_html=True)
        df = load_from_db(username, role)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            for i, row in df.iterrows():
                color = "#d4edda" if row['Result'] == "Approved" else "#f8d7da"
                st.markdown(f"""
                <div style='border:2px solid #2E8B57;border-radius:10px;padding:15px;
                            margin-bottom:20px;background-color:{color};'>
                    <b>{row["Prediction ID"]}</b> | 👤 {row['Username']}<br/>
                    Result: <b>{row['Result']}</b> | Probability: {row['Probability']:.2f}<br/>
                    Loan Type: {row['Loan Type']} | Income: Rs {row['Income']}<br/>
                    Loan Amount: Rs {row['Loan Amount']} | Term: {row['Loan Term']} months
                </div>""", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    pdf_file = generate_single_pdf(row)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 Download PDF", f,
                                           file_name=f"{row['Prediction ID']}.pdf",
                                           mime="application/pdf", key=f"pdf_{i}")
                with col2:
                    if role == 'admin' or row['Username'] == username:
                        if st.button("🗑️ Delete", key=f"del_{i}"):
                            delete_from_db(row['Prediction ID'])
                            st.success("Deleted!")
                            st.rerun()
                st.markdown("---")
        else:
            st.warning("No reports available")

    elif page == "Dashboard":
        st.markdown("<h2 style='color:#2E8B57;'>📊 Dashboard</h2>", unsafe_allow_html=True)
        df = load_from_db(username, role)
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Predictions", len(df))
            with col2: st.metric("✅ Approved", len(df[df['Result'] == 'Approved']))
            with col3: st.metric("❌ Rejected", len(df[df['Result'] == 'Rejected']))
            st.markdown("---")
            st.write("### Loan Results Distribution")
            st.bar_chart(df["Result"].value_counts())
            st.write("### Loan Type Distribution")
            st.bar_chart(df["Loan Type"].value_counts())
            st.write("### Probability Trend")
            st.line_chart(df["Probability"])
        else:
            st.warning("No data available")

    elif page == "ChangePassword":
        st.markdown("<h2 style='color:#2E8B57;'>🔑 Change Password</h2>", unsafe_allow_html=True)
        current = st.text_input("Current Password", type="password")
        new_pass = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm New Password", type="password")
        if st.button("Update Password"):
            if not login_user(username, current):
                st.error("❌ Current password is incorrect")
            elif new_pass != confirm:
                st.error("❌ New passwords do not match")
            elif len(new_pass) < 6:
                st.warning("⚠️ Password must be at least 6 characters")
            else:
                change_password(username, new_pass)
                st.success("✅ Password updated successfully!")

    elif page == "ManageUsers" and role == 'admin':
        st.markdown("<h2 style='color:#2E8B57;'>👥 Manage Users</h2>", unsafe_allow_html=True)
        users_df = get_all_users()
        st.dataframe(users_df, use_container_width=True)
        st.markdown("---")
        st.markdown("### ➕ Add New User")
        col1, col2, col3 = st.columns(3)
        with col1: new_user = st.text_input("Username")
        with col2: new_pass = st.text_input("Password", type="password")
        with col3: new_role = st.selectbox("Role", ["user", "admin"])
        if st.button("Add User"):
            if not new_user or not new_pass:
                st.warning("⚠️ Fill all fields")
            elif register_user(new_user, new_pass, new_role):
                st.success(f"✅ User '{new_user}' added!")
                st.rerun()
            else:
                st.error("❌ Username already exists")
        st.markdown("---")
        st.markdown("### 🗑️ Delete User")
        users_list = [u for u in users_df['username'].tolist() if u != 'admin']
        del_user = st.selectbox("Select user to delete", users_list if users_list else ["No users"])
        if st.button("Delete User"):
            if del_user and del_user != "No users":
                delete_user(del_user)
                st.success(f"✅ User '{del_user}' deleted!")
                st.rerun()

if not st.session_state.logged_in:
    auth_page()
else:
    main_app()