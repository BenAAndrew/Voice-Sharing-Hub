from flask import request, render_template, redirect
from app import app, db, Voice
import requests
import os

@app.route("/", methods=["GET"])
def index():
    voices = Voice.query.all() 
    return render_template("index.html", voices=voices)


@app.route("/voice", methods=["GET"])
def voice():
    try:
        voice = Voice.query.filter_by(id=request.args.get("id")).one()
    except:
        return redirect("/")

    audio_path = os.path.join("static", "samples", voice.name+".wav")
    has_audio = os.path.isfile(audio_path)
    return render_template("voice.html", voice=voice, audio_path=audio_path, has_audio=has_audio)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        for key, value in request.values.items():
            if key.endswith("url"):
                try:
                    r = requests.head(value)
                except:
                    return render_template("create.html", error=f"Invalid {key.replace('_',' ')}")

        if request.files.get("audio_sample"):
            f = request.files["audio_sample"]
            f.save(os.path.join("static", "samples", request.values["name"]+".wav"))

        voice = Voice(
            **request.values
        )
        db.session.add(voice)
        db.session.commit()
        return redirect("/voice?id="+str(voice.id))
    else:
        return render_template("create.html")
