# 🔍AI Code Reviewer – Streamlit Web Application
Final Internship Project – Code Quality Analysis & Optimization Tool
# 📌 Overview

The AI Code Reviewer is a Streamlit-based web application designed to automatically analyze Python source code for quality, style, maintainability, and structural efficiency.

This tool performs static code analysis using industry-standard libraries such as Flake8, Radon, and Black, and provides a clean Apple-style UI for developers to review and improve their code.

This project simulates a real-world code-review system used in software companies, making it ideal for internship submission.

# 🎯 Objective

To build an automated tool that helps developers:

Detect style violations

Measure code complexity

Improve maintainability

Format source code

Download final reports

Visualize complexity metrics

# 🛠️ Features
1. Upload or Edit Python Files

Upload any .py file

Or edit the code directly inside the editor

2. Automated Code Analysis

The system performs:

Flake8 analysis – PEP8 style issues

Radon CC – Cyclomatic complexity

Radon MI – Maintainability Index

Code formatting via Black

3. Clean Apple-Style UI

Modern minimal UI

Multi-tab output sections

Live metrics

Beautiful formatted code section

4. Exportable Reports

You can download:

Formatted code

JSON analysis reports

5. Local & Global Deployment Support

Runs locally or can be deployed globally using Streamlit Cloud.

# 📂 Project Structure
AI-CODE-REVIEWER/
│── app.py                      # Main Streamlit app
│── requirements.txt            # Python dependencies
│── .streamlit/
│      └── config.toml          # Dark mode UI configuration
│── core/
│      ├── code_analysis.py     # Flake8 + Radon logic
│      ├── formatter.py         # Black code formatter
│      └── utils.py             # File utilities
│── inputs/                     # Uploaded / example code
│── outputs/                    # Formatted code output
│── reports/                    # JSON reports

# 🚀 How It Works
Step 1 — Upload Code

User uploads a .py file or selects an example by pasting the code.

Step 2 — Analysis Processing
Click save edits to file and click run analysis.

The file is scanned using:
flake8 → Finds style issues
radon cc → Measures complexity
radon mi → Calculates maintainability

Step 3 — Code Formatting
Black automatically formats the code to industry standards.

Step 4 — Output & Visuals
List of style errors
Complexity charts
Maintainability reports
Fully formatted code

Step 5 — Export
Download results as JSON or download the formatted code file.


# 🧰 Technologies Used
| Tool             | Purpose              |
| ---------------- | -------------------- |
| **Streamlit**    | Web interface        |
| **Flake8**       | Style checking       |
| **Radon**        | Complexity analysis  |
| **Black**        | Auto code formatting |
| **Matplotlib**   | Complexity charts    |
| **Python 3.10+** | Backend logic        |


# 📦 Installation Steps 
pip install -r requirements.txt

streamlit run app.py

# 🌐 Deployment Options

You can deploy this project globally using:

✔ Streamlit Cloud 


# 🏁 Conclusion

The AI Code Reviewer simplifies the entire process of analyzing Python code and provides developers with a clean, advanced, and visually appealing interface to enhance code quality.
It integrates multiple static analysis tools into one unified platform, making it useful for interns, students, and professional developers.



# Live demo 👇

https://jgmqxoaptndlsravfmjpxg.streamlit.app/
