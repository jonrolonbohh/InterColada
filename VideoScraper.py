# import numpy as np
import json
from bs4 import BeautifulSoup
import re
import urllib
import requests
import csv



def GetAllVideoLinksChannel(channel_id):
    api_key = ""

    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key, channel_id)

    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append(base_video_url + i['id']['videoId'])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links



def GetDescriptionAndTitle(url):
    
    numTries = 50
    # keepPulling = True
    it = 0
    soup = BeautifulSoup(requests.get(url).content,"lxml")
    titleSearch = soup.find_all("title")
    title = titleSearch[0].get_text('\n')
    description = ""
    if "compilation" in title.lower():
        print("found a non game video: %s"%title.lower)
        title = ""
        description = ""
        return title, description

    while it < numTries:
        it += 1
        try:
            pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
            description = pattern.findall(str(soup))[0].replace('\\n','\n')
            
        except(IndexError):
            print("Failed attempt on %i"% it)
            continue
            # it+=1
        if description:
            break

    if not description:
        title = ""
        return title, description


    # titleSearch = soup.find_all("title")
    # title = titleSearch[0].get_text('\n')
    # print(description)
    return description, title

def GetTitle(url):
    soup = BeautifulSoup(requests.get(url).content,"lxml")
    t = soup.find_all("title")
    for title in soup.find_all("title"):
        print(title.get_text('\n'))


def GetGoals(description, title):
    # split strings by enter
    splitLines = description.split("\n")

    titles = list()
    timeStamps = list()
    goalScorers = list()
    primaryAssists = list()
    highlightGoals = list()

    for line in splitLines:
        highlightGoal = False
        # make line lowercase
        line = line.lower()
        # Skip if not a goal
        if "goal" not in line:
            print("No goal in %s"%line)
            continue
        
        # skip if own goal
        if "own" in line:
            print("Own Goal in %s"%line)
            continue

        # get timestamp and comment
        try:
            firstStr = re.match(r'(?P<time>[[\d{2}]?:?\d{2}:\d{2})( )(?P<comment>[\s\S]+)',line)
            timeStamp = firstStr.group("time")
            # print(timeStamp)
            comment = firstStr.group("comment")
            # print(comment)

        except:
            print("%s not valid line"%line)
            continue

        
        # We have the title and comment. Now we have to parse the comment
        # for who scored the goal and gather the data

        # Remove all spaces in the comment:
        comment=comment.replace(" ","")
        
        # Remove goal part
        comment = comment.replace("goal","")

        # If the goal contains exclamations or percents, it was a highlight goal
        if "!" in comment or r'%' in comment:
            print("highlight goal found")
            highlightGoal = True
            comment = comment.replace("!","")
            comment = comment.replace("%","")

        # Count the Plus numbers. It'll determine how we credit goals
        scorers = comment.split("+")
        
        # cleanup the team name for now
        goalScorer = scorers[-1].replace("(b)","")
        goalScorer = goalScorer.replace("(w)","")
        scorers[-1] = goalScorer


        
        # For now, only the primary assist will count towards assists because it's complicated to code rn
        if len(scorers) == 1:
            # Only single Scorer
            primaryAssist = ""
        else:
            # At least more than one assister. Will only make primary assist
            primaryAssist = scorers[-2]

        titles.append(title)
        timeStamps.append(timeStamp)
        goalScorers.append(goalScorer)
        primaryAssists.append(primaryAssist)
        highlightGoals.append(highlightGoal)

    return titles, timeStamps, goalScorers, primaryAssists, highlightGoals



    




        
    # print(splitLines)


def main():

    currentVideos = GetAllVideoLinksChannel("UCkZJ6nMg5apbOXfBNq_lFJw")
    allTitles = list()
    allTimeStamps = list()
    allGoalScorers = list()
    allPrimaryAssists = list()
    allHighlightGoals = list()
    header = ['Vid', 'timeStamp', 'goalScorer', 'primaryAssist', 'highlightGoal']
    with open('goals.csv', 'w', encoding='UTF8', newline='') as f:
         writer = csv.writer(f)
         writer.writerow(header)

    for count, vid in enumerate(currentVideos):
        print("Current vid %i"%(count))
        # thisTitle = GetTitle(vid)
        thisDescription, thisTitle = GetDescriptionAndTitle(vid)
        if not thisDescription:
            print("vid %i failed. skipping"%count)
            continue
        titles, timeStamps, goalScorers, primaryAssists, highlightGoals = GetGoals(thisDescription, thisTitle)
        with open('goals.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(titles)):
                data = [titles[i], timeStamps[i], goalScorers[i],primaryAssists[i], highlightGoals[i]]
                writer.writerow(data)

        allTitles.append(titles)
        allTimeStamps.append(timeStamps)
        allGoalScorers.append(goalScorers)
        allPrimaryAssists.append(primaryAssists)
        allHighlightGoals.append(highlightGoals)
        # print(test)
        
        # splitLines = test.split("\n")
        # print(splitLines)


if __name__ == '__main__':

    stringTest = "1:00:50 lol eddie !!!!"
    
    # print(z.groups)
    main()