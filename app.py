from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import threading
import boto3

app = Flask(__name__, template_folder="static", static_folder="static")

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 # 1MB
db = SQLAlchemy(app)

# S3
s3 = boto3.client(
   "s3",
   aws_access_key_id=os.getenv('S3_KEY'),
   aws_secret_access_key=os.getenv('S3_SECRET')
)
BUCKET_NAME = "voicesharinghub"
BUCKET_URL = "https://voicesharinghub.s3.eu-west-2.amazonaws.com/"

def upload_file_to_s3(file):
    try:
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print(e)

class Voice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(200), nullable=False)
    dataset_url = db.Column(db.String(200), nullable=False)
    model_url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    has_audio = db.Column(db.Boolean, default=False)

lock = threading.Lock()
with lock:
    db.create_all()

from views import *

if __name__ == "__main__":
    app.run(debug=True)
