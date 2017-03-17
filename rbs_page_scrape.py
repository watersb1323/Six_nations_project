# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 19:41:50 2017

@author: beano
"""


# Import relevant packages
import requests
from bs4 import BeautifulSoup
import pandas as pd

id1 = '204324'
lineup_url = 'http://www.rbs6nations.com/en/matchcentre/match_centre.php?section=playstatshome&fixid='

database_list = []

page_url = lineup_url + id1
page = requests.get(page_url)
soup = BeautifulSoup(page.content, 'html.parser')

a_table = soup.find('div', class_='basecolumn1a')
# table = soup.select('div.basecolumn1a')

b_table = soup.find('div', class_='Content_MatchDayStats')
c_table = soup.find('opta')

print(list(c_table.children))

print(len(c_table))
print(type(c_table))
print(c_table)