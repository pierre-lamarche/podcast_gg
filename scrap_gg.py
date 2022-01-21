#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 23:42:58 2022

@author: pierre
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import re
from datetime import datetime
import locale
import requests
import os
import json
import mutagen
from mutagen.easyid3 import EasyID3
import argparse
import time

locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Defines the input json file", dest='url_json',
                        default="urls.json")
    parser.add_argument("-o", "--output", help="Defines the name of the output folder", dest='folder',
                        default=".")
    args = parser.parse_args()
    folder = args.folder
    
    with open(args.url_json, 'r') as f:
        podcasts = json.load(f)
        
    for podcast in podcasts:        
        url_base = "https://www.franceinter.fr/emissions/"+podcast['url']
        
        display = Display(visible=0, size=(1024, 768))
        display.start()
        
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
        
        if not os.path.exists(f"{folder}/{album}"):
            os.mkdir(f"{folder}/{album}")
        time.sleep(2)
        
        for year in years:
            if not os.path.exists(f"{folder}/{album}/{year}"):
                os.mkdir(f"{folder}/{album}/{year}")
                time.sleep(2)
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
                
                for cast in liste_podcasts:
                    browser.get(cast)
                    date = format(datetime.strptime(browser.find_element(By.CLASS_NAME, 'cover-emission-period').text, '%A %d %B %Y'), "%Y-%m-%d")
                    titre = browser.find_element(By.CLASS_NAME, 'cover-emission-actions-title').text
                    titre_standardise = re.sub(r'[\\/*?:"<>|]', "", titre)
                    url_dl = browser.find_element(By.CLASS_NAME, 'replay-button').get_attribute('data-url')
                    if url_dl is None:
                        fail += [date]
                    else:
                        print(f"Écriture du fichier {folder}/{album}/{year}/{date} - {titre_standardise}.mp3")
                        r = requests.get(url_dl)
                        fileName = f"{folder}/{album}/{year}/{date} - {titre_standardise}.mp3"
                        with open(fileName, "wb") as f:
                            f.write(r.content)
                        # handle tags properly
                        try:
                            meta = EasyID3(fileName)
                        except mutagen.id3.ID3NoHeaderError:
                            meta = mutagen.File(fileName, easy=True)
                            meta.add_tags()
                        meta['title'] = titre
                        meta['album'] = album
                        meta['artist'] = podcast['artist']
                        meta['date'] = date
                        meta['copyright'] = 'Radio France'
                        meta['genre'] = 'Podcast'
                        meta['website'] = url_dl
                        meta.save(fileName, v1=2)
        
        browser.close()
        display.stop()
            