from flask import Blueprint, jsonify, redirect, render_template, request, flash, url_for, jsonify
from sqlalchemy import func
from zmq import has

from .models import Target, Media, Creds
from .scripts import tt_scraper_following, tt_scraper_followers, metadata_scrape, create_folder, nitter_scrape_media
from . import db

from time import sleep
import pandas as pd 

import shutil # Delte folders + content
import json # Json request
import os # System files

# Config Views
views = Blueprint('views', __name__)

# Const
BASEDIR = os.path.abspath(os.path.dirname(__file__))
PER_PAGE_PROFILE = 20
PER_PAGE_MEDIA = 24

############# * Functions * #############

# Function to create essential Folder
def create_profile(username):
    try:
        metadata_scrape.metadata_scrape(username)
        create_folder.create_folder(username, BASEDIR)
        print("Profile Created!")
    except Exception as e:
        print(e)
        return redirect(url_for('views.error_page'))


############# * Common Error Views * #############

# Error Pages
@views.route("/error-scraping")
def error_page():
    return render_template("error.html")

# Private profile
@views.route("/private-profile")
def private_profile():
    return render_template("private_profile.html")


############# * Add Creds to database * #############

@views.route('/add-creds', methods=['GET', 'POST'])
def add_creds():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        email = request.form.get('email').lower()
        password = request.form.get('password').lower()

        creds = Creds.query.filter_by(id = 1).first()
        if creds:
            print("Updating Creds")
            creds.username = username
            creds.email = email
            creds.password = password
            db.session.commit()
        else:
            new_creds = Creds(
                username = username,
                email = email,
                password = password
            )
            db.session.add(new_creds)
            db.session.commit()


        

    return render_template('add_creds.html')


############# * Landing Page * ############

# List of Targets
@views.route('/')
def landing_page():
    has_query = False
    page = request.args.get('page', 1, type=int)
    targets = Target.query.order_by(Target.id.desc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    return render_template('home.html', targets = targets, has_query = has_query)

# List Page with query order
@views.route('/order_by_<string:type>/<string:direction>')
def landing_page_order(type, direction):
    page = request.args.get('page', 1, type=int)    
    has_query = False

    if type == "id" and direction == "asc":
        targets = Target.query.order_by(Target.id.asc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    elif type == "id" and direction == "desc":
        targets = Target.query.order_by(Target.id.desc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    elif type == "username" and direction == "asc":
        targets = Target.query.order_by(func.lower(Target.username).asc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    elif type == "username" and direction == "desc":
        targets = Target.query.order_by(func.lower(Target.username).desc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    elif type == "fav" and direction == "asc":
        targets = Target.query.order_by(Target.is_favorite.asc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    elif type == "fav" and direction == "desc":
        targets = Target.query.order_by(Target.is_favorite.desc()).paginate(page = page, per_page = PER_PAGE_PROFILE)

    return render_template('home.html', targets = targets, has_query = has_query)

# Search target engine
@views.route('/search', methods=['GET', 'POST'])
def filter_search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('search-query')
    if not query:
        flash("No input added")
        return redirect(url_for('views.landing_page'))
    has_query = True
    targets = Target.query.filter(Target.username.contains(query))
    targets = targets.paginate(page = page, per_page = PER_PAGE_PROFILE)

    return render_template('home.html', targets = targets, has_query = has_query)

############# * Info Page * #############

# Form to get info
@views.route("/get-info-scrape", methods = ['GET', 'POST'])
def get_info():
    if request.method == 'POST':
        username = request.form.get('username')
        target = Target.query.filter_by(username = username).first()
        if not target:
            create_profile(username)
            sleep(1) # Prevent redirect before page be complete
        return redirect(url_for('views.profile_info', username = username))
    return render_template("form-info-scrape.html")

# Info Page
@views.route('/profile-info/<string:username>')
def profile_info(username):
    profile = Target.query.filter_by(username=username).first()
    if not profile:
        create_profile(username)
        sleep(3)
        profile = Target.query.filter_by(username=username).first()
        return render_template("info.html", profile = profile)
    return render_template("info.html", profile = profile)


############# * Following * #############

# Following FORM get target username
@views.route('/following-scrape', methods = ['POST', 'GET'])
def following_scrape():
    if request.method == 'POST':
        username = request.form.get('username')
        if not Target.query.filter_by(username = username).first():
            create_profile(username)
        return redirect(url_for('views.scrape_following', username = username))
    return render_template("form-following-scrape.html")

# Following Scrape
@views.route('/scrape-following/<string:username>')
def scrape_following(username):
    try:
        try:
            target = Target.query.filter_by(username = username).first()
            creds = Creds.query.first()

            if not creds:
                flash("Need to add twitter account to use scrappers...", category='danger')
                return redirect(url_for('views.add_creds'))

            if target.is_private == 1:
                return redirect(url_for('views.private_profile'))
            if target.has_following_scrape == 0:
                status = tt_scraper_following.scrape_twitter(BASEDIR, username)
                if status:
                    target.has_following_scrape = 1
                    target.following_csv = f"Data/{username}/{username}_following.csv"
                    db.session.commit()
                    return redirect(url_for('views.following_list', username = target.username))
                else:
                    flash("Something went wrong while scraping...Try again", category='danger')
                    return redirect(url_for("views.profile_info", username = target.username))
        except:
            create_profile(username)
            return redirect(url_for('views.scrape_following', username = username))
        target = target.query.filter_by(username = username).first()
        return redirect(url_for("views.following_list", username = target.username ))
    except Exception as e:
        flash("Something went wrong while scraping...Try again", category='danger')
        return redirect(url_for("views.profile_info", username = target.username))

# Following List
@views.route("/following-list/<string:username>")
def following_list(username):
    target = Target.query.filter_by(username = username).first()
    df = pd.read_csv(f"{BASEDIR}\{target.following_csv}")
    following = []
    for idx in df.index:
        obj = {
            "entry":idx,
            "username":df['username'][idx],
            "desc":df['desc'][idx],
            "link":df['link'][idx],
            "img":df['img'][idx]
        }
        following.append(obj)
    return render_template('following-list.html', following = following, target = target)


############# * Followers * #############

# ! MISSING Followers Form Scrape 
@views.route('/followers-scrape', methods = ['POST', 'GET'])
def followers_scrape():
    if request.method == 'POST':
        username = request.form.get('username')
        if not Target.query.filter_by(username = username).first():
            create_profile(username)
        return redirect(url_for('views.scrape_followers', username = username))
    return render_template("form-follower-scrape.html")

# Followers Scrape
@views.route('/scrape-followers/<string:username>')
def scrape_followers(username):
    try:
        try:
            target = Target.query.filter_by(username = username).first()
            creds = Creds.query.first()

            if not creds:
                flash("Need to add twitter account to use scrappers...", category='danger')
                return redirect(url_for('views.add_creds'))

            if target.is_private == 1:
                return redirect(url_for('views.private_profile'))
            if target.has_follower_scrape == 0:
                status = tt_scraper_followers.scrape_twitter(BASEDIR, username)
                if status:
                    target.has_follower_scrape = 1
                    target.followers_csv = f"Data/{username}/{username}_followers.csv"
                    db.session.commit()
                    return redirect(url_for('views.follower_list', username = target.username))
                else:
                    flash("Something went wrong while scraping...Try again", category='danger')
                    return redirect(url_for("views.profile_info", username = target.username))
        except:
            create_profile(username)
            return redirect(url_for('views.scrape_following', username = username))
        target = target.query.filter_by(username = username).first()
        return redirect(url_for("views.follower_list", username = target.username ))
    except Exception as e:
        print(e)
        flash("Something went wrong while scraping...Try again", category='danger')
        return redirect(url_for("views.error_page", e = e))

# Follower List
@views.route("/follower-list/<string:username>")
def follower_list(username):
    target = Target.query.filter_by(username = username).first()
    df = pd.read_csv(f"{BASEDIR}\{target.followers_csv}")

    followers = []
    for idx in df.index:
        obj = {
            "entry":idx,
            "username":df['username'][idx],
            "desc":df['desc'][idx],
            "link":df['link'][idx],
            "img":df['img'][idx]
        }
        followers.append(obj)

    return render_template('follower-list.html', followers = followers, target = target)


############# * Media * #############

# Media Scrape Form
@views.route('/media-scrape', methods = ['POST', 'GET'])
def media_scrape():
    if request.method == 'POST':
        username = request.form.get('username')
        if not Target.query.filter_by(username = username).first():
            create_profile(username)
        return redirect(url_for('views.scrape_media', username = username))
    return render_template("form-media-scrape.html")

# Media Scrape
@views.route('/scrape-media/<string:username>')
def scrape_media(username):
    username = username.lower()
    target = Target.query.filter_by(username = username).first()
    if not target:
        create_profile(username)
        return redirect(url_for('views.scrape_media', username = username))
    if target.has_media_scrape == 0:
        status_media_scrape = nitter_scrape_media.get_media(username, BASEDIR)
        if status_media_scrape:
            target.has_media_scrape = 1
            target.media_csv = f"Data/{username}/{username}_media.csv"
            target.media_path_download = f'{BASEDIR}\data\{username}\media'
            db.session.commit()
            return redirect(url_for('views.media_list', username = username))
    else:
        return redirect(url_for("views.media_list", username = username))
    return redirect(url_for('views.error_page'))

# Media Display
@views.route('/media/<string:username>')
def media_list(username):
    page = request.args.get('page', 1, type=int)
    target = Target.query.filter_by(username = username).first()

    #  page = request.args.get('page', 1, type=int)
    #  targets = Target.query.order_by(Target.id.desc()).paginate(page = page, per_page = PER_PAGE_PROFILE)
    

    if target.has_media_scrape:
        media = Media.query.filter_by(target_id = target.id)
        total_media = Media.query.filter_by(target_id = target.id).count()
        media = media.paginate(page = page, per_page = PER_PAGE_MEDIA)
        return render_template('media_list.html', media = media, target = target, total_media = total_media)      
    
    flash(f"{username.title()} doesn't have media scrape. Scrapping now", category="danger")
    return redirect(url_for("views.error_page"))
        

############# * JSON Requests * #############

# Delete entry . Only needs to be a POST
@views.route("/delete-entry", methods=['POST'])
def delete_entry():
    target = json.loads(request.data)
    target_id = target['entry_id']

    target = Target.query.get(target_id)
    media_delete = Media.query.filter_by(target_id = target_id).all()

    if target: 
        try:
            shutil.rmtree(f"{BASEDIR}\data\{target.username}")
            print("Deleted with success!")
        except:
            print("Directory doesn't exist")
        # remove entry from database 
        try:
            for m_del in media_delete: # Iterate through media inputs delete
                db.session.delete(m_del)

            db.session.delete(target)
            db.session.commit()
        except Exception as e:
            print(e)
    return jsonify({})

# Add profile to favorite
@views.route('/add-favorite', methods = ['POST'])
def add_favorite():
    target = json.loads(request.data)
    target_id = target['id']

    target_fav_status = Target.query.get(target_id)
    if target_fav_status.is_favorite == 0:
        target_fav_status.is_favorite = 1
    else:
        target_fav_status.is_favorite = 0
    
    db.session.commit()

    return jsonify({})

