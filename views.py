from flask import request, render_template, redirect
from app import (
    app,
    db,
    Voice,
    upload_file_to_s3,
    download_file,
    samples_folder,
    get_sample_name,
    results_folder,
    get_timestamp,
    get_demo_name,
    WAVEGLOW_NAME
)
import requests
import os
import inflect


from synthesize import synthesize, load_model, load_waveglow


voices = Voice.query.all()
models = {}
waveglow = load_waveglow(os.path.join(samples_folder, WAVEGLOW_NAME))

# Synthesis
inflect_engine = inflect.engine()
GRAPH = "graph.png"
AUDIO = "audio.wav"


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

        if voice.name not in models:
            demo = get_demo_name(voice.name)
            print("Loading", demo)
            models[voice.name] = load_model(os.path.join(samples_folder, demo))
        
        model = models[voice.name] 
        timestamp = get_timestamp()
        graph_path = os.path.join(results_folder, f"{timestamp}-{GRAPH}")
        audio_path = os.path.join(results_folder, f"{timestamp}-{AUDIO}")
        synthesize(model, waveglow, text, inflect_engine, graph=graph_path, audio=audio_path)
        return render_template("demo.html", voice=voice, graph=graph_path, audio=audio_path, text=text)
    else:
        try:
            voice = Voice.query.filter_by(id=request.args.get("id")).one()
        except:
            return redirect("/")

        if not voice.has_demo:
            return redirect(f"/voice?id={voice.id}")

        return render_template("demo.html", voice=voice)
