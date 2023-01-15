import os
import re
import json
import requests
from flask import render_template, redirect, url_for
from flask_login import current_user
from project.forms import SearchForm, SearchChampionForm
from project.models import User, UserFavourite
from project import db

api_key = os.environ.get("API_KEY_RIOT")


def render_template_form(template, **kwargs):
    search_form = SearchForm()
    search_champion_form = SearchChampionForm()
    username = search_form.search_user.data
    champion = search_champion_form.search_champion.data
    if username:
        return redirect(url_for("find_user", username=username))
    if champion:
        return redirect(url_for("find_champion", champion=champion))
    return render_template(template, search_form=search_form,
                           search_champion_form=search_champion_form, **kwargs)


def data_returner(uri):
    try:
        response = requests.get(uri)
    except requests.ConnectionError:
        return "Error"
    if response.status_code >= 400:
        return "Error"
    json_response = response.text
    data = json.loads(json_response)
    return data


def player_information(participants, puuid):
    placement = ""
    last_round = ""
    level = ""
    champions = []
    for participant in participants:
        if participant["puuid"] == puuid:
            placement = participant["placement"]
            last_round = participant["last_round"]
            level = participant["level"]
            for champion in participant["units"]:
                champion_id = champion["character_id"]
                champion_name = re.sub("TFT\d[a-z]*_", "", champion_id)
                if "Dragon" in champion_name:
                    continue
                tier = champion["tier"]
                try:
                    item_names = champion["itemNames"]
                    item_names = [re.sub("TFT(\d)*_Item_", "", item) for item in item_names]
                    names = [' '.join(re.findall('[A-Z][^A-Z]*', name)) for name in item_names]
                    item_names = [item.lower() for item in item_names]
                    item_names = [i for i in zip(item_names, names)]
                except KeyError:
                    item_names = []
                    names = []
                champions.append({
                    "champion_name": champion_name,
                    "tier": tier,
                    "items_name": item_names,
                    "names": names
                })
            break
    info = {
        "placement": placement,
        "last_round": last_round,
        "level": level,
        "champions": champions
    }
    return info


def find_user_matches(username):
    uri = f"https://eun1.api.riotgames.com/tft/summoner/v1/summoners/by-name/{username}" \
          f"?api_key={api_key}"
    data = data_returner(uri)
    if data == "Error":
        return render_template_form("user_info.html", error={"error": "User not found"})
    puuid = data["puuid"]

    start = 0
    count = 20
    uri = f"https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/" \
          f"ids?start={start}&count={count}&api_key={api_key}"
    data = data_returner(uri)
    if data == "Error":
        return render_template_form("user_info.html", error={"error": "Connection Error"})
    if not data:
        return render_template_form("user_info.html", error={"error": "Player doesn't play"})

    match_history = []
    for game in data:
        uri = f"https://europe.api.riotgames.com/tft/match/v1/matches/{game}?api_key={api_key}"
        match = data_returner(uri)
        if match == "Error":
            return render_template_form("user_info.html", error={"error": "Connection Error"})
        match_history.append(player_information(match["info"]["participants"], puuid))

    return match_history


def check_favourites(name, is_player):
    if current_user.is_authenticated:
        for f in current_user.favourites:
            if is_player:
                if f.is_player:
                    if f.name.lower() == name.lower():
                        return True
            else:
                if not f.is_player:
                    if f.name.lower() == name.lower():
                        return True

    return False


def delete_favourite(name):
    user = User.query.filter_by(email=current_user.email).first()
    for fav in user.favourites:
        if fav.name == name:
            to_delete = UserFavourite.query.filter_by(id=fav.id).first()
            db.session.delete(to_delete)
            db.session.commit()


def add_favourite(name, is_player):
    favourite = UserFavourite(name=name, is_player=is_player)
    user = User.query.filter_by(email=current_user.email).first()
    user.favourites.append(favourite)
    db.session.add(user)
    db.session.add(favourite)
    db.session.commit()
