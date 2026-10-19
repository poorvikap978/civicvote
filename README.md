# civicvote
# CivicVote 🗳️

### A Fingerprint-Based Voting System

CivicVote is a web-based voting application designed to demonstrate voter verification, secure vote submission, duplicate-vote prevention, and audit logging. The project aims to explore how biometric verification and web technologies can be combined to support a more controlled and transparent voting workflow.

## 🚀 Features

- **Voter Verification:** Fingerprint-based voter verification, according to the implemented system.
- **Duplicate-Vote Prevention:** Designed to prevent a voter from voting more than once.
- **Vote Management:** Supports the voting workflow implemented in the application.
- **Audit Logging:** Maintains logs of relevant system activities.
- **Web Interface:** Provides a user-friendly interface built with web technologies.
- **Database Integration:** Uses PostgreSQL for persistent data storage, if configured in the project.

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git and GitHub

## 📁 Project Structure

The project structure may vary depending on the implementation.

```text
CivicVote/
├── app.py
├── templates/
├── static/
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Getting Started

### Prerequisites

Install the following tools:

- Python 3
- pip
- PostgreSQL, if required by your configuration
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/poorvikap978/civicvote.git
cd civicvote
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Configure your database connection and secret keys using environment variables or a local `.env` file, according to your application code.

**Do not commit passwords, database credentials, secret keys, or real biometric records to GitHub.**

### 5. Run the Application

If `app.py` is the Flask entry point, run:

```bash
python3 app.py
```

Open the local URL displayed in your terminal, usually `http://127.0.0.1:5000`.

## ☁️ Deployment

CivicVote can be prepared for deployment on a hosting platform such as [Render](https://render.com/).

Deployment requirements may include:

- A configured Flask web service
- A production WSGI server such as Gunicorn
- A PostgreSQL database
- Environment variables for configuration and secrets
- Any additional dependencies required by the application

The exact deployment commands and configuration depend on the project's entry point, database setup, and fingerprint-verification implementation.

## 🔐 Security and Limitations

- This project is intended for educational and demonstration purposes.
- Use synthetic test data when demonstrating the application publicly.
- Do not upload real fingerprint data, voter information, or actual voting records.
- A working web application is not, by itself, proof of election-grade security or biometric accuracy.
- Any real-world deployment would require independent security, privacy, accessibility, and election-system assessments.

## 🎯 Project Objective

The objective of CivicVote is to demonstrate a web-based voting workflow incorporating voter verification, duplicate-vote prevention, database integration, and audit logging.

## 👩‍💻 Author

**Poorvika**

GitHub: [@poorvikap978](https://github.com/poorvikap978)

---

*Built as an educational project exploring web development, database management, and biometric-based voter verification.*