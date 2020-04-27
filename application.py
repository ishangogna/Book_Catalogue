from flask import Flask, render_template,request,session,jsonify,session,redirect
import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
DATABASE_URL = "Your DATABASE URI here"
app.secret_key= "Project1"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Registration")
def register():
    return render_template("Registration.html")   

@app.route("/Registration", methods=["POST"])
def signup():
    user = request.form.get("user")
    if not request.form.get("user"):
        return render_template("Error.html",Message = "Username is mandatory for signup.")
    if not request.form.get("pwd"):
        return render_template("Error.html",Message = "Password is mandatory for signup.")
    
    userCheck = db.execute("SELECT * From UserInfo WHERE Username = :Username",{"Username":user}).fetchone()
    if userCheck:
        return render_template("error.html",Message = "Username already exists")
    else:
        db.execute("INSERT INTO UserInfo VALUES(:Username,:Password)",{"Username":user,"Password":pwd})
        db.commit()
        return render_template("signupSuccess.html")

@app.route("/success.html", methods = ["POST"])
def login():
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if not request.form.get("user"):
        return render_template("error.html",Message = "You didnt enter a username")
    elif not request.form.get("pwd"):
        return render_template("error.html",Message = "You didnt enter a password")

    result = db.execute("SELECT * FROM UserInfo WHERE Username = :Username AND Password = :Password",{"Username":user,"Password":pwd}).fetchall()
    if result:
        session["user"] = user
        return render_template("success.html",user = user)
    else:
        return "Wrong info."

@app.route("/display.html",methods=["POST"])
def search():
    searchElement = request.form.get("searchElement")
    results = db.execute("SELECT * FROM bookInfo WHERE Author = :Author",{"Author":searchElement}).fetchall()
    if results:
        return render_template("display.html",results = results,searchElement=searchElement)
    else:
        return "Nothing found."

@app.route("/display/<string:searchElement>",methods={"POST","GET"})
def lookup(searchElement):
    results = db.execute("SELECT * FROM bookInfo WHERE ISBN = :ISBN",{"ISBN":searchElement}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "wwQWylMTBj2TsKHWqqyLkA", "isbns": searchElement})
    averageRating = res.json()['books'][0]['average_rating']
    reviewCount = res.json()['books'][0]['reviews_count']
    if results:
        for ISBN,Title,Author,Year in results:
            reviewResults = db.execute("SELECT * FROM bookinfo JOIN User_Review ON Bookinfo.isbn=User_Review.isbn WHERE bookinfo.isbn=:ISBN",{"ISBN":ISBN}).fetchall()       
            session["ISBN"] = ISBN
            return render_template("bookPage.html",ISBN=ISBN, Title = Title, Author = Author, Year = Year, averageRating=averageRating, reviewCount = reviewCount,results = results,reviewResults = reviewResults)
    else:
        return "Nothing found."

@app.route("/bookPage", methods=["POST","GET"])
def addReview():
    ISBN = session["ISBN"]
    reviews = request.form.get("review")
    rating = request.form.get("rating")
    currentUser = session["user"]
    checkReview = db.execute("SELECT * FROM User_Review WHERE user_id = :user AND ISBN = :ISBN",{"user":currentUser,"ISBN":ISBN}).fetchone()
    if checkReview:
        return render_template("Error.html",Message = "You cannot submit more than one review for the same book.")
    else:
        db.execute("INSERT INTO User_Review VALUES(:ISBN,:Reviews,:Rating,:User_id)",{"ISBN":ISBN,"Reviews":reviews,"Rating":rating,"User_id":currentUser })
        db.commit()

    
@app.route("/api/<string:ISBN>", methods = ["GET"])
def showJSON(ISBN):
    results = db.execute("SELECT * FROM bookInfo WHERE ISBN = :ISBN",{"ISBN":ISBN}).fetchall()
    if results:
        for ISBN,Title,Author,Year in results:
            return jsonify({
                "ISBN": ISBN,
                "Title" : Title,
                "Author" : Author,
                "Year" : Year
        })
    else:
        return jsonify({"error":"No such book"}), 422

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/") 


if __name__ == "__main__":
    main()
