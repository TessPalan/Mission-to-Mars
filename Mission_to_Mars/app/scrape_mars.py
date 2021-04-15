# Define a function called `scrape` that will execute all of your scraping code from the `mission_to_mars.ipynb` notebook and return one Python dictionary containing all of the scraped data. 

# It will be a good idea to create multiple smaller functions that are called by the `scrape()` function. 
# Remember, each function should have one 'job' (eg. you might have a `mars_news()` function that scrapes the NASA mars news site and returns the content as a list/tuple/dictionary/json)
# HINT: the headers in the notebook can serve as a useful guide to where one 'job' ends and another begins. 
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pymongo
import pandas as pd
import requests
import pathlib
import pprint

def scrape():
    results = {}
    # Path to chromedriver
    path = "/usr/local/bin/chromedriver"

    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    try: 
        news_title, news_text = get_mars_titles(browser)
        featured_image_url = get_featured_img(browser)
        html_table = get_mars_facts(browser)
        titles_planets = get_hemispheres(browser)

    except Exception as e:
        print(e)

    else:
        results["news_title"] = news_title
        results["news_text"] = news_text
        results["featured_image_url"] = featured_image_url
        results["html_table"] = html_table
        results['titles_planets'] = titles_planets
    
    return results

def get_mars_titles(browser):
    # ## Visit the NASA mars news site

    # Visit the mars nasa news site
    nasa_url = 'https://mars.nasa.gov/news/'
    # Optional delay for loading the page
    browser.visit(nasa_url)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # .find() the content title and save it as `news_title`
    news_titles = soup.find_all('div', class_='content_title')
    news_title = news_titles[1].text

    # .find() the paragraph text
    news_text = soup.find('div', class_='article_teaser_body').text

    return news_title, news_text

def get_featured_img(browser):

    # ## JPL Space Images Featured Image

    # Visit JPL space images Mars URL 
    jpl_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jpl_url)

    # Parse the resulting html with soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # find the relative image url
    soup.find('img', class_='headerimage fade-in')

    img_src = soup.find('img', 'headerimage fade-in')['src']

    # Use the base url to create an absolute url
    featured_image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_src}'
    return featured_image_url

def get_mars_facts(browser):

    # ## Mars Facts

    # Create a dataframe from the space-facts.com mars page
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)

    df = tables[1]

    # clean the dataframe and export to HTML
    to_html = df.to_html()

    html_table = to_html.replace('\n', '')
     
    return html_table

def get_hemispheres(browser):

     # ## Hemispheres

    # visit the USGS astrogeology page for hemisphere data from Mars
    usgs_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(usgs_url)


    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # First, get a list of all of the hemispheres
    hemisphere = soup.find('h3')

    hemispheres = soup.find_all('h3')
    titles = []
    for hemisphere in hemispheres:
        titles.append(hemisphere.text)

    titles = sorted(titles)

    img = soup.find('a', class_='itemLink product-item')

    imgs = soup.find_all('a', class_='itemLink product-item')
    planets = []
    for img in imgs:
        planets.append(img['href'].split('/')[-1])
    
    planets = sorted(list(set(planets)))

    titles_planets = []
    for title, planet in zip(titles,planets):
        document = {'img_url': f'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/{planet}.tif/full.jpg',
        'title': title
        } 
        titles_planets.append(document)
    
    return titles_planets

if (__name__ == '__main__'):
    scrape()