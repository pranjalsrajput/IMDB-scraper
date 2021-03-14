import json
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import mysql.connector
import urllib
import urllib.request

image_download_folder = "../posters/"

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
    # page = requests.get(url, headers=hdr).text
    soup = BeautifulSoup(page, 'html.parser')
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('noscript')]
    return soup

def scrape_data(url):
    # mydb = createDBConnection()
    # mycursor = mydb.cursor()
    genre = "Action"
    url = "https://www.imdb.com/title/tt0456257/?ref_=adv_li_tt"
    movie_metadata = {}
    director = 'NA'
    rating = 'NA'
    poster_url = 'NA'
    name='NA'
    release_year = 'NA'
    casts = []
    image_extension = '.jpg'

    soup = get_html_page(url)


    if len(soup.find_all('div', {'class': 'heroic-overview'})) != 0:
        name = soup.find_all('div', {'class': 'heroic-overview'})[0].find_all('h1')[0].contents[0]

    if len(soup.find_all('div', {'class': 'poster'}))!=0:
        poster_url = soup.find_all('div', {'class': 'poster'})[0].find_all('img')[0]['src']
        urllib.request.urlretrieve(poster_url, image_download_folder + name + "_" + genre + image_extension)
    else:
        print('Poster not found')

    movie_metadata['name'] = name.strip()
    movie_metadata['poster_url'] = poster_url

    if len(soup.find_all('span',{'id':'titleYear'}))!=0:
        release_year = soup.find_all('span',{'id':'titleYear'})[0].text[1:-1]
    else:
        for i in range(len(soup.find_all('div', {'id': 'titleDetails'})[0].find_all('div', {'class':'txt-block'}))):
            if(soup.find_all('div', {'id': 'titleDetails'})[0].find_all('div', {'class':'txt-block'})[i].text.split(':')[0].strip()=='Release Date'):
                release_year = soup.find_all('div', {'id': 'titleDetails'})[0].find_all('div', {'class': 'txt-block'})[i].text.split(
                    ':')[1].split("\n")[0].strip()
                break


    movie_metadata['release_year'] = release_year

    if (len(soup.find_all('span',{'itemprop':'ratingValue'}))!=0):
        rating = soup.find_all('span',{'itemprop':'ratingValue'})[0].text
    movie_metadata['rating'] = rating

    if (len(soup.find_all('div', {'class': 'summary_text'}))!=0):
        summary_text = str(soup.find_all('div', {'class': 'summary_text'})[0].text).strip()
    movie_metadata['summary_text'] = summary_text

    if(len(soup.find_all('div', {'class': 'credit_summary_item'}))!=0):
        for i in range(len(soup.find_all('div', {'class': 'credit_summary_item'}))):
            if('Director:' in str(soup.find_all('div', {'class': 'credit_summary_item'})[i])):
                director = soup.find_all('div', {'class': 'credit_summary_item'})[i].find('a').text
            if ('Stars:' in str(soup.find_all('div', {'class': 'credit_summary_item'})[i])):
                cast_list = soup.find_all('div', {'class': 'credit_summary_item'})[i].find_all('a')
                for cast in cast_list:
                    if (cast.text != 'See full cast & crew'):
                        casts.append(cast.text.strip())
    movie_metadata['director'] = director.strip()
    movie_metadata['casts'] = casts

    with open('movies_metadata.json', 'a', encoding='utf-8') as file:
        json.dump(movie_metadata,file)
        file.write(os.linesep)

    del movie_metadata, name, release_year, rating, poster_url, image_extension, summary_text, casts, director
    file.close()

def workbook_writer(workbook, worksheet, row, value):
    col = 0
    worksheet.write(row, col, str(value))

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
    mycursor= mydb.cursor()
    sql = "INSERT INTO moviegenres (record_id, movie_name, url, genre) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, val)
    mydb.commit()
    # print("record inserted")

if __name__ == "__main__":

    url ="https://www.imdb.com/search/keyword/?keywords=superhero&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=a581b14c-5a82-4e29-9cf8-54f909ced9e1&pf_rd_r=AH5B99H1NWASSW5D5PPJ&pf_rd_s=center-5&pf_rd_t=15051&pf_rd_i=genre&ref_=kw_nxt&sort=moviemeter,asc&mode=detail&page=1"
    # chrome_driver = get_driver()
    scrape_data(url)
    print("Scraping Done")

