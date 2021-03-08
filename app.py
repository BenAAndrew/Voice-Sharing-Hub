from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="static", static_folder="static")

# Database
DATABASE_PATH = "postgresql://postgres:password@localhost:5432/voicehub"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Voice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    dataset_url = db.Column(db.String(200), nullable=False)
    model_url = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    audio_sample_url = db.Column(db.String(200), nullable=False)

# Setup
db.create_all()
from views import *

if __name__ == "__main__":
    app.run(debug=True)
