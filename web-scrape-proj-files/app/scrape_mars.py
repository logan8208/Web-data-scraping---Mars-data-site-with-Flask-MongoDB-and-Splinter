#!/usr/bin/env python
# coding: utf-8

#
#
#
#
#                                               Logan Caldwell, 2019
#
#
#
#

# Importing dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt

#
#
#
# MASTER SCRAPE FUNCTION combining all retrieval functions:
#
#
#

def scrape_all():

      # Initiating headless driver for deployment
      browser = Browser("chrome", executable_path="chromedriver", headless=True)
      news_title, news_paragraph = mars_news(browser)

      # Running all scraping functions and storing in dictionary.
      data = {
            "news_title": news_title,
            "news_paragraph": news_paragraph,
            "featured_image": featured_image(browser),
            "hemispheres": hemispheres(browser),
            "weather": twitter_weather(browser),
            "facts": mars_facts(),
            "last_modified": dt.datetime.now()
      }

      # Stopping webdriver and returning all data
      browser.quit()
      return data

#
#
#
#                                               To mars news site
#
#
#

def mars_news(browser):

      url = 'https://mars.nasa.gov/news/'
      browser.visit(url)

      # Safe delay while loading the page
      browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

      # Convert the html to soup object

      html = browser.html
      news_soup = bs(html, 'html.parser')

      # Try/except process for obtaining news titles and para's:

      try:
            slide_elem = news_soup.select_one('ul.item_list li.slide')

            # Using parent element to find the first 'a' tag and saving it as `news_title`
            news_title = slide_elem.find("div", class_='content_title').get_text()

            # Using parent element to find paragraph text
            news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

      except AttributeError:
            return None, None

      return news_title, news_p

#
#
#
#                                  Get featured images - Twitter site
#
#
#

def featured_image(browser):

      # Linking url to splinter via browser/chromedriver

      url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
      browser.visit(url)

      # Finding full image button; clicking it

      full_image_elem = browser.find_by_id('full_image')
      full_image_elem.click()

      # Finding more info button; clicking it

      browser.is_element_present_by_text('more info', wait_time=1)
      more_info_elem = browser.find_link_by_partial_text('more info')
      more_info_elem.click()

      # Parsing the resulting html with soup (bs)

      html = browser.html
      img_soup = bs(html, 'html.parser')
      
      # finding the relative image url
      img = img_soup.select_one('figure.lede a img')

      # try/except for obtaining image url link

      try:
            img_url_rel = img.get("src")

      except AttributeError:
            return None

      # Using the base url to create an absolute url
      img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
      return img_url

#
#
#
#                                        Get mars weather
#
#
#

def twitter_weather(browser):

      url = 'https://twitter.com/marswxreport?lang=en'
      browser.visit(url)

      # Retrieving html code and parsing via BeautifulSoup (bs)

      html = browser.html
      weather_soup = bs(html, 'html.parser')

      # Finding a tweet with the "data-name" ≡ "Mars Weather"

      mars_weather_tweet = weather_soup.find('div', attrs={"class": "tweet", "data-name": "Mars Weather"})

      # Searching within the tweet for the p tag containing the tweet text

      mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
      return mars_weather

#
#
#
#                                       Get mars hemisphere images
#
#
#

def hemispheres(browser):

      url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
      browser.visit(url)

      # Looping through those links, clicking the link, finding the sample anchor, returning the href

      hemisphere_image_urls = []
      
      for i in range(4):

            # Finding elements on each loop of for loop to avoid stale element exception
            browser.find_by_css("a.product-item h3")[i].click()
            
            hemi_data = scrape_hemisphere(browser.html) # See scrape_hemisphere func below this func
            
            # Appending hemisphere object to list
            hemisphere_image_urls.append(hemi_data)
            
            # Navigating backwards
            browser.back()

      return hemisphere_image_urls

#
#
#
#                                        Scrap hemi func to be called by hemispheres func:
#
#
#

def scrape_hemisphere(html_text):

    # Soupify-ing the html text
    hemi_soup = bs(html_text, "html.parser")

    # Trying to get href and text except if error.
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere

#
#
#
#                                               Get mars facts
#
#
#

def mars_facts():

      # Try/except for reading html to pandas:

      try:
            df = pd.read_html('https://space-facts.com/mars/')[0]
      except BaseException:
            return None

      df.columns=['description', 'value']
      df.set_index('description', inplace=True)

      # Returning table in html format with added Bootstrap styling:

      return df.to_html(classes="table table-striped table-dark")

if __name__ == "__main__":

      # Printing scraped data (if running as script)
      print(scrape_all())