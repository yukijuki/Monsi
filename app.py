from flask import Flask
from flask import request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:fmg9akimbo@localhost/monsi"
app.config["SECRET_KEY"] = "super-secret"

app.debug = True
db = SQLAlchemy(app)


# Define Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime())
    

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), unique=True)
    link = db.Column(db.String(255), unique=True)
    count = db.Column(db.Integer)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    user = User(data["email"], data["password"])
    db.session.add(user)
    db.session.commit()

    return 200

@app.route("/login", methods=["GET"])
def login():
    data = request.get_json()

    user_data = User.query.filter_by(email=data["email"]).first()
    if user_data is None:
        return 404
    elif user_data["password"] == data["password"]:
        return 200
    elif user_data["password"] == "":
        return 403
    else:
        return 418


@app.route("/get_images", methods=["Get"])
def get_images():
    data = Image.query.all()
    return jsonify({"url":data["url"], "link":data["link"]})

if __name__ == "__main__":
    app.run()