from flask import Flask, render_template, request, redirect
import json
import os
import uuid

app = Flask(__name__)

DATA_FILE = "data/reports.json"


# ==========================================
# DATA
# ==========================================


def load_data():

    if not os.path.exists(DATA_FILE):

        os.makedirs("data", exist_ok=True)

        data = {"lost": [], "found": []}

        save_data(data)

        return data

    try:

        with open(DATA_FILE, "r") as file:
            return json.load(file)

    except json.JSONDecodeError:

        data = {"lost": [], "found": []}

        save_data(data)

        return data


def save_data(data):

    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# ==========================================
# ID
# ==========================================


def generate_id(prefix):

    return prefix + "-" + str(uuid.uuid4())[:6].upper()


# ==========================================
# TEXT SIMILARITY
# ==========================================


def text_similarity(text1, text2):

    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0

    common = words1.intersection(words2)

    return len(common) / len(words1.union(words2))


# ==========================================
# SMART MATCH
# ==========================================


def calculate_match(lost, found):

    score = 0

    # --------------------------
    # ITEM NAME = 40%
    # --------------------------

    item_similarity = text_similarity(lost["item"], found["item"])

    score += item_similarity * 40

    # --------------------------
    # LOCATION = 30%
    # --------------------------

    location_similarity = text_similarity(lost["location"], found["location"])

    score += location_similarity * 30

    # --------------------------
    # DESCRIPTION = 30%
    # --------------------------

    description_similarity = text_similarity(lost["description"], found["description"])

    score += description_similarity * 30

    return round(score)


# ==========================================
# HOME
# ==========================================


@app.route("/")
def home():

    data = load_data()

    return render_template("index.html", lost=data["lost"], found=data["found"])


# ==========================================
# LOST REPORT
# ==========================================


@app.route("/report-lost", methods=["POST"])
def report_lost():

    data = load_data()

    report = {
        "id": generate_id("LF"),
        "name": request.form["name"],
        "contact": request.form["contact"],
        "item": request.form["item"],
        "description": request.form["description"],
        "location": request.form["location"],
        "date_time": request.form["date_time"],
        "verification": request.form["verification"],
        "status": "ACTIVE",
    }

    data["lost"].append(report)

    save_data(data)

    return redirect("/")


# ==========================================
# FOUND REPORT
# ==========================================


@app.route("/report-found", methods=["POST"])
def report_found():

    data = load_data()

    report = {
        "id": generate_id("FF"),
        "name": request.form["name"],
        "contact": request.form["contact"],
        "item": request.form["item"],
        "description": request.form["description"],
        "location": request.form["location"],
        "date_time": request.form["date_time"],
        "status": "ACTIVE",
    }

    data["found"].append(report)

    save_data(data)

    return redirect("/")


# ==========================================
# SMART MATCHES
# ==========================================


@app.route("/matches")
def matches():

    data = load_data()

    matches_list = []

    for lost in data["lost"]:

        if lost["status"] != "ACTIVE":
            continue

        for found in data["found"]:

            if found["status"] != "ACTIVE":
                continue

            score = calculate_match(lost, found)

            # Only show useful matches
            if score >= 30:

                matches_list.append({"score": score, "lost": lost, "found": found})

    # Highest score first

    matches_list.sort(key=lambda x: x["score"], reverse=True)

    return render_template("matches.html", matches=matches_list)

# ==========================================
# VERIFY OWNERSHIP
# ==========================================


@app.route("/verify", methods=["POST"])
def verify():

    data = load_data()

    lost_id = request.form["lost_id"]
    found_id = request.form["found_id"]
    verification = request.form["verification"]

    lost = next((r for r in data["lost"] if r["id"] == lost_id), None)

    found = next((r for r in data["found"] if r["id"] == found_id), None)

    if lost is None or found is None:
        return redirect("/matches")

    # Check verification detail

    if verification.strip().lower() == lost["verification"].strip().lower():

        lost["status"] = "VERIFIED"
        found["status"] = "MATCHED"

        save_data(data)

        return render_template("verified.html", lost=lost, found=found)

    else:

        return render_template("verification_failed.html")


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)

# VERSION 1
