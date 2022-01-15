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

locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

years = [str(i) for i in range(2016, 2023)]
browser = webdriver.Firefox()

url_base = "https://www.franceinter.fr/emissions/la-drole-d-humeur-de-guillermo-guiz"
fail = []

if not os.path.exists("/home/pierre/Musique/La Drôle D'Humeur De Guillermo Guiz"):
    os.mkdir("/home/pierre/Musique/La Drôle D'Humeur De Guillermo Guiz")

for year in years:
    if not os.path.exists(f"/home/pierre/Musique/La Drôle D'Humeur De Guillermo Guiz/{year}"):
        os.mkdir(f"/home/pierre/Musique/La Drôle D'Humeur De Guillermo Guiz/{year}")
    browser.get(f"{url_base}/archives-{year}")
    
    # accept RGPD
    if browser.find_elements(By.ID, 'didomi-notice-agree-button'):
            button_consent = browser.find_element(By.ID, 'didomi-notice-agree-button')
            button_consent.click()
            
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
            url_dl = browser.find_element(By.CLASS_NAME, 'replay-button').get_attribute('data-url')
            if url_dl is None:
                fail += [date]
            else:
                r = requests.get(url_dl)
                with open(f"/home/pierre/Musique/La Drôle D'Humeur De Guillermo Guiz/{year}/{date} - {titre}.mp3", "wb") as f:
                    f.write(r.content)

browser.close()
            
            
            
        