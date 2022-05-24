# Twitter_OSINT_Tool

## About

Twitter OSINT tool - Enables you to scrape twitters following and followers account most os their shared medias (images only) as well as gather some META information of profiles.

## Functionalities

### Follower/Followees Scrape

Uses selenium chromedriver in headless mode to webscrape the followers of an account.

### Media Webscrapping

Using nitter and chromedriver to webscrape to store in database the entire archive of a profile. It's also possible to download it directly - "Download All" button

### Reverse Search

Reverse search profile picture, username, and any media entry.

## How to Use

Eventhough this app is programmed using an webframework - Flask. I won't be uploading it because it requires to use chromedriver. Therefore, the best way to use it, it's to run it locally.
In my case, I have it running on a Raspberry Pi 4 - 2gb.


To install it, simpely do: 
<ol>
<li> python3 -m pip install -r requirements.txt </li>
<li> In tt_osint create 2 folders - key sensitive: </li>
<ol>
<li>"Data" -> Will store the CSVs and Media downloaded - it creates a folder to every profile scraped.</li>
<li>2.2 "database" -> Will store "database.db" </li>
</ol>
<li>3. python3 run.py</li>
</ol>

If it's the first time using the application in order to webscrape profiles you need to add a twitter account - Use a burner account, or something you won't mind getting blocked.
Keep in mind that sometimes the login in twitter fails, so you might need to try sometimes.

## Upcoming Features
<ol>
<li> Make notes in info page functional. </li>
<li>Make reverse search username in specific websites functional. Most of the logic is done, but want to make everything else stable before.</li>
<li> Figure out a better way to handle the error in login in selenium.</li>
</ol>