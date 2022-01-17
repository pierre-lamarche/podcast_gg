#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 23:42:58 2022

@author: pierre
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from datetime import datetime
import locale
import requests
import os
import json

locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

with open("urls.json", 'r') as f:
    podcasts = json.load(f)
    
podcast = podcasts[0]
    
url_base = "https://www.franceinter.fr/emissions/"+podcast['url']
browser = webdriver.Firefox()
browser.get(url_base)

# accept RGPD
if browser.find_elements(By.ID, 'didomi-notice-agree-button'):
        button_consent = browser.find_element(By.ID, 'didomi-notice-agree-button')
        button_consent.click()
        
# get title
album = browser.find_element(By.CLASS_NAME, 'cover-emission-title').text.lower().title()

button_archives = browser.find_element(By.CLASS_NAME, 'season-link-container-link')
button_archives.click()

years = [element.text for element in browser.find_elements(By.CLASS_NAME, 'season-cover-list-element')]
fail = []

if not os.path.exists("/home/pierre/Musique/{album}"):
    os.mkdir("/home/pierre/Musique/{album}")

for year in years:
    if not os.path.exists(f"/home/pierre/Musique/{album}/{year}"):
        os.mkdir(f"/home/pierre/Musique/{album}/{year}")
    browser.get(f"{url_base}/archives-{year}")
            
    # récupérer le nombre de pages
    if browser.find_elements(By.CSS_SELECTOR, '.pager-item.last [href]'):
        page_max = int(re.match(r'.*p=(\d+)$', browser.find_element(By.CSS_SELECTOR, '.pager-item.last [href]').get_attribute('href')).group(1))
    else:
        page_max = 1
    
    # loop over the pages
    for page in range(1, page_max+1):
        browser.get(f"{url_base}/archives-{year}?p={page}")
        liste_podcasts = [element.get_attribute('href') for element in browser.find_elements(By.CLASS_NAME, 'card-text-sub')]
        
        for podcast in liste_podcasts:
            browser.get(podcast)
            date = format(datetime.strptime(browser.find_element(By.CLASS_NAME, 'cover-emission-period').text, '%A %d %B %Y'), "%Y-%m-%d")
            titre = browser.find_element(By.CLASS_NAME, 'cover-emission-actions-title').text.replace("/", "")
            titre = re.sub(r'[\\/*?:"<>|]', "", titre)
            url_dl = browser.find_element(By.CLASS_NAME, 'replay-button').get_attribute('data-url')
            if url_dl is None:
                fail += [date]
            else:
                r = requests.get(url_dl)
                with open(f"/home/pierre/Musique/{album}/{year}/{date} - {titre}.mp3", "wb") as f:
                    f.write(r.content)

browser.close()
        