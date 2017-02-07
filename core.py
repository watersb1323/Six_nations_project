__author__ = 'beano'

# Import relevant packages
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define URL's necessary to extract player's information
match1 = 'http://www.rbs6nations.com/en/matchcentre/match_centre.php?section=lineups&fixid=204324'
match2 = 'http://www.rbs6nations.com/en/matchcentre/match_centre.php?section=lineups&fixid=204325'
match3 = 'http://www.rbs6nations.com/en/matchcentre/match_centre.php?section=lineups&fixid=204326'
lineup_urls = [match1, match2, match3]

complete_player_names = []

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

    # Extract player names
    team1_players_html = soup.find_all(class_='namea')
    team1_players = [player_html.get_text().lower() for player_html in team1_players_html[1:]]
    print(team1_players)

    team2_players_html = soup.find_all(class_='nameb')
    team2_players = [player_html.get_text().lower() for player_html in team2_players_html[1:]]
    print(team2_players)

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

player_database = pd.DataFrame(data=complete_player_names, columns=['name', 'team', 'position'])
print(player_database)


# Add to dictionary



#
# scot_players = tree.xpath("//td[@class='namea'][text()]")
#
# #scot_players
#
# print(scot_players)