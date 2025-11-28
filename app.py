"""
SkillPath - Flask Backend (app.py)
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import analysis
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = "uploads"
ROADMAP_FOLDER = "roadmaps"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ROADMAP_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ROADMAP_FOLDER"] = ROADMAP_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/results")
def results_page():
    return render_template("results.html")


@app.route("/parse", methods=["POST"])
def parse_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    parsed = analysis.parse_resume(save_path)
    return jsonify({"parsed": parsed})


@app.route("/match", methods=["POST"])
def match_endpoint():
    payload = request.get_json()
    if not payload or "parsed" not in payload:
        return jsonify({"error": "Missing parsed payload"}), 400

    matches = analysis.match_candidate(payload["parsed"])
    return jsonify({"matches": matches})


@app.route("/roadmap", methods=["POST"])
def roadmap_endpoint():
    """
    Expects payload: { candidate: { ... } }
    Candidate may be a job match object (role, match_score, missing_skills, ...) or a custom dict.
    """
    payload = request.get_json()
    if not payload or "candidate" not in payload:
        return jsonify({"error": "Missing candidate payload"}), 400

    candidate = payload["candidate"]

    # generate roadmap PDF
    pdf_path = analysis.generate_roadmap(candidate)

    if not os.path.isfile(pdf_path):
        return jsonify({"error": "Roadmap generation failed"}), 500

    # send file, using safe download name
    return send_file(pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path))


if __name__ == "__main__":
    app.run(debug=True)
