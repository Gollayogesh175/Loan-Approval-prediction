# 🏦 Loan Prediction System

A smart AI-based Loan Approval Prediction System built with **Streamlit**, **Machine Learning**, and **SQLite** database.

---

## 🚀 Features

- 🔐 Multi-user Login & Registration
- 🛡️ Role-based Access (Admin & User)
- 📊 AI-based Loan Approval Prediction
- 📁 Prediction Reports with PDF Download
- 📊 Interactive Dashboard with Charts
- 💾 SQLite Database for persistent storage
- 🔑 Change Password functionality
- 👥 Admin Panel to Manage Users

---

## 🖥️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core Language |
| Streamlit | Web App Framework |
| Scikit-learn | ML Model |
| Pandas | Data Handling |
| SQLite | Database |
| ReportLab | PDF Generation |
| Hashlib | Password Encryption |

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/loan-predictor.git
cd loan-predictor
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

---

## 📁 Project Structure
```
loan-predictor/
├── app.py               # Main application file
├── model.pkl            # Trained ML model
├── scaler.pkl           # Feature scaler
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── .gitignore           # Git ignore file
```

---

## 🔑 Default Login

| Role | Username | Password |
|---|---|---|
| Admin | admin | admin123 |

---

## 📊 Input Features

| Feature | Description |
|---|---|
| Gender | Male / Female |
| Marital Status | Married / Not Married |
| Dependents | Number of dependents |
| Education | Graduate / Not Graduate |
| Self Employed | Yes / No |
| Applicant Income | Monthly income |
| Loan Amount | Requested loan amount |
| Loan Term | Duration in months |
| Credit Score | CIBIL score (300-1000) |
| Property Value | Asset value |

---

## 📊 CIBIL Score Guide

| Score Range | Rating | Approval Chance |
|---|---|---|
| 750 - 900 | Excellent | High |
| 650 - 749 | Good | Moderate |
| 550 - 649 | Fair | Low |
| 300 - 549 | Poor | Very Low |

---

## 👥 User Roles

### 👤 User
- Register and Login
- Make Loan Predictions
- View own Reports
- Download PDF Reports
- Change Password

### 🛡️ Admin
- All User features
- View All Users Predictions
- Manage Users (Add / Delete)
- Full Dashboard Access

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

Made with ❤️ by **Yoges**
```

---

### Save this as `README.md` in your project folder:
```
loan-predictor/
├── app.py
├── model.pkl
├── scaler.pkl
├── requirements.txt
├── README.md        ← add this file
└── .gitignore