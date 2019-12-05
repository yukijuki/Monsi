from flask import Flask, request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime



app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:fmg9akimbo@localhost/monsi"
app.config["SECRET_KEY"] = "super-secret"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.debug = True
db = SQLAlchemy(app)
db.create_all()

# Define Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime())
    

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    link = db.Column(db.String(255))


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    newuser = User(uuid=str(uuid.uuid4()), email=data["email"], password=data["password"], confirmed_at=datetime.datetime.now())
    db.session.add(newuser)
    db.session.commit()

    return jsonify({"user": newuser})


@app.route("/login/", methods=["GET"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if user is None:
        return 404, jsonify({"message":"No user found"})

    elif user.password == data["password"]:
        user_data = {}
        user_data["email"] = user.email
        user_data["password"] = user.password
        return 200

    elif user_data["password"] == "":
        return 403

    else:
        return 418
    

#image get
@app.route("/get_first_image", methods=["GET"])
def get_first_image():

    image = Image.query.first()

    response = []

    image_data = {}
    image_data["image_id"] = image.image_id
    image_data["url"] = image.url
    image_data["link"] = image.link
    response.append(image_data)

    return jsonify({"images": response})


@app.route("/get_images", methods=["GET"])
def get_images():
    images = Image.query.all()
    
    response = []

    for image in images:
        image_data = {}
        image_data["image_id"] = image.image_id
        image_data["url"] = image.url
        image_data["link"] = image.link
        response.append(image_data)

    return jsonify({"images": response})


@app.route("/click_images", methods=["POST"])
def click_images():
    data = request.get_json()

    log = Log(image_id=data(["image_id"]), created_at=datetime.datetime.now())
    db.session.add(log)
    db.session.commit()
    return 200

if __name__ == "__main__":
    app.run()