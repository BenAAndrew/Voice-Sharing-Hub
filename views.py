from flask import request, render_template, redirect
from app import (
    app,
    db,
    Voice,
    upload_file_to_s3,
    download_file,
    samples_folder,
    get_sample_name,
    get_demo_results,
    DEMO_URL
)
import requests
import os
import csv
service_password = os.getenv("SERVICE_PASSWORD")


@app.route("/", methods=["GET"])
def index():
    voices = Voice.query.order_by(Voice.id.asc())
    return render_template("index.html", voices=voices)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.values["password"] == service_password:
            voices = Voice.query.all()
            return render_template("admin.html", voices=voices, password=request.values["password"])
    return render_template("admin.html")


@app.route("/demo-settings", methods=["POST"])
def demo_settings():
    if request.values["password"] == service_password:
        voice = Voice.query.filter_by(id=request.values["id"]).one()
        voice.has_demo = not voice.has_demo
        db.session.add(voice)
        print(voice)
        db.session.commit()
    return redirect("/admin")


@app.route("/verify-voice", methods=["POST"])
def verify_voice():
    if request.values["password"] == service_password:
        voice = Voice.query.filter_by(id=request.values["id"]).one()
        voice.verified = not voice.verified
        db.session.add(voice)
        db.session.commit()
    return redirect("/admin")


@app.route("/update-voice", methods=["POST"])
def update_voice():
    if request.values["password"] == service_password:
        voice = Voice.query.filter_by(id=request.values["id"]).one()
        voice.name = request.values["name"]
        voice.description = request.values["description"]
        voice.source_url = request.values["source_url"]
        voice.dataset_url = request.values["dataset_url"]
        voice.model_url = request.values["model_url"]
        db.session.add(voice)
        db.session.commit()
    return redirect("/admin")


@app.route("/delete-voice", methods=["POST"])
def delete_voice():
    if request.values["password"] == service_password:
        voice = Voice.query.filter_by(id=request.values["id"]).one()
        db.session.delete(voice)
        db.session.commit()
    return redirect("/admin")


@app.route("/import-voices", methods=["POST"])
def import_voices():
    if request.values["password"] == service_password:
        request.files["file"].save("temp.csv")
        for row in csv.DictReader(open("temp.csv")):
            for field in row:
                if row[field] == "true":
                    row[field] = True
                elif row[field] == "false":
                    row[field] = False
            voice = Voice(**row)
            db.session.add(voice)
        db.session.commit()
    return redirect("/admin")


@app.route("/voice", methods=["GET"])
def voice():
    try:
        voice = Voice.query.filter_by(id=request.args.get("id")).one()
    except:
        return redirect("/")

    audio_path = os.path.join(samples_folder, get_sample_name(voice.name))
    return render_template("voice.html", voice=voice, audio_path=audio_path)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        for key, value in request.values.items():
            if key.endswith("url"):
                try:
                    r = requests.head(value)
                except:
                    return render_template("create.html", error=f"Invalid {key.replace('_',' ')}")

        data = request.values.copy()

        if request.files.get("audio_sample"):
            f = request.files["audio_sample"]
            f.filename = get_sample_name(data["name"])
            upload_file_to_s3(f)
            download_file(f.filename)
            data["has_audio"] = True

        voice = Voice(**data)
        db.session.add(voice)
        db.session.commit()
        return redirect("/voice?id=" + str(voice.id))
    else:
        return render_template("create.html")


@app.route("/demo-voice", methods=["GET", "POST"])
def demo_voice():
    if request.method == "POST":
        text = request.values["text"]
        voice = Voice.query.filter_by(id=request.values["id"]).one()
        assert voice.has_demo, "Not enabled for demo"

        results = get_demo_results(voice.name, text)
        return render_template("demo.html", voice=voice, graph=DEMO_URL+results["graph"], audio=DEMO_URL+results["audio"], text=text)
    else:
        try:
            voice = Voice.query.filter_by(id=request.args.get("id")).one()
        except:
            return redirect("/")

        if not voice.has_demo:
            return redirect(f"/voice?id={voice.id}")

        return render_template("demo.html", voice=voice)
