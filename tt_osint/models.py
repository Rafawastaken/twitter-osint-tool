from . import db

# Creds to be used with scrappers 
class Creds(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(40))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))

# Database entry to store scraped Targets
class Target(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(70)) # Username
    is_private = db.Column(db.Integer)
    name = db.Column(db.String(50)) # Actual Nmae
    link = db.Column(db.String(70)) # link 

    num_tweets = db.Column(db.String(20)) # Number of tweets
    
    follower_number = db.Column(db.String(10)) # Num. Followers
    followers = db.relationship('Follower', backref='target')  # * Foreign Key
    followers_csv = db.Column(db.String(100)) # CSV Followers
    has_follower_scrape = db.Column(db.Integer) # 1 has Follower scrape 0 if not
    
    following_number = db.Column(db.String(10)) # Num. Following
    followings = db.relationship('Following', backref='target')  # * Foreign Key
    following_csv = db.Column(db.String(100)) # CSV Following
    has_following_scrape = db.Column(db.Integer) # 1 has following scrape 0 if not

    media = db.Column(db.String(70)) # Num Media
    medias = db.relationship('Media', backref='target') # * Foreign Key Media
    media_csv = db.Column(db.String(70)) # Media CSV
    media_path_download = db.Column(db.String(70)) # Folder download path
    has_media_scrape = db.Column(db.Integer) # 1 has media scrape 0 if not
    
    img_link = db.Column(db.String(1000)) # Link Img
    banner_link = db.Column(db.String(1000)) # Link Banner
    
    place = db.Column(db.String(200)) # Place
    joined = db.Column(db.String(100)) # Joined in
    website = db.Column(db.String(100)) # website
    desc = db.Column(db.String(300)) # Desc profile

    custom_links = db.Column(db.String(2000)) # Other Links 
    custom_notes = db.Column(db.String(2000)) # Custom notes

    is_favorite = db.Column(db.Integer, default = 0)

# database table to store media. Has correlation with Target
class Media(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.String(50))
    desc = db.Column(db.String(300))
    link = db.Column(db.String(150))
    img = db.Column(db.String(200))
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))

# database table to sotre Followers. Has correlation with Target
class Follower(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    desc = db.Column(db.String(300))
    link = db.Column(db.String(150))
    img = db.Column(db.String(200))
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))

# database table to sotre Followings. Has correlation with Target
class Following(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    desc = db.Column(db.String(300))
    link = db.Column(db.String(150))
    img = db.Column(db.String(200))
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))