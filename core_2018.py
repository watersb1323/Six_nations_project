__author__ = 'beano'

# Import relevant packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re, sys

cap_letter_regex = re.compile('[A-Z][^A-Z]*')

# Define URL's necessary to extract player's information

lineup_url1 = 'https://www.ultimaterugby.com/match/france-vs-italy-at-stade-v%C3%A9lodrome-23rd-feb-2018/50237/lineup'
lineup_url2 = 'https://www.ultimaterugby.com/match/ireland-vs-wales-at-aviva-stadium-24th-feb-2018/50238/lineup'
lineup_url3 = 'https://www.ultimaterugby.com/match/scotland-vs-england-at-murrayfield-24th-feb-2018/50239/lineup'

lineup_urls = [lineup_url1, lineup_url2, lineup_url3]

complete_player_names = []

# Obtain list of players for database
for page_url in lineup_urls:
    # Convert HTML to soup
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    team_names = page_url.split('match/')[1].split('-at')[0].split('-vs-')
    team1_name = team_names[0].title()
    team2_name = team_names[1].title()
    print(team1_name, team2_name)

    # Extract positions
    positions_html = soup.find_all(class_='position')
    positions = [position_html.get_text() for position_html in positions_html]
    # print(positions)

    # Extract player names
    team1_players_html = soup.find(class_='table-squad').find_all(class_='team-home')
    team1_players_concat = [player_html.get_text().strip() for player_html in team1_players_html][:len(positions)]
    team1_players = [' '.join(re.findall(cap_letter_regex, player_html)) for player_html in team1_players_concat]
    # print(team1_players)

    team2_players_html = soup.find(class_='table-squad').find_all(class_='team-away')
    team2_players_concat = [player_html.get_text().strip() for player_html in team2_players_html][:len(positions)]
    team2_players = [' '.join(re.findall(cap_letter_regex, player_html)) for player_html in team2_players_concat]
    # print(team2_players)

    t1_p_len = len(team1_players)
    t2_p_len = len(team2_players)
    pos_len = len(positions)

    if t1_p_len == pos_len:
        for i in range(t1_p_len):
            temp = [team1_players[i], team1_name, positions[i]]
            complete_player_names.append(temp)

    if t2_p_len == pos_len:
        for i in range(t2_p_len):
            temp = [team2_players[i], team2_name, positions[i]]
            complete_player_names.append(temp)

# Construct dataframe from list of rows for database
player_database = pd.DataFrame(data=complete_player_names, columns=['name', 'team', 'position'])
print(player_database)

# print(player_database.loc[player_database['team'] == 'wales'])
# print(player_database[player_database.position == '4'])

# ###################################################
# Find player stats
# ###################################################

# Add columns for player stats
stats_columns = [   'minutes played',
                    'started as a sub',
                    'not used',
                    'points',
                    'tries',
                    'drop goals',
                    'conversion scored',
                    'penalties scored',
                    'yellow card',
                    'red and yellow card',
                    'red card']

stats_columns_len = len(stats_columns)
db_size = len(player_database['name'])

for column_name in stats_columns:
    player_database[column_name] = pd.Series(['-']*db_size)

for index, row in player_database.iterrows():
    print(index, row['name'], sep=' ')
    # Obtain player name
    player = row['name']
    name_string = player.replace(' ', '+')

    # Go to appropriate web page
    stats_index_url = 'http://rugby.statbunker.com/usual/search?action=Find&search={0}'.format(name_string)
    stats_index_page = requests.get(stats_index_url)
    stats_index_soup = BeautifulSoup(stats_index_page.content, 'html.parser')

    try:
        player_id_html = stats_index_soup.find('a', class_='linkGreen', href=True)
        player_id_href = player_id_html['href']
        player_id = player_id_href.split('=')[1]
    except TypeError:
        print('TypeError encountered, continuing', index, row['name'])
    # print(player_id)

    player_2016_stats_url = 'http://rugby.statbunker.com/players/SeasonMatches?player_id={0}&comps_type=-1&dates=2017'.format(player_id)
    player_2016_page = requests.get(player_2016_stats_url)
    player_2016_soup = BeautifulSoup(player_2016_page.content, 'html.parser')

    stats_figures_html = player_2016_soup.select('b')
    stats_figures = [cell.get_text() for cell in stats_figures_html[5:16]]

    sf_len = len(stats_figures)

    if sf_len == stats_columns_len:
        for i in range(sf_len):
            player_database.loc[player_database['name'] == player, stats_columns[i]] = stats_figures[i]

# print(player_database)

# Write player_database to excel document
writer = pd.ExcelWriter('6_nations_round_3_output_2018.xlsx')
player_database.to_excel(writer, sheet_name='players')
writer.save()
