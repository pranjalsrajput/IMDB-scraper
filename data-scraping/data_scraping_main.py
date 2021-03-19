import hashlib
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import mysql.connector
import urllib
import urllib.request
from multiprocessing import Pool, Value, RLock
import time

file_lock = RLock()
image_download_folder = "../posters/"
full_data_file_path = 'full_data.json'
scraped_data_file_path = 'scraped_data.json'

hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def get_html_page(url):
    req = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('noscript')]
    return soup


def scrape_data(record):
    url = record["url"]
    record_id = record["id"]
    print("Processing url: ", url)
    # mydb = createDBConnection()
    # mycursor = mydb.cursor()
    genre = 'NA'
    # url = "https://www.imdb.com/title/tt0944947/"
    movie_metadata = {}
    directors = []
    creators = []
    rating = 'NA'
    poster_url = 'NA'
    name = 'NA'
    release_year = 'NA'
    summary_text ='NA'
    casts = []
    image_extension = '.jpg'
    # try:

    soup = get_html_page(url)
    time.sleep(0.5)

    if len(soup.find_all('div', {'class': 'poster'})) != 0:
        poster_url = soup.find_all('div', {'class': 'poster'})[0].find_all('img')[0]['src']
        # image_name = name.strip().replace(" ", "_")
        # image_name = image_name.replace("/", "_")
        # image_name = image_name.replace("\\", "_")
        image_download_path = image_download_folder + record_id + image_extension
        urllib.request.urlretrieve(poster_url, image_download_path)

        if len(soup.find_all('div', {'class': 'title_wrapper'})) != 0:
            genre = ''
            for i in range(len(soup.find_all('div', {'class': 'title_wrapper'})[0].find_all('a'))):
                val = soup.find_all('div', {'class': 'title_wrapper'})[0].find_all('a')[i].text
                if i == 0:
                    genre = genre + val
                if i != 0 and i != len(soup.find_all('div', {'class': 'title_wrapper'})[0].find_all('a')) - 1:
                    genre = genre + "_" + val

        if len(soup.find_all('div', {'class': 'heroic-overview'})) != 0:
            name = soup.find_all('div', {'class': 'heroic-overview'})[0].find_all('h1')[0].contents[0]

        movie_metadata["id"] = record_id
        movie_metadata['name'] = name.strip()
        movie_metadata['genre'] = genre
        movie_metadata['img_path'] = image_download_path
        movie_metadata['poster_url'] = poster_url

        if len(soup.find_all('span', {'id': 'titleYear'})) != 0:
            release_year = soup.find_all('span', {'id': 'titleYear'})[0].text[1:-1]
        else:
            if len(soup.find_all('div', {'id': 'titleDetails'})) != 0:
                for i in range(len(soup.find_all('div', {'id': 'titleDetails'})[0].find_all('div', {'class': 'txt-block'}))):
                    if (soup.find_all('div', {'id': 'titleDetails'})[0].find_all('div', {'class': 'txt-block'})[i].text.split(
                            ':')[0].strip() == 'Release Date'):
                        release_year = \
                            soup.find_all('div', {'id': 'titleDetails'})[0].find_all('div', {'class': 'txt-block'})[
                                i].text.split(
                                ':')[1].split("\n")[0].strip()
                        break

        movie_metadata['release_year'] = release_year

        if (len(soup.find_all('span', {'itemprop': 'ratingValue'})) != 0):
            rating = soup.find_all('span', {'itemprop': 'ratingValue'})[0].text
        movie_metadata['rating'] = rating

        if (len(soup.find_all('div', {'class': 'summary_text'})) != 0):
            summary_text = str(soup.find_all('div', {'class': 'summary_text'})[0].text).strip()
        movie_metadata['summary_text'] = summary_text

        if (len(soup.find_all('div', {'class': 'credit_summary_item'})) != 0):
            for i in range(len(soup.find_all('div', {'class': 'credit_summary_item'}))):
                if ('Director' in str(soup.find_all('div', {'class': 'credit_summary_item'})[i])):
                    directors_ = soup.find_all('div', {'class': 'credit_summary_item'})[i].find_all('a')
                    for director_ in directors_:
                        directors.append(director_.text.strip())
                if ('Creator' in str(soup.find_all('div', {'class': 'credit_summary_item'})[i])):
                    producers = soup.find_all('div', {'class': 'credit_summary_item'})[i].find_all('a')
                    for producer in producers:
                        creators.append(producer.text.strip())
                if ('Stars:' in str(soup.find_all('div', {'class': 'credit_summary_item'})[i])):
                    cast_list = soup.find_all('div', {'class': 'credit_summary_item'})[i].find_all('a')
                    for cast in cast_list:
                        if (cast.text != 'See full cast & crew'):
                            casts.append(cast.text.strip())
        movie_metadata['directors'] = directors
        movie_metadata['creators'] = creators
        movie_metadata['casts'] = casts
        movie_metadata['url'] = url

        write_json_data(movie_metadata, 'movies_metadata.json')

        del movie_metadata, name, release_year, rating, poster_url, image_extension, summary_text, casts, directors
        del creators, url, record_id
        # file.close()
        with file_lock:
            print("******* write ***********")
            write_json_data(dic=record, file_name=scraped_data_file_path)
    else:
        print('Poster not found for record: ',record_id)

    # except:
    #     print("An exception occurred")


def get_driver():
    # Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    DRIVER_PATH = '/home/pranjal/Downloads/chromedriver'
    browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    return browser


def createDBConnection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="shivangi",
        password="Pranjal_001",
        database="MOVIES"
    )
    print("DB created")
    return mydb


def insertQuery(val, mydb):
    mycursor = mydb.cursor()
    sql = "INSERT INTO moviegenres (record_id, movie_name, url, genre) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, val)
    mydb.commit()


def read_json_data(file_name):
    with open(file_name) as f:
        data_list = [json.loads(line) for line in f]
        return data_list


def write_json_data(dic, file_name, mode='a'):
    with open(file_name, mode) as output_file:
        json.dump(dic, output_file)
        output_file.write(os.linesep)
    output_file.close()


def filter_out_scraped_data():
    print("Filtering data")
    filtered_list = []
    full_data = read_json_data(full_data_file_path)
    # scraped_data = read_json_data(scraped_data_file_path)
    completed_lines_hash = set()

    # 3
    # scraped_data = open(scraped_data_file_path, "r")

    # 4
    for line in open(scraped_data_file_path, "r"):
        # 5
        hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
        completed_lines_hash.add(hashValue)

    for line in open(full_data_file_path, "r"):
        # 5
        hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
        # 6
        if hashValue not in completed_lines_hash:
            filtered_list.append(json.loads(line))

    # x = [i for i in full_data if i not in scraped_data]
    return filtered_list


if __name__ == "__main__":
    filtered_list = filter_out_scraped_data()
    print("Scraping Start")
    with Pool(processes=50) as p:
        p.map(scrape_data, filtered_list)
    print("Scraping Done")
    p.close()
    p.join()
