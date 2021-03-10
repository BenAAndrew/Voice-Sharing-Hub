from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import threading

app = Flask(__name__, template_folder="static", static_folder="static")

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Voice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(200), nullable=False)
    dataset_url = db.Column(db.String(200), nullable=False)
    model_url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    audio_sample_url = db.Column(db.String(200), nullable=True)

lock = threading.Lock()
with lock:
    db.create_all()

from views import *

if __name__ == "__main__":
    app.run(debug=True)
