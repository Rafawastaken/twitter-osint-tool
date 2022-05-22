from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings
from bs4 import BeautifulSoup as sp
import pandas as pd
from time import sleep
import os, shutil
from .. import db
from ..models import Creds, Follower, Target

def create_driver(BASE_DIR):
    # No debugging
    options = Options()
    options.add_argument('--log-level=3')
    options.add_argument('--headless')

    driver = webdriver.Chrome(
        executable_path = BASE_DIR + r'/scripts/driver/chromedriver.exe',
        chrome_options = options
    )

    driver.maximize_window()

    return driver

def login_tt(driver, creds):
    print("Efeutar Login TT")
    try:
        driver.get('https://twitter.com/')

        # Aceitar Cookies
        sleep(2)
        driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div[2]/div[1]/div/span/span').click()
        
        # Aceder pagina de login
        sleep(1)
        driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[5]/a/div/span/span').click()
        
        # Email
        sleep(2)
        driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[5]/label/div/div[2]/div/input').send_keys(creds.get('email'))
        driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[6]/div/span/span').click()
        sleep(1)

        # Username
        sleep(2)
        try:
            driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input').send_keys(creds.get('username'))
            driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span').click()
        except:
            try:
                driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input').send_keys(creds.get('username'))
                driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div').click()
            except:
                try:
                    driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input').send_keys(creds.get('username'))
                    driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div').click()
                except:
                    print("Can't locate username input")
                    sleep(10)
        sleep(1)

        # Password
        sleep(2)
        driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input').send_keys(creds.get('passw'))
        driver.find_element_by_xpath('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/span/span').click()

        sleep(10)

        print("Login Efetuado com sucesso!")
        return True

    except Exception as e:
        print(e)
        driver.close()
        print("ERROR")
        print(e)

        return False

def webscrape(content, idx, username_scrape, BASE_DIR):
    # Webscrape users
    arr_conteudo = []    
    soup = sp(content, features='lxml')
    
    for entry in soup.find_all(class_ = 'css-1dbjc4n r-1adg3ll r-1ny4l3l'):
        try:
            # Username
            username = entry.find(class_ = 'css-4rbku5 css-18t94o4 css-1dbjc4n r-1niwhzg r-1loqt21 r-1pi2tsx r-1ny4l3l r-o7ynqc r-6416eg r-13qz1uu')["href"]
            username = username.replace("/", "") 

            # Link de Imagem
            img = entry.find(class_ = 'css-1dbjc4n r-1niwhzg r-vvn4in r-u6sd8q r-4gszlv r-1p0dtai r-1pi2tsx r-1d2f490 r-u8s1d r-zchlnj r-ipm5af r-13qz1uu r-1wyyakw')['style']
            img = img.split('"')[1].replace('_normal', '')
            
            # Link 
            link = f"https://twitter.com/{username}"
            
            # Desc perfil
            # Desc perfil
            try:
                desc = entry.find(class_ = 'css-1dbjc4n r-1iusvr4 r-16y2uox')
                desc = desc.find(class_ = 'css-901oao r-1nao33i r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-1h8ys4a r-1jeg54m r-qvutc0').text
            except:
                try:
                    desc = desc.find_all(class_ = 'css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0')[3].text
                    # entry.find_all(class_ = 'css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0')[3].text
                except:
                    desc = "None"

            obj_conteudo = {
                'username':username,
                'desc':desc,
                'link':link,
                'img':img
            }
            
            arr_conteudo.append(obj_conteudo)
        except:
            continue

        # Criar DataFrame
        df = pd.DataFrame(arr_conteudo)
        df.to_csv(f'{BASE_DIR}/scripts/temp/{username_scrape}_{idx}.csv', index=False)

def scrape_user(driver, username, BASE_DIR):
    print(f"Iniciar Scraper!\nScrapping: {username}")

    link_scrape = f"https://twitter.com/{username}/followers"
    driver.get(link_scrape)

    sleep(5)

    last_source = ''
    x = 1
    while True:
        print(f"\t->Paginas: {x}", end='\r')
        sleep(3)

        current_source = str(driver.page_source)

        if last_source == current_source:
            break

        webscrape(current_source, x, username, BASE_DIR)

        last_source = current_source
        x = x + 1

        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    driver.close() # Fechar instancia do driver

def formatar_data(username_scraped, BASE_DIR):
    # Formatar CSV
    print("")
    print("Formatar Data...")
    files = os.listdir(f'{BASE_DIR}/scripts/temp/') # Filtar num Files na Data
    df = pd.DataFrame(columns=['username','desc', 'link', 'img']) # DataFrame Final

    for file in files:
        df_add = pd.read_csv(f'{BASE_DIR}\\scripts\\temp\\{file}', encoding="utf-8")
        df = df.append(df_add)

    df.drop_duplicates(inplace=True) # Remover Duplicados
    df['desc'] = df['desc'].apply(lambda x: str(x).replace('\n', ' | ')) # Remover quebras de linha
    df.to_csv(f'{BASE_DIR}\\Data\\{username_scraped}\\{username_scraped}_followers.csv', index = False) # Guardar

    print(f"Scraper finalizado: {len(df)} users encontrados!")

def limpar_ambiente(BASE_DIR):
    # Apagar Ficheiros
    print("Apagar data temporaria")
    for filename in os.listdir(f'{BASE_DIR}\\scripts\\temp\\'):
        file_path = os.path.join(f'{BASE_DIR}\\scripts\\temp\\', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def add_database(BASE_DIR, username):
    target = Target.query.filter_by(username = username).first()
    target.followers_csv = f'{BASE_DIR}\Data\{username}\{username}_followers.csv'
    dataframe = pd.read_csv(target.followers_csv)

    for idx in dataframe.index:
        username = str(dataframe["username"][idx])
        desc = str(dataframe["desc"][idx])
        link = str(dataframe["link"][idx])
        img = str(dataframe["img"][idx])
        
        follower_entry = Follower(
            username = username,
            desc = desc,
            link = link,
            img = img,
            target = target
            )
        db.session.add(follower_entry)

    target.has_follower_scrape = 1
    db.session.commit()
    

def scrape_twitter(BASE_DIR, username_scrape):
    # Hide pandas useless warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    try:
        driver = create_driver(BASE_DIR)
        print(f"Starting Scraper: {username_scrape}")
        creds_query = Creds.query.filter_by(id = 1).first()
        creds = {
            "email":creds_query.email,
            "username":creds_query.username,
            "passw":creds_query.password
        }
        print(f"Using {creds.get('username')} account!")

        login_tt(driver, creds)
        scrape_user(driver, username_scrape, BASE_DIR)
        formatar_data(username_scrape, BASE_DIR)
        limpar_ambiente(BASE_DIR)
        add_database(BASE_DIR, username_scrape)
        
        try:
            driver.close()
        except:
            pass

        return True
    except Exception as e:
        print(e)
        return False