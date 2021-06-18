from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import threading
import boto3
import requests


# Flask
app = Flask(__name__, template_folder="static", static_folder="static")
samples_folder = os.path.join("static", "samples")
os.makedirs(samples_folder, exist_ok=True)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# S3
s3 = boto3.client("s3", aws_access_key_id=os.getenv("S3_KEY"), aws_secret_access_key=os.getenv("S3_SECRET"))
BUCKET_NAME = "voicesharinghub"
BUCKET_URL = "https://voicesharinghub.s3.eu-west-2.amazonaws.com/"

# Demo
DEMO_URL = "https://voice-cloning-api.herokuapp.com/"


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


def get_demo_results(voice_name, text):
    r = requests.get(url=DEMO_URL, params={"name": voice_name, "text": text})
    return r.json()


def get_sample_name(voice_name):
    return voice_name.replace(" ", "_") + ".wav"


def download_files():
    voices = Voice.query.all()
    downloaded_files = os.listdir(samples_folder)

    for voice in voices:
        sample = get_sample_name(voice.name)
        if voice.has_audio and sample not in downloaded_files:
            print("Downloading", sample)
            download_file(sample)


class Voice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    creator = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(200), nullable=False)
    dataset_url = db.Column(db.String(200), nullable=False)
    model_url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    has_audio = db.Column(db.Boolean, default=False)
    has_demo = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)

lock = threading.Lock()
with lock:
    db.init_app(app)
    migrate.init_app(app, db)

from views import *
download_files()

if __name__ == "__main__":
    app.run(debug=False)
