from optparse import Option
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup as sp
import pandas as pd

from time import sleep

from .. import db
from ..models import Target, Media

def create_driver(BASEDIR):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')

    executable_path = BASEDIR + r'/scripts/driver/chromedriver.exe'

    driver = webdriver.Chrome(executable_path = executable_path, chrome_options = options)

    return driver

def add_database(username, df):
    target = Target.query.filter_by(username = username).first()
    for idx in df.index:
        media_entry = Media(
            date = df["date"][idx],
            desc = df['desc'][idx],
            link = df['link'][idx],
            img = df['img'][idx],
            target = target
            )
        db.session.add(media_entry)
    db.session.commit()

def get_media(username, BASEDIR):
    try:
        complete_link = f"https://nitter.net/{username}/media"    
    
        driver = create_driver(BASEDIR)
        driver.get(complete_link)

        arr_content = []
        x = 0

        while True:
            sleep(2)
            content = driver.page_source
            soup = sp(content, features='lxml')
            items = soup.find_all(class_ = 'timeline-item')

            for item in items:
                try:
                    date = item.find(class_ = 'tweet-date').find("a")['title']
                    date = date.split('·')[0]
                except:
                    date = None

                try: 
                    desc = item.find(class_ = 'tweet-content media-body').text
                except:
                    desc = None

                try:
                    link_tweet = item.find(class_ = 'tweet-link')['href']
                    post_link = "https://twitter.com" + link_tweet
                    post_link = post_link.replace('#m', '')
                    
                    imgs = item.find_all(class_ = 'attachment image')
                    try:
                        for img in imgs:
                            img_query = img.find('a')['href']
                            img_link = f"https://nitter.net{img_query}"

                            entry_obj = {
                                'date':date,
                                'desc':desc,
                                'link':post_link,
                                'img':img_link
                            }

                            arr_content.append(entry_obj)
                            print(f"Found: {x}", end = '\r' )
                            x = x + 1

                    except Exception as e:
                        print(e)
                        continue
                    
                except:
                    continue

            try:
                next_page = driver.find_element_by_link_text('Load more')
                next_page.click()
            except:
                break

        df = pd.DataFrame(arr_content)
        df.to_csv(f'{BASEDIR}\\Data\\{username}\\{username}_media.csv', index = False) # Guardar

        # Add to database
        add_database(username, df)

        return True
    except:
        return False