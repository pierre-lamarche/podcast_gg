# -*- coding: utf-8 -*-
"""
Created on 30/03/2021
@author: pierre
"""

url = "https://podcloud.fr/subscriptions/60637d562f0fc600c379f6ac.rss?k=5KXuxtdByX8lmS-tP_RMHA&u=pierrelamarche"

import feedparser as fp
import requests
import datetime
import os
import re

podcasts = fp.parse(url)

chemin_dl = "/home/pierre/Musique/dl"

for entry in podcasts.entries:
    r = requests.get(entry.links[1]['href'])
    timestamp = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z').strftime("%Y-%m-%d")
    auteur = re.match(r'^\w* : \d{2}:\d{2}:\d{2} - ([^-]*) -', entry.subtitle).group(1)
    with open(chemin_dl+'/'+timestamp+' - '+entry.title.replace('/', '')+".mp3", "wb") as f:
        f.write(r.content)