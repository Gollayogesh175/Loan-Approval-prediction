import streamlit as st
import pandas as pd
import pickle as pk
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# Load model and scaler
model = pk.load(open('model.pkl','rb'))
scaler = pk.load(open('scaler.pkl','rb'))

st.set_page_config(page_title="Loan Prediction System", layout="wide")

# ---------- SESSION LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN PAGE ----------
def login_page():
    st.markdown("""<h1 style='text-align:center;color:#2E8B57;'>🔐 Login</h1>""", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------- PAGE NAVIGATION ----------
def set_page(page_name):
    st.session_state.page = page_name

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- MAIN APP ----------
def main_app():

    # Sidebar buttons (page by page navigation)
    st.sidebar.title("🏦 Loan App")
    if st.sidebar.button("🏠 Home"):
        set_page("Home")
    if st.sidebar.button("📊 Loan Prediction"):
        set_page("Loan Prediction")
    if st.sidebar.button("📁 Reports"):
        set_page("Reports")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.session_state.page

    # HOME PAGE
    if page == "Home":
        st.markdown("""<h1 style='text-align:center;color:#2E8B57;'>🏦 Loan Prediction System</h1>""", unsafe_allow_html=True)
        st.write("### Smart Loan Approval System")
        st.image("https://images.unsplash.com/photo-1565514158740-064f34bd6cfd", use_container_width=True)

    # LOAN PREDICTION PAGE
    elif page == "Loan Prediction":
        st.markdown("""<h2 style='color:#2E8B57;'>🔍 Loan Prediction</h2>""", unsafe_allow_html=True)

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

        # Encoding
        Gender = 1 if Gender == 'Male' else 0
        Married = 1 if Married == 'Yes' else 0
        Dependents = 3 if Dependents == '3+' else int(Dependents)
        Education = 1 if Education == 'Graduate' else 0
        Self_Employed = 1 if Self_Employed == 'Yes' else 0
        Credit_History = 1 if Credit_History >= 700 else 0

        input_data = pd.DataFrame([[
            Gender, Married, Dependents, Education,
            Self_Employed, ApplicantIncome, LoanAmount,
            Credit_History, Loan_Amount_Term, Property_Area
        ]])

        input_scaled = scaler.transform(input_data)

        if st.button("Predict Loan Status"):
            prediction = model.predict(input_scaled)
            prob = model.predict_proba(input_scaled)[0][1]

            result = "Approved" if prediction[0] == 1 else "Rejected"

            if prediction[0] == 1:
                st.success(f"✅ Loan Approved (Probability: {prob:.2f})")
            else:
                st.error(f"❌ Loan Rejected (Probability: {prob:.2f})")

            report = pd.DataFrame({
                "Time": [datetime.now()],
                "Loan Type": [loan_type],
                "Income": [ApplicantIncome],
                "Loan Amount": [LoanAmount],
                "Loan Term": [Loan_Amount_Term],
                "Property Value": [Property_Area],
                "Result": [result],
                "Probability": [prob]
            })

            if "history" not in st.session_state:
                st.session_state.history = report
            else:
                st.session_state.history = pd.concat([st.session_state.history, report])

    # REPORTS PAGE
    elif page == "Reports":
        st.markdown("""<h2 style='color:#2E8B57;'>📊 Prediction Reports</h2>""", unsafe_allow_html=True)

        if "history" in st.session_state:
            st.dataframe(st.session_state.history)

            csv = st.session_state.history.to_csv(index=False).encode('utf-8')
            st.download_button("Download Report", csv, "loan_report.csv", "text/csv")
        else:
            st.warning("No reports available")

# ---------- RUN ----------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
