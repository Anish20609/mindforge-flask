from flask import Flask, render_template, request, redirect, url_for
import os
import json
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime

app = Flask(__name__)

# === Ensure folders exist ===
os.makedirs("tests", exist_ok=True)
os.makedirs("static/graphs", exist_ok=True)

# === Homepage ===
@app.route('/')
def home():
    return render_template("index.html")

# === Dashboard ===
@app.route('/dashboard')
def dashboard():
    files = os.listdir("tests")
    test_names = [f.replace(".json", "") for f in files if f.endswith(".json")]
    return render_template("dashboard.html", tests=test_names)

# === Add Test ===
@app.route('/add', methods=['GET', 'POST'])
def add_test():
    subjects = ["Maths", "Physics", "Chemistry", "English", "Computer"]

    if request.method == 'POST':
        exam_name = request.form['exam_name']
        test_data = {}

        for subject in subjects:
            chapters = request.form.getlist(f'{subject}_chapter')
            marks = request.form.getlist(f'{subject}_mark')
            chapter_data = []

            for ch, m in zip(chapters, marks):
                if ch.strip() != "" and m.strip() != "":
                    chapter_data.append({"chapter": ch, "marks": int(m)})

            test_data[subject] = chapter_data

        filename = f"{exam_name.replace(' ', '_')}.json"
        with open(os.path.join("tests", filename), 'w') as f:
            json.dump(test_data, f, indent=4)

        return redirect(url_for('dashboard'))

    return render_template("add_test.html", subjects=subjects)

# === Show Graph ===
@app.route('/graph')
def show_graph():
    files = os.listdir("tests")
    all_data = {}

    for file in files:
        with open(os.path.join("tests", file), 'r') as f:
            test_data = json.load(f)
            for subject, chapters in test_data.items():
                for item in chapters:
                    key = f"{subject}: {item['chapter']}"
                    all_data[key] = all_data.get(key, 0) + item['marks']

    if not all_data:
        return "No data to show."

    labels = list(all_data.keys())
    values = list(all_data.values())

    # Create graph
    plt.figure(figsize=(10, 6))
    plt.barh(labels, values, color="orchid")
    plt.title("📊 Chapter-wise Progress")
    plt.xlabel("Marks")
    plt.tight_layout()

    graph_path = "static/graphs/progress.png"
    plt.savefig(graph_path)
    plt.close()

    return render_template("graph.html", graph_url=graph_path)
@app.route('/export')
def export_pdf():
    files = os.listdir("tests")
    if not files:
        return "No test data to export."

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MindForge Report Card", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%d %b %Y %H:%M')}", ln=True)
    pdf.ln(10)

    for file in files:
        with open(os.path.join("tests", file), 'r') as f:
            data = json.load(f)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"🧪 Test: {file.replace('.json','')}", ln=True)
            for subject, chapters in data.items():
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f"Subject: {subject}", ln=True)
                pdf.set_font("Arial", "", 12)
                for item in chapters:
                    pdf.cell(0, 8, f"• {item['chapter']} - {item['marks']} marks", ln=True)
            pdf.ln(6)

    output_path = "static/MindForge_Report.pdf"
    pdf.output(output_path)

    return redirect("/static/MindForge_Report.pdf")
@app.route('/tips')
def smart_tips():
    files = os.listdir("tests")
    chapter_scores = {}
    chapter_counts = {}

    for file in files:
        with open(os.path.join("tests", file), 'r') as f:
            data = json.load(f)
            for subject, chapters in data.items():
                for item in chapters:
                    key = f"{subject}: {item['chapter']}"
                    chapter_scores[key] = chapter_scores.get(key, 0) + item['marks']
                    chapter_counts[key] = chapter_counts.get(key, 0) + 1

    tips = []

    for chapter in chapter_scores:
        avg = chapter_scores[chapter] / chapter_counts[chapter]
        if avg < 50:
            tips.append((chapter, round(avg, 1)))

    return render_template("tips.html", tips=tips)
@app.route('/rank')
def show_rank():
    files = os.listdir("tests")
    total = 0
    count = 0

    for file in files:
        with open(os.path.join("tests", file), 'r') as f:
            data = json.load(f)
            for subject, chapters in data.items():
                for ch in chapters:
                    total += ch['marks']
                    count += 1

    if count == 0:
        return "No data found."

    average = total / count
    percent = round(min(max(average, 0), 100), 1)

    # Determine Rank
    if percent >= 90:
        rank = "🔥 Legend"
    elif percent >= 75:
        rank = "🏅 Prodigy"
    elif percent >= 60:
        rank = "📘 Learner"
    else:
        rank = "🌱 Beginner"

    return render_template("rank.html", avg=percent, rank=rank)


# === Run Server ===
if __name__ == '__main__':
    app.run(debug=True)
