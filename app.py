from flask import Flask, request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:fmg9akimbo@localhost/monsi"
app.config["SECRET_KEY"] = "super-secret"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.debug = True
db = SQLAlchemy(app)
# db.create_all()

# Define Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    confirmed_at = db.Column(db.DateTime())
    

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    link = db.Column(db.String(255))
    count_likes = db.Column(db.Integer)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    image_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    image_id = db.Column(db.String(255), unique=True)
    like = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime())


#----------------------------------------------------------------
#User login

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    """
    data = {
        "email":"Str",
    }
    """

    newuser = User(email=data["email"], confirmed_at=datetime.datetime.now())
    db.session.add(newuser)
    db.session.commit()

    return jsonify({"user": newuser})


@app.route("/login/", methods=["GET"])
def login():
    data = request.get_json()
    """
    data = {
        "email":"Str",
    }
    """

    user = User.query.filter_by(email=data["email"]).first()

    if user is None:
        return jsonify({"message":"No user found"})
    else:
        return jsonify({"message":"Logined Succesfully"})
    

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
    image_data["count_likes"] = image.count_likes
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
        image_data["count_likes"] = image.count_likes
        response.append(image_data)

    return jsonify({"images": response})


@app.route("/click_images", methods=["Post"])
def click_images():
    data = request.get_json()
    """
    data = {
        "email":"Str",
        "image_id":"Int"
    }
    """
    #is post better or insert better for log?
    log = Log(email=data["email"], image_id=data["image_id"], created_at=datetime.datetime.now())
    db.session.add(log)
    db.session.commit()

    return jsonify({"images": "clicked"})


@app.route("/likes/", methods=["GET", "POST"])
def like_images():
    data = request.get_json()

    """
    data = {
        "email":"Str",
        "image_id":"Int"
    }
    """

    like = Like.query.filter_by(email=data["email"]).filter_by(image_id=data["image_id"]).all()

    #Delete
    if like is not None: 
        db.session.delete(like)
        image = Image.query.filter_by(image_id=data["image_id"]).all()
        image.count_likes -= 1
        db.session.commit()

        return jsonify({"message": "succesfully unliked"})

    #Post
    else: #when its first time to like there is nothing in the db 
        like = like(email=data["email"], image_id=data["image_id"], like=True, created_at=datetime.datetime.now())
        db.session.add(like)

        image = Image.query.filter_by(image_id=data["image_id"]).all()
        if image.count_likes is None:
            image.count = 1
        else:
            image.count_likes += 1
        db.session.commit()

        return jsonify({"message": "succesfully liked"})


@app.route("/load_like", methods=["Get"])
def load_like():
    data = request.get_json()

    """
    data = {
        "email":"Str",
        "image_id":"Int"
    }
    """
    #want to load not just like table but like and Image joined
    #loads images that we liked in the order of latest
    
    like = Like.query.filter_by(email=data["email"]).filter_by(image_id=data["image_id"]).order_by(Like.created_at.desc()).all()
    images = Image.query.filter_by(image_id=like.image_id).all()

    response = []

    for image in images:
        image_data = {}
        image_data["image_id"] = image.image_id
        image_data["url"] = image.url
        image_data["link"] = image.link
        image_data["count_likes"] = image.count_likes
        response.append(image_data)

    return jsonify({"images": response})

if __name__ == "__main__":
    app.run()