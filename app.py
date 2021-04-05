from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import threading
import boto3
from datetime import datetime

from synthesize import load_model, load_waveglow

# Flask
app = Flask(__name__, template_folder="static", static_folder="static")
samples_folder = os.path.join("static", "samples")
results_folder = os.path.join("static", "results")
os.makedirs(samples_folder, exist_ok=True)
os.makedirs(results_folder, exist_ok=True)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB
db = SQLAlchemy(app)

# S3
s3 = boto3.client("s3", aws_access_key_id=os.getenv("S3_KEY"), aws_secret_access_key=os.getenv("S3_SECRET"))
BUCKET_NAME = "voicesharinghub"
BUCKET_URL = "https://voicesharinghub.s3.eu-west-2.amazonaws.com/"


def upload_file_to_s3(file):
    try:
        s3.upload_fileobj(
            file, BUCKET_NAME, file.filename, ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )
    except Exception as e:
        print(e)


def download_file(filename):
    try:
        s3.download_file(BUCKET_NAME, filename, os.path.join("static", "samples", filename))
    except Exception as e:
        print(e)


def get_sample_name(voice_name):
    return voice_name.replace(" ", "_") + ".wav"


def get_demo_name(voice_name):
    return voice_name.replace(" ", "_") + ".pt"


def get_timestamp():
    return datetime.now().strftime("%d-%m-%Y_%H-%M-%S")


def download_files(voices):
    downloaded_files = os.listdir(samples_folder)
    print("DOWNLOADING FILES")

    for voice in voices:
        sample = get_sample_name(voice.name)
        demo = get_demo_name(voice.name)
        if voice.has_audio and sample not in downloaded_files:
            print("Downloading", sample)
            download_file(sample)
        if voice.has_demo and demo not in downloaded_files:
            print("Downloading", demo)
            download_file(demo)


def preload_models(voices):
    print("LOADING MODELS")
    models = {}

    for voice in voices:
        if voice.has_demo:
            demo = get_demo_name(voice.name)
            print("Loading", demo)
            models[voice.name] = load_model(os.path.join(samples_folder, demo))

    return models


def preload_waveglow():
    print("LOADING WAVEGLOW")

    if WAVEGLOW_NAME not in os.listdir(samples_folder):
        download_file(WAVEGLOW_NAME)

    print("Loading", WAVEGLOW_NAME)
    return load_waveglow(os.path.join(samples_folder, WAVEGLOW_NAME))


class Voice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(200), nullable=False)
    dataset_url = db.Column(db.String(200), nullable=False)
    model_url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    has_audio = db.Column(db.Boolean, default=False)
    has_demo = db.Column(db.Boolean, default=False)


lock = threading.Lock()
with lock:
    db.create_all()

from views import *
voices = Voice.query.all()
download_files(voices)

# Models
WAVEGLOW_NAME = "waveglow.pt"
models = preload_models(voices)
waveglow = preload_waveglow()


def get_model_and_waveglow(name):
    return models[name], waveglow


if __name__ == "__main__":
    app.run(debug=False)
