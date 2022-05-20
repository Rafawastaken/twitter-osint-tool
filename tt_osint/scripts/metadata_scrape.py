from bs4 import BeautifulSoup as sp
from ..models import Target
import requests

from .. import db

def scrape(username):
    # Make GET request and intepret source
    link = f'https://nitter.net/{username}'
    r = requests.get(link)
    soup = sp(r.content, features='lxml')

    # Scrapping 
    profile_tab = soup.find(class_ = 'profile-tab sticky')
    name = profile_tab.find(class_ = 'profile-card-fullname').text

    try:
        desc = profile_tab.find(class_ = 'profile-bio').text
        desc = desc.replace('\n', ' ').replace('  ', '')
    except:
        desc = None

    try:
        website = profile_tab.find(class_ = 'profile-website').find('a')['href']
    except:
        website = None

    try:
        profile_img = profile_tab.find(class_ = 'profile-card-avatar')
        profile_img = "https://nitter.net" + profile_img['href']
    except:
        profile_img = None

    num_tweets = profile_tab.find(class_ = 'posts').find(class_ = 'profile-stat-num').text
    num_following = profile_tab.find(class_ = 'following').find(class_ = 'profile-stat-num').text
    num_followers = profile_tab.find(class_ = 'followers').find(class_ = 'profile-stat-num').text

    try:
        location = profile_tab.find(class_ = 'profile-location').text.replace('\n', '')
    except:
        location = None

    try:
        image_num = profile_tab.find(class_ = 'photo-rail-header').text
        image_num = image_num.split()[0]
    except:
        image_num = None

    try:
        profile_banner = soup.find(class_ = 'profile-banner').find("a")['href']
        profile_banner = 'https://nitter.net' + profile_banner
    except:
        profile_banner = None
        
    join_data = profile_tab.find(class_ = 'profile-joindate').text.replace(" Joined ", "")

    private = 0
    is_private = soup.find(class_ = 'timeline-header timeline-protected')
    if is_private:
        private = 1

    # End of Scrape

    # Create a metadata profile object
    profile_metadata = {
        "username":username,
        "name":name,
        "link":link,
        "desc":desc,
        "website":website,
        "profile_img":profile_img,
        "num_tweets":num_tweets,
        "num_followers":num_followers,
        "num_following":num_following,
        "location":location,
        "media_num":image_num,
        "profile_banner":profile_banner,
        "join_date":join_data,
        "private":private,
        "is_favorite":0
    }

    return profile_metadata

def metadata_scrape(username):
    try:
        meta_obj = scrape(username)
        # Create database 
        target_add = Target(
            username = username,
            is_private = meta_obj.get('private'),
            name = meta_obj.get('name'),
            link = meta_obj.get('link'),
            
            num_tweets = meta_obj.get("num_tweets"),
            
            followers = meta_obj.get('num_followers'),
            followers_csv = None,
            has_follower_scrape = 0,
        
            following = meta_obj.get('num_following'),
            following_csv = None,
            has_following_scrape = 0,

            media = meta_obj.get("media_num"),
            has_media_scrape = 0,

            img_link = meta_obj.get('profile_img'),
            banner_link = meta_obj.get('profile_banner'),

            place = meta_obj.get('location'),
            joined = meta_obj.get('join_date'),
            website = meta_obj.get('website'),
            desc = meta_obj.get('desc'),
            custom_links = None,
            custom_notes = None
        )
        # Add and save to database
        db.session.add(target_add)
        db.session.commit()

        return True
    except:
        return False

    