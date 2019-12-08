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
    uuid = db.Column(db.String(255), unique=True)
    image_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True)
    image_id = db.Column(db.String(255), unique=True)
    like = db.Column(db.Boolean)


#----------------------------------------------------------------
#User login

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    """
    data = {
        "email":"Str",
        "password":"Str"
    }
    """

    newuser = User(uuid=str(uuid.uuid4()), email=data["email"], password=data["password"], confirmed_at=datetime.datetime.now())
    db.session.add(newuser)
    db.session.commit()

    return jsonify({"user": newuser})


@app.route("/login/", methods=["GET"])
def login():
    data = request.get_json()
    """
    data = {
        "email":"Str",
        "password":"Str"
    }
    """

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
    

#-------------------------------------------------------
#Image 

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


@app.route("/click_images", methods=["Post"])
def click_images():
    data = request.get_json()
    """
    data = {
        "uuid":"Str",
        "image_id":"Int"
    }
    """
    #is post better or insert better for log?
    log = Log(uuid=data["uuid"], image_id=data["image_id"], created_at=datetime.datetime.now())
    db.session.add(log)
    db.session.commit()
    return 200


@app.route("/like_images", methods=["GET", "POST", "UPDATE"])
def like_images():
    data = request.get_json()
    """
    data = {
        "uuid":"Str",
        "image_id":"Int"
    }
    """

    favorite = Favorite.query.filter_by(uuid=data["uuid"]).filter_by(image_id=data["image_id"]).all()

    #Update
    if favorite.like == True:
        favorite.like = False
        db.session.add(favorite)
        db.session.commit()

    #Update
    elif favorite.like == False:
        favorite.like = True
        db.session.add(favorite)
        db.session.commit()

    #Post
    else: #when its first time to like there is nothing in the db 
        like = Favorite(uuid=data["uuid"], image_id=data["image_id"], like=True)
        db.session.add(like)
        db.session.commit()

    return 200


@app.route("/load_favorite", methods=["Get"])
def load_favorite():
    data = request.get_json()

    """
    data = {
        "uuid":"Str",
        "image_id":"Int"
    }
    """
    #want to load not just Favorite table but Favorite and Image joined

    favorite = Favorite.query.filter_by(uuid=data["uuid"]).filter_by(image_id=data["image_id"]).filter_by(like=True).all()
    images = Image.query.filter_by(image_id=favorite.image_id).all()

    response = []

    for image in images:
        image_data = {}
        image_data["image_id"] = image.image_id
        image_data["url"] = image.url
        image_data["link"] = image.link
        response.append(image_data)

    return jsonify({"images": response})

if __name__ == "__main__":
    app.run()