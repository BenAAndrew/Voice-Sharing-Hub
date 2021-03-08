from flask import request, render_template, redirect
from app import app, db, Voice
import requests

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
    return render_template("voice.html", voice=voice)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        for key, value in request.values.items():
            if key.endswith("url"):
                try:
                    r = requests.head(value)
                except:
                    return render_template("create.html", error=f"Invalid {key.replace('_',' ')}")

        voice = Voice(
            **request.values
        )
        db.session.add(voice)
        db.session.commit()
        return redirect("/voice?id="+str(voice.id))
    else:
        return render_template("create.html")
