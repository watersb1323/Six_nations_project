__author__ = 'beano'

# Import relevant packages
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define URL's necessary to extract player's information
id1 = 204336
lineup_url = 'http://www.rbs6nations.com/en/matchcentre/match_centre.php?section=lineups&fixid='
match1 = lineup_url + str(id1)
match2 = lineup_url + str(id1 + 1)
match3 = lineup_url + str(id1 + 2)
lineup_urls = [match1, match2, match3]

complete_player_names = []

# Obtain list of players for database
for page_url in lineup_urls:
    # Convert HTML to soup
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract team names
    team1_name = soup.find(class_='teams').find(class_='home').get_text().strip().lower()
    team2_name = soup.find(class_='teams').find(class_='away').get_text().strip().lower()
    print(team1_name, team2_name)

    # Extract positions
    positions_html = soup.find_all(class_='pos')
    positions = [position_html.get_text() for position_html in positions_html]
    # print(positions)

    # Extract player names
    team1_players_html = soup.find_all(class_='namea')
    team1_players = [player_html.get_text().lower() for player_html in team1_players_html]
    # print(team1_players)

    team2_players_html = soup.find_all(class_='nameb')
    team2_players = [player_html.get_text().lower() for player_html in team2_players_html]
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
            temp = [team2_players[i], team2_name, int(positions[i])]
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
writer = pd.ExcelWriter('6_nations_round_5_output_2017.xlsx')
player_database.to_excel(writer, sheet_name='players')
writer.save()