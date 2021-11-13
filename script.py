from bs4 import BeautifulSoup as bs
import requests
import os
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep


# web driver configuration
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.headless = True
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
ua = UserAgent(use_cache_server=False)
userAgent = ua.random
chrome_options.add_argument(f'user-agent={userAgent}')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


def get_all_gifs():
    """
    Returns all gifs URLs on a favourites page
    """

    driver.get('https://monophy.com/')
    sleep(5)
    driver.save_screenshot('screenshot1.png')
    sleep(5)

    scroll_pause_time = 3 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1
    
    # while True:
    #     # scroll one screen height each time
    #     driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    #     driver.save_screenshot('screenshot2.png')
    #     i += 1
    #     sleep(scroll_pause_time)
    #     # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    #     scroll_height = driver.execute_script("return document.body.scrollHeight;")  
    #     # Break the loop when the height we need to scroll to is larger than the total scroll height
    #     if (screen_height) * i > scroll_height:
    #         break

    sleep(5)

    gifs = driver.find_elements_by_tag_name('img')
    sleep(1)

    print(f'Downloading {len(gifs)} gifs')

    giphys_list = []
    for s in range(len(gifs)):
        try:
            postion_question_mark = gifs[s].get_attribute('src').index("?") 
            giphys_list.append(gifs[s].get_attribute('src')[:postion_question_mark])
        except ValueError:
            pass
    return giphys_list

def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)

    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, url.split("/")[-2] + '.gif')

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def main(path):
    """
    Main function to start scripts
    """
    try:
        print('Starting script and loading gifs...This might take a while because it is actually downloading all the gif monophy ever has')
        images = get_all_gifs()
        for gifs in images:
            download(gifs, path)

        print('Closing Script driver...')
        driver.close()
    except Exception as e:
        print(e)


path = input('Enter the name of the folder to store the downloaded images to\t')

# calling main function
main(path)

    