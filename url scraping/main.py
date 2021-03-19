import csv
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import mysql.connector

# no_of_requests = 2219  # Action genre
no_of_requests = 3707  # Sci-Fi genre
# no_of_requests = 101  # Action genre
global chrome_driver

def scrape_data(url, driver):
    mydb = createDBConnection()
    mycursor = mydb.cursor()
    for request_no in range(1865, no_of_requests):
        print("Request: ",request_no," Processing page: ", url,"\n")
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        record_list = soup.find_all('img',{'class':'loadlate'})
        with open('sci-fi_movies_list.json', 'a',  encoding='utf-8') as file:
            for record in record_list:
                movie = {}
                movie_id = record.attrs['data-tconst']
                movie_name = record.attrs['alt']
                movie["id"] = movie_id
                movie["movie_name"] = movie_name
                movie["url"] = "https://www.imdb.com/title/"+movie_id+"/?ref_=adv_li_i"
                val = (movie_id, movie_name, movie["url"], "Sci-Fi")
                insertQuery(val, mydb)
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

    url ="https://www.imdb.com/search/title/?genres=sci-fi&after=WzkyMjMzNzIwMzY4NTQ3NzU4MDcsInR0MTEyMzE2MzgiLDkzMjAxXQ%3D%3D&explore=title_type,genres&ref_=adv_nxt"
    chrome_driver = get_driver()
    scrape_data(url, chrome_driver)
    print("Scraping Done")

