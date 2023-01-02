import os
from flask import flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from project import app, db, bcrypt
from project.utilities import (
    data_returner, render_template_form, check_favourites,
    find_user_matches, delete_favourite, add_favourite
)
from project.forms import RegistrationForm, LoginForm
from project.models import User, UserFavourite

api_key = os.environ.get("API_KEY_RIOT")


@app.route("/", methods=["GET", "POST"])
def home():
    uri = f"https://eun1.api.riotgames.com/tft/league/v1/challenger?api_key={api_key}"
    data = data_returner(uri)
    if data == "Error":
        return render_template_form("Connection Error")
    summoners = []
    for summoner in data["entries"]:
        name = summoner["summonerName"]
        wins = summoner["wins"]
        losses = summoner["losses"]
        win_ratio = round(wins / (wins + losses) * 100, 2)
        summoners.append({"name": name, "win_ratio": win_ratio})
    return render_template_form("home.html", summoners=summoners)


@app.route("/find_user/<string:username>/", methods=["GET", "POST"])
def find_user(username):
    username = username.lower()
    match_history = find_user_matches(username)

    values = [values for values in request.values.values()]
    if request.method == "POST" and "watch" in values[0]:
        if check_favourites(username, True):
            delete_favourite(username)
        elif not check_favourites(username, True):
            add_favourite(username, True)

        return redirect(url_for("find_user", username=username))

    favourite = {"favourite": check_favourites(username, True)}

    return render_template_form("user_info.html", match_history=match_history,
                                username=username, favourite=favourite)


@app.route("/champion/<string:champion>/", methods=["GET", "POST"])
def find_champion(champion):
    uri = f"https://eun1.api.riotgames.com/tft/league/v1/challenger?api_key={api_key}"
    data = data_returner(uri)
    if data == "Error":
        return render_template_form("Connection Error")
    summoners = []
    for summoner in data["entries"]:
        summoners.append(summoner["summonerName"])

    match_history = []

    for summoner in summoners[:2]:
        match_history.append(find_user_matches(summoner))

    items = {}

    for matches in match_history:
        for match in matches:
            if match["placement"] < 5:
                for champ in match["champions"]:
                    if champ["champion_name"].lower() != champion.lower():
                        for item in champ["items_name"]:
                            if items.get(item) is None:
                                items[item] = 1
                            else:
                                items[item] += 1

    items_list = [k for k, v in sorted(items.items(), key=lambda i: i[1], reverse=True)]
    items_list = items_list[:3]

    values = [values for values in request.values.values()]
    if request.method == "POST" and "watch" in values[0]:
        if check_favourites(champion, False):
            delete_favourite(champion)
        elif not check_favourites(champion, False):
            add_favourite(champion, False)

        return redirect(url_for("find_champion", champion=champion))

    favourite = {"favourite": check_favourites(champion, False)}

    return render_template_form("champion.html", items_list=items_list, champion=champion,
                                favourite=favourite)


@app.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created!", "success")
        return redirect(url_for('home'))
    return render_template_form('register.html', form=form)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
        flash("Invalid email or password!", "danger")
    return render_template_form("login.html", form=form)


@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/favourite/")
@login_required
def favourite():
    favourites_list = []
    fav = UserFavourite.query.filter_by(user_id=current_user.id).all()
    for f in fav:
        favourites = {"name": f.name, "is_player": f.is_player}
        favourites_list.append(favourites)
    return render_template_form("favourites.html", favourites_list=favourites_list)
