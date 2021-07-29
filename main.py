from flask import Flask, render_template,redirect,url_for, request, session, flash, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import joblib

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)
main_data_set_to_sql = pd.read_pickle(r"C:\Users\rejks\Desktop\Python\Flask\dummy.pkl")
model = joblib.load(r"C:\Users\rejks\Desktop\Python\Flask\movie-recomender")

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self,name, email, password):
        self.name = name
        self.email = email
        self.password = password


@app.route('/')
def home():
    if "user" in session:
        user = session["user"]
        flash("You are  logged in")
        return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())


@app.route("/login", methods=["POST","GET"])
def login():
    if "user" in session:
        flash("Already logged in!")
        return redirect(url_for("home"))
    else:
        if request.method =="POST":
            session.permanent = True
            user = request.form["nm"]
            session["user"] = user
            user_password = request.form["password_input"]
            login_or_register = request.form["login"]

            if login_or_register == "login":
                found_user = users.query.filter_by(name=user).first()
                try:
                    if user_password == found_user.password:
                        session['logged_in'] = True
                        return redirect(url_for("home"))
                except:
                    flash("Bad password")
                    return render_template("index.html")
            else:
                return redirect(url_for("register"))
        else:
            return render_template("login.html")


@app.route("/register", methods=["POST","GET"])
def register():
    if "user" in session:
        flash("Already logged in!")
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            session.permanent = True
            user = request.form["nm"]
            session["user"] = user
            user_password = request.form["password_input"]
            user_email = request.form["email_input"]
            login_or_register = request.form["login"]
            if login_or_register == "register":
                usr = users(user,user_email,user_password)
                db.session.add(usr)
                db.session.commit()
                flash("Login Succesful!")
                session['logged_in'] = True
                return redirect(url_for("home"))
            else:
                return render_template("register.html")
        else:
            return render_template("register.html")


@app.route("/logout")
def logout():
    flash(f'You have been logged out', "info")
    session.pop("user", None)
    session.pop("email", None)
    session['logged_in'] = False
    return redirect(url_for("home"))


@app.route('/web', methods=["POST","GET"])
def web():
    predictions = "None"
    if request.method=="POST":
        movie_title = request.form["movie_title"]
        recomender = main_data_set_to_sql.loc[main_data_set_to_sql["primaryTitle"] == movie_title].values.tolist()
        s = recomender[0][3:6]
        recomender_format = [s[0] * 0.9, s[1] * 1.1, s[2]], [s[0] * 1.1, s[1] * 0.9, s[2]]
        predictions = model.predict(recomender_format)
        return render_template("movies.html", result=predictions)
    else:
        return render_template("movies.html", result =predictions )


@app.route('/predict_api', methods=["POST"])
def predict_api():
    movie_title = request.args.get('name')
    recomender = main_data_set_to_sql.loc[main_data_set_to_sql["primaryTitle"] == movie_title].values.tolist()
    s = recomender[0][3:6]
    recomender_format = [s[0] * 0.9, s[1] * 1.1, s[2]], [s[0] * 1.1, s[1] * 0.9, s[2]]
    predictions = model.predict(recomender_format)
    api_recomendation = predictions.tolist()
    return jsonify(api_recomendation)



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)