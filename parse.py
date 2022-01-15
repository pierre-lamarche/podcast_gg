# -*- coding: utf-8 -*-
"""
Created on 30/03/2021
@author: pierre
"""

rss = "http://radiofrance-podcast.net/podcast09/rss_16609.xml"

import feedparser as fp
import requests
import datetime
from os import listdir
import os
#import re

podcasts = fp.parse(rss)

chemin_dl = "/home/pierre/Musique/La Drôle D'Humeur De Guillermo Guiz"

for entry in podcasts.entries[:-1]:
    timestamp = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z').strftime("%Y-%m-%d")
    #auteur = re.match(r'^\w* : \d{2}:\d{2}:\d{2} - ([^-]*) -', entry.subtitle).group(1)
    titre = entry.title.replace('/', '')
    annee = timestamp[:4]
    if not os.path.exists(f'{chemin_dl}/{annee}'):
        os.mkdir(f'{chemin_dl}/{annee}')
    if timestamp not in [f[:10] for f in listdir(f'{chemin_dl}/{annee}')]:
        r = requests.get(entry.links[1]['href'])
        with open(f'{chemin_dl}/{annee}/{timestamp} - {titre}.mp3', "wb") as f:
            f.write(r.content)