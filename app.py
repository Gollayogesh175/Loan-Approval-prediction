import streamlit as st
import pandas as pd
import pickle as pk
import warnings
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

warnings.filterwarnings('ignore')

# ---------- Load Model & Scaler ----------
model = pk.load(open('model.pkl','rb'))
scaler = pk.load(open('scaler.pkl','rb'))

st.set_page_config(page_title="Loan Prediction System", layout="wide")

# ---------- PDF FUNCTION (BANK LOGO REMOVED) ----------
def generate_single_pdf(row):
    file_path = f"{row['Prediction ID']}.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # ---------- TITLE ----------
    elements.append(Paragraph("🏦 Loan Prediction Report", styles['Title']))
    elements.append(Spacer(1, 10))

    # ---------- PREDICTION INFO ----------
    color = "green" if row['Result'] == "Approved" else "red"
    elements.append(Paragraph(f"<b>Prediction ID:</b> {row['Prediction ID']}", styles['Heading2']))
    elements.append(Paragraph(f"<b>Result:</b> <font color='{color}'>{row['Result']}</font>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # ---------- DETAILS ----------
    elements.append(Paragraph(f"<b>Time:</b> {row['Time']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Loan Type:</b> {row['Loan Type']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Income:</b> ₹{row['Income']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Loan Amount:</b> ₹{row['Loan Amount']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Loan Term:</b> {row['Loan Term']} months", styles['Normal']))
    elements.append(Paragraph(f"<b>Property Value:</b> ₹{row['Property Value']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Probability:</b> {row['Probability']:.2f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # ---------- APPROVED / REJECTED MESSAGE ----------
    if row['Result'] == "Approved":
        msg = """
        ✅ For Loan Approved message:<br/>
        🎉 Congratulations! Your loan is approved.<br/>
        ✔ Maintain a good repayment history to keep your credit score strong.<br/>
        ✔ Ensure timely EMI payments to avoid penalties.<br/>
        ✔ Your loan will be disbursed within 3-5 working days.<br/>
        ✔ Keep your documents ready for verification.
        """
    else:
        msg = """
        ❌ For Loan Rejected message:<br/>
        ❌ Loan Rejected due to the following possible reasons:<br/>
        ✘ Low CIBIL score (below 650)<br/>
        ✘ Insufficient income to cover loan repayment<br/>
        ✘ High number of dependents affecting repayment capacity<br/>
        ✘ Unstable employment or self-employment risk<br/>
        ✘ Loan amount too high compared to income
        """
    elements.append(Paragraph(msg, styles['Normal']))
    elements.append(Spacer(1, 12))

    # ---------- TIPS ----------
    tips = """
    💡 Tips to Improve Your Eligibility:<br/>
    → Improve your CIBIL score by paying bills on time<br/>
    → Reduce existing debts<br/>
    → Apply for a lower loan amount<br/>
    → Add a co-applicant to strengthen your application<br/>
    → Maintain stable income for at least 6 months
    """
    elements.append(Paragraph(tips, styles['Normal']))
    elements.append(Spacer(1, 12))

    # ---------- LOAN USAGE ----------
    usage = """
    📋 General Loan Usage Info:<br/>
    📌 How Your Loan Can Be Used:<br/>
    🏠 Home Loan → Purchase, construct, or renovate property<br/>
    🚗 Car Loan → Buy new or used vehicles<br/>
    🎓 Education Loan → Fund tuition, hostel, and study materials<br/>
    💼 Business Loan → Expand business, buy equipment, manage cash flow<br/>
    💳 Personal Loan → Medical emergencies, travel, or personal needs<br/><br/>
    📌 Loan Repayment Tips:<br/>
    → Always pay EMI before the due date<br/>
    → Avoid multiple loan applications at once<br/>
    → Keep your debt-to-income ratio below 40%<br/>
    → Set up auto-pay to never miss a payment
    """
    elements.append(Paragraph(usage, styles['Normal']))
    elements.append(Spacer(1, 12))

    # ---------- CIBIL GUIDE ----------
    cibil = """
    📊 CIBIL Score Range Info:<br/>
    CIBIL Score Guide:<br/>
    🟢 750 - 900 → Excellent → High approval chance<br/>
    🟡 650 - 749 → Good → Moderate approval chance<br/>
    🟠 550 - 649 → Fair → Low approval chance<br/>
    🔴 300 - 549 → Poor → Very low approval chance
    """
    elements.append(Paragraph(cibil, styles['Normal']))

    doc.build(elements)
    return file_path

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "prediction_count" not in st.session_state:
    st.session_state.prediction_count = 1

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
    st.sidebar.title("🏦 Loan Approval Prediction App")
    if st.sidebar.button("🏠 Home"):
        set_page("Home")
    if st.sidebar.button("📊 Prediction"):
        set_page("Prediction")
    if st.sidebar.button("📁 Reports"):
        set_page("Reports")
    if st.sidebar.button("📊 Dashboard"):
        set_page("Dashboard")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.session_state.page

    # ---------- HOME PAGE ----------
    if page == "Home":
        st.markdown("""<h1 style='text-align:center;color:#2E8B57;'>🏦 Loan Prediction System</h1>""", unsafe_allow_html=True)
        st.write("### Smart Loan Approval prediction System")
        st.image("https://images.unsplash.com/photo-1565514158740-064f34bd6cfd", use_container_width=True)

    # ---------- PREDICTION PAGE ----------
    elif page == "Prediction":
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

        input_data = pd.DataFrame([[Gender, Married, Dependents, Education,
                                    Self_Employed, ApplicantIncome, LoanAmount,
                                    Credit_History, Loan_Amount_Term, Property_Area]])

        input_scaled = scaler.transform(input_data)

        if st.button("Predict Loan Status"):
            prediction = model.predict(input_scaled)
            prob = model.predict_proba(input_scaled)[0][1]

            result = "Approved" if prediction[0] == 1 else "Rejected"
            pred_id = f"PRED-{st.session_state.prediction_count}"
            st.session_state.prediction_count += 1

            if prediction[0] == 1:
                st.success(f"✅ {result} (ID: {pred_id}) | Probability: {prob:.2f}")
            else:
                st.error(f"❌ {result} (ID: {pred_id}) | Probability: {prob:.2f}")

            report = pd.DataFrame({
                "Prediction ID": [pred_id],
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

    # ---------- REPORTS PAGE ----------
    elif page == "Reports":
        st.markdown("""<h2 style='color:#2E8B57;'>📊 Prediction Reports</h2>""", unsafe_allow_html=True)
        
        if "history" in st.session_state:
            df = st.session_state.history.reset_index(drop=True)
            
            # ---------- CUSTOM CSS ----------
            st.markdown("""
            <style>
            .report-card {
                border: 2px solid #2E8B57;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: #f0fdf4;
            }
            .report-header {
                font-size: 18px;
                font-weight: bold;
                color: #1f5d3b;
            }
            .report-detail {
                font-size: 14px;
                margin-left: 10px;
            }
            </style>
            """, unsafe_allow_html=True)

            for i, row in df.iterrows():
                st.markdown(f"""
                <div class='report-card'>
                    <div class='report-header'>{row["Prediction ID"]}</div>
                    <div class='report-detail'>Result: <b>{row['Result']}</b> | Probability: {row['Probability']:.2f}</div>
                    <div class='report-detail'>Loan Type: {row['Loan Type']}</div>
                    <div class='report-detail'>Income: ₹{row['Income']}</div>
                    <div class='report-detail'>Loan Amount: ₹{row['Loan Amount']}</div>
                    <div class='report-detail'>Loan Term: {row['Loan Term']} months</div>
                    <div class='report-detail'>Property Value: ₹{row['Property Value']}</div>
                </div>
                """, unsafe_allow_html=True)

                pdf_file = generate_single_pdf(row)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "Download PDF",
                        f,
                        file_name=f"{row['Prediction ID']}.pdf",
                        mime="application/pdf",
                        key=i
                    )
                st.markdown("---")
        else:
            st.warning("No reports available")

    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.markdown("""<h2 style='color:#2E8B57;'>📊 Dashboard</h2>""", unsafe_allow_html=True)
        if "history" in st.session_state:
            df = st.session_state.history
            st.write("Loan Results Distribution")
            st.bar_chart(df["Result"].value_counts())

            st.write("Loan Type Distribution")
            st.bar_chart(df["Loan Type"].value_counts())

            st.write("Probability Trend")
            st.line_chart(df["Probability"])
        else:
            st.warning("No data available")

# ---------- RUN ----------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()