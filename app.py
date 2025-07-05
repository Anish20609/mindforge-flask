from flask import Flask, render_template, request, redirect, send_file
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF

app = Flask(__name__)
DATA_FILE = "tests/tests.json"

# Ensure folders exist
os.makedirs("tests", exist_ok=True)
os.makedirs("static/graphs", exist_ok=True)

# Load tests from file
def load_tests():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Save tests to file
def save_tests(tests):
    with open(DATA_FILE, "w") as f:
        json.dump(tests, f, indent=4)

# Rank system logic
def calculate_rank(total_marks):
    if total_marks >= 95:
        return "Diamond"
    elif total_marks >= 85:
        return "Platinum"
    elif total_marks >= 75:
        return "Gold"
    elif total_marks >= 65:
        return "Silver"
    else:
        return "Bronze"

# Home page
@app.route("/")
def index():
    tests = load_tests()
    recent_tests = sorted(tests, key=lambda x: x["date"], reverse=True)[:5]
    return render_template("index.html", recent_tests=recent_tests)

# Add Test
@app.route("/add", methods=["GET", "POST"])
def add_test():
    if request.method == "POST":
        test = {
            "subject": request.form["subject"],
            "chapter": request.form["chapter"],
            "date": request.form["date"],
            "marks": int(request.form["marks"]),
            "total": int(request.form["total"]),
            "remarks": request.form["remarks"]
        }
        tests = load_tests()
        tests.append(test)
        save_tests(tests)
        return redirect("/")
    return render_template("add.html")

# Dashboard page
@app.route("/dashboard")
def dashboard():
    tests = load_tests()
    return render_template("dashboard.html", tests=tests)

# Graph page
@app.route("/graph")
def graph():
    tests = load_tests()
    if not tests:
        return "No test data to generate graph."

    dates = [t["date"] for t in tests]
    marks = [t["marks"] for t in tests]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, marks, marker="o", linestyle="-", color="blue")
    plt.title("Marks Progress")
    plt.xlabel("Date")
    plt.ylabel("Marks Scored")
    plt.grid(True)
    plt.tight_layout()

    graph_path = "static/graphs/progress.png"
    plt.savefig(graph_path)
    plt.close()
    return render_template("graph.html", graph_url=graph_path)

# Tips route
@app.route("/tips")
def tips():
    tips_list = [
        "Stay consistent every day!",
        "Revise mistakes from previous tests.",
        "Solve 10 questions before sleeping.",
        "Use NCERT examples for basics.",
        "Avoid burnout — take breaks!"
    ]
    return render_template("tips.html", tips=tips_list)

# Rank route
@app.route("/rank")
def rank():
    tests = load_tests()
    total_scored = sum(t["marks"] for t in tests)
    total_max = sum(t["total"] for t in tests)
    percentage = (total_scored / total_max * 100) if total_max > 0 else 0
    current_rank = calculate_rank(percentage)
    return render_template("rank.html", total=total_scored, max=total_max,
                           percentage=round(percentage, 2), rank=current_rank)

# Export to PDF (emoji removed)
@app.route("/export")
def export_pdf():
    tests = load_tests()
    if not tests:
        return "No data to export."

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test Report", ln=True, align='C')
    pdf.ln(10)

    for t in tests:
        pdf.cell(200, 10, txt=f"Date: {t['date']}", ln=True)
        pdf.cell(200, 10, txt=f"Subject: {t['subject']}", ln=True)
        pdf.cell(200, 10, txt=f"Chapter: {t['chapter']}", ln=True)
        pdf.cell(200, 10, txt=f"Marks: {t['marks']} / {t['total']}", ln=True)
        pdf.cell(200, 10, txt=f"Remarks: {t['remarks']}", ln=True)
        pdf.ln(5)

    output_path = "tests/report.pdf"
    pdf.output(output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
