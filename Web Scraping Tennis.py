import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import unicodedata
import re
import matplotlib.pyplot as plt
import csv
from itertools import zip_longest
import json
import numpy as np
import string



#Taken and adapted from COMP20008
#Specify the initial page to crawl
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'
seed_item = 'index.html'

seed_url = base_url + seed_item
#Ensures that web crawl is not infinite, and only goes for a pre-specified amount of time
page = requests.get(seed_url, timeout = (5, 20))
soup = BeautifulSoup(page.text, 'html.parser')

visited = {}; 
visited[seed_url] = True
pages_visited = 1

remove_unessentials = ['Previous Article', 'Next Article','Previous ArticleNext Article','Tennis News - Find out more about your favourite players including David Nalbandian, Marat Safin and Roger Federer.\n']
#Remove index.html
links = soup.findAll('a')
seed_link = soup.findAll('a', href=re.compile("^index.html"))
#to_visit_relative = list(set(links) - set(seed_link))
to_visit_relative = [l for l in links if l not in seed_link]


# Resolve to absolute URLs
to_visit = []
total_headlines = []
total_articles = []
total_body = []
for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))

    
#Find all links that go to separate pages
while (to_visit):
    # Impose a limit to avoid breaking the site 
 
    # Consume the list of URLs
    link = to_visit.pop(0)

    page = requests.get(link)

    soup = BeautifulSoup(page.text, 'html.parser')
    

    visited[link] = True

    new_links = soup.findAll('a')
    #Find URLs
    for new_link in new_links :
        new_item = new_link['href']
        new_url = urljoin(link, new_item)

        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)

    pages_visited += 1

    #Find headers
    new_headlines = soup.h1.text
    total_headlines.append(new_headlines)
    header_name = soup.find('div', {"id": "mainArticle"})

    text_list = [i.text for i in header_name.findAll('h1') if i.text not in remove_unessentials]
    content = soup.find('div', {"id": "articleDetail"})
    #Find body text
    for i in content.findAll('p'):
        if i.text not in remove_unessentials:
            text_list.append(i.text)
    total_body.append(text_list)

url_list = []
for each_key in visited.keys():
    url_list.append(each_key)
url_list.pop(0)



url_article_table = [url_list, total_headlines]


#Write to Task1 CSV
table = []
export_data = zip_longest(*url_article_table, fillvalue = '')
with open("task1.csv", 'w') as file_out:
    headers = ["URL", "Headline"]
    writer = csv.writer(file_out)
    # write the header
    writer.writerow(("URL", "Headline"))
    writer.writerows(export_data)



#Open the json file
with open('tennis.json') as f:
    Data = json.load(f)


site_word_pair_list = []

#Searching each site for first player mentioned
#Regex is used in order to remove names with punctuations e.g. "James (Bates,"
for each_site in total_body:
    name_found = 0
    word_pair_list = []

    for each_text in each_site:
        i = 0
        split_text = each_text.split()
        for i in range(len(split_text)-1):
            j = i+1
            word_i = re.sub("\(|\"|\!|\,|\.|\)|\;", "",split_text[i])
            word_j = re.sub("\(|\"w|\!|\,|\.|\)|\;", "",split_text[j])
            word_pair = word_i + " " + word_j
            word_pair_list.append(word_pair)
            
    site_word_pair_list.append(word_pair_list)         

length = 0
relevant_header_list= []
relevant_body_list = []
i=0
players =[]

#Find the first name mentioned in the article
for i in range(len(site_word_pair_list)):
    name_found = 0

    for pair in site_word_pair_list[i]:
        corrected_pair = re.sub("\,", "",pair)
        for each_player in Data:
            #Scan for matches of the pair with the corresponding name in the JSON file
            if ((corrected_pair.upper() in each_player['name']) and (len(corrected_pair.split(' ')[0]) > 1) and 
                (len(corrected_pair.split()[0])==len(each_player['name'].split()[0]))) :
                name_found = 1   
                player_name = string.capwords(each_player['name'])
                players.append(player_name)
                relevant_header_list.append(total_headlines[i])
                relevant_body_list.append(total_body[i])
                length +=1
            
        if (name_found == 1):
            break



urls = 0
url_list = []
# Create a list with relevant URLs
for each_relevant_header in relevant_header_list:
    for i in range(len(url_article_table[1])):
        if each_relevant_header == str(url_article_table[1][i]):
            url_list.append(url_article_table[0][i])
            urls+=1
        i+=1




    
#Get all scores that are found in the articles, skipping invalid scores
def get_score(body_list):
    remove_space_punctuation = " ,.!?"
    list_score_and_index = []
    i=0
    j=0
    for i in range(len(body_list)):
        # Regular expressions used in order to find valid scores
        for each_paragraph in body_list[i]:
            match_score = re.sub("\(\d\-\d\)", "", each_paragraph)
            new_match_score = re.sub("\(\d\\\d\)", "", match_score)
            without_space_matches = re.sub("  ", " ", new_match_score)
            scores = re.search("(\d\-\d.){2,5}", without_space_matches)

            #Remove any unwanted characters and append first score found to a new list
            if scores:
                if (scores.group(0)[-1] in remove_space_punctuation):
                    new_scores = [scores.group(0)[0:-1], i]
                    list_score_and_index.append(new_scores)
                elif (scores.group(0)[-1].isnumeric()):
                    new_scores = [scores.group(0), i]
                    list_score_and_index.append(new_scores)
                    continue
                break
                
        
    return(list_score_and_index)

scores_and_index = get_score(relevant_body_list)

new_total_games_list = []
needed_headers = []
needed_urls = []
needed_players =[]
needed_scores = []

#Adds all the relevant articles and their information together
for each in scores_and_index:
    #Deals with forfeits
    if (len(each[0].split()[-1]) >=4 and (abs(int(each[0].split()[-1][0])-int(each[0].split()[-1][2:]))>10)):
        continue
    
    needed_headers.append(relevant_header_list[int(each[1])])
    needed_urls.append(url_list[int(each[1])])
    needed_players.append(players[int(each[1])])
    needed_scores.append(each[0])

#Write to Task2 CSV
total_task2 = [needed_urls, needed_headers, needed_players, needed_scores]
export_data = zip_longest(*total_task2, fillvalue = '')
with open("task2.csv", 'w') as file_out:
    headers = ["URL", "Headline", "Player", "Score"]
    writer = csv.writer(file_out)
    # write the header
    writer.writerow(("URL", "Headline", "Player", "Score"))
    writer.writerows(export_data)



#Get the total game difference of each article
collected_game_difference = []
for each_match in needed_scores:
    game_difference = 0
    for each_set in each_match.split():
        game_difference += (int(each_set[0])-int(each_set[2:]))
    collected_game_difference.append((game_difference))


total_player_frequency = []
player_frequency_dict = {}
players_game_difference = {}


#Find the frequency and the total game difference per match for each relevant player
for each_player_index in range(len(needed_players)):

    if needed_players[each_player_index] not in player_frequency_dict:
        player_frequency_dict[needed_players[each_player_index]] = 0
        players_game_difference[needed_players[each_player_index]] = 0
        
    player_frequency_dict[needed_players[each_player_index]] += 1
    players_game_difference[needed_players[each_player_index]] += abs(collected_game_difference[each_player_index])

all_players_difference = []    
player_name = []     
avg_difference =[]
#Find the average game difference per player
for every_name in players_game_difference:
    player_name.append(every_name) 
    avg_difference.append((players_game_difference[every_name]) / player_frequency_dict[every_name])

all_players_difference = [player_name, avg_difference]

#Write to Task3 CSV
export_data = zip_longest(*all_players_difference, fillvalue = '')
with open("task3.csv", 'w') as file_out:
    headers = ["Player", "Avg_game_difference"]
    writer = csv.writer(file_out)
    # write the header
    writer.writerow(("Player", "Avg_game_difference"))
    writer.writerows(export_data)


task_4_dict_items = player_frequency_dict.items()
top5_frequent_players = []
top5_frequencies = []

top_number_preference = 5
frequency_list = []

#Find top 5 frequently written about players as per Task 4
for each_tuple in task_4_dict_items:
    new_tuple = each_tuple[::-1]
    frequency_list.append(new_tuple)
frequency_list.sort(reverse = True)
for each_tuple in frequency_list[:top_number_preference]:
    top5_frequent_players.append(each_tuple[1])
for each_tuple in frequency_list[:top_number_preference]:
    top5_frequencies.append(each_tuple[0])


y_pos = np.arange(len(top5_frequent_players))
#Set figure size and their labels
plt.figure(figsize=(15, 8))
plt.bar(y_pos, top5_frequencies, align='center', alpha=0.5, width = 0.5)
plt.xticks(y_pos, top5_frequent_players)
plt.xlabel('Player Name')
plt.ylabel('Frequency')
plt.title('Most Frequent Players in Articles', fontweight = 'bold')

#Save file
plt.savefig('task4.png', dpi = 400)
plt.close()

#Find the win percentage of each relevant player as per Task 5
win_percent = []
for each_player in player_name:
    for each_desc in Data:
        if (each_player.upper() == each_desc['name']):
            win_percent.append(float(each_desc['wonPct'][:-2]))


plt.figure(figsize = (14,8))

# Set height of bars
bars1 = avg_difference
bars2 = win_percent

# Set width of bars
bar_width = 0.3
# Sets position of bars
r1 = np.arange(len(bars1))
r2 = [x + bar_width for x in r1]

# Make the plot
plt.bar(r1, bars1, color='#5DFF00', width=bar_width, edgecolor='white', label='Average Game Difference')
plt.bar(r2, bars2, color='#1CADF5', width=bar_width, edgecolor='white', label='Win Percentage')
 
# Add labels
plt.xlabel('Player Name')
plt.ylabel('Value')
plt.xticks(r1+0.2, player_name)
plt.tick_params(axis='x', labelsize=4)

# Create legend & Show graphic
plt.legend()
plt.title('Players and Their Average Game Differences and Win Percentages', fontweight = 'bold')
plt.savefig('task5.png',dpi =400, bbox_inches = 'tight')
plt.close()






    

