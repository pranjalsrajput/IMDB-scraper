import csv
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import mysql.connector
import urllib
import urllib.request

no_of_requests = 3115  # horror genre

global chrome_driver

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
    for request_no in range(1, no_of_requests):
        print("Horror: Request: ",request_no," Processing page: ", url,"\n")
        # driver.get(url)
        # soup = BeautifulSoup(driver.page_source, 'html.parser')
        soup = get_html_page(url)
        record_list = soup.find_all('img',{'class':'loadlate'})
        with open('horror_movies_list.json', 'a',  encoding='utf-8') as file:
            for record in record_list:
                movie = {}
                movie_id = record.attrs['data-tconst']
                movie_name = record.attrs['alt']
                movie["id"] = movie_id
                movie["movie_name"] = movie_name
                movie["url"] = "https://www.imdb.com/title/"+movie_id+"/?ref_=adv_li_i"
                # val = (movie_id, movie_name, movie["url"], "Sci-Fi")
                # insertQuery(val, mydb)
                json.dump(movie, file)
                file.write(os.linesep)
                del movie, movie_id, movie_name

        file.close()
        url = "https://www.imdb.com" + soup.find_all('a', {'class': 'lister-page-next next-page'})[0].attrs[
            'href']



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

    url ="https://www.imdb.com/search/title/?genres=horror&explore=title_type,genres&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3396781f-d87f-4fac-8694-c56ce6f490fe&pf_rd_r=AH5B99H1NWASSW5D5PPJ&pf_rd_s=center-1&pf_rd_t=15051&pf_rd_i=genre&ref_=ft_gnr_pr1_i_3"
    # chrome_driver = get_driver()
    # scrape_data(url, chrome_driver)
    scrape_data(url)
    print("Scraping Done")

