from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="static", static_folder="static")

# Database
DATABASE_PATH = "postgres://wtvkgdtoypnztx:3f55991b5f1dff58502fa50745a6ad971f0b386af5e66654092bc6929ca34109@ec2-176-34-222-188.eu-west-1.compute.amazonaws.com:5432/dfqauckl0k4ahq"
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
