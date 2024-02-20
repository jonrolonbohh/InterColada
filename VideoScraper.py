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

# Function to get description using YouTube Data API
def get_description_from_api(video_id):
    api_key = "AIzaSyCADRh61QrKZUoII2GUzZ_89QnVTYa_izs"
    url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet'
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=30)
            break  # Success, exit the loop
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out, retrying...")
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt + 1}, retrying...")

    data = response.json()

    # Check if the response contains the necessary information
    if 'items' in data and len(data['items']) > 0:
        return data['items'][0]['snippet']['description']
    else:
        return ""


def GetDescriptionAndTitle(url):
    
    numTries = 25
    # keepPulling = True
    it = 0
    description = ""
    title = ""
    soup = BeautifulSoup(requests.get(url).content,"lxml")
    titleSearch = soup.find_all("title")
    title = titleSearch[0].get_text('\n')
    
    if "compilation" in title.lower():
        print("found a non game video: %s"%title.lower())
        title = ""
        return title, description

    if "ksp" in title.lower():
        print("found a ksp video: %s"%title.lower())
        title = ""
        return title, description

    while it < numTries:
        it += 1
        # try:
        pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')

        description_search = pattern.findall(str(soup))

        if not description_search:
            print("No description found. Attempting to get from API")
            # Extract video ID from URL
            video_id = url.split("watch?v=")[-1]
            description = get_description_from_api(video_id)
        else:
            description = description_search[0].replace('\\n', '\n')
            
        # except(IndexError):
        #     print("IndexError attempt on %i"% it)
        #     continue
            # it+=1
        if description:
            break
        print("EmptyDescription on attempt %i"%it)

    if not description:
        title = ""
        return title, description

    return description, title



def GetGoals(description, title, vid):
    # split strings by enter
    splitLines = description.split("\n")

    titles = list()
    timeStamps = list()
    elapsedTime = list()
    goalScorers = list()
    primaryAssists = list()
    highlightGoals = list()
    goalLinks = list()
    

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
            comment = firstStr.group("comment")

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
        elapsedTimeMins = calcElapsedTime(timeStamp)
        elapsedTime.append(elapsedTimeMins)
        
        elapsedTimeSecs = round(elapsedTimeMins*60)
        timeStampString = "&t=%is"%elapsedTimeSecs
        goalLink = vid + timeStampString
        goalLinks.append(goalLink)
        goalScorers.append(goalScorer)
        primaryAssists.append(primaryAssist)
        highlightGoals.append(highlightGoal)

    return titles, timeStamps,elapsedTime, goalScorers, primaryAssists, highlightGoals, goalLinks



    
def calcElapsedTime(timeStampString):
    # Calculate Elapsed time for stamina stats
    time = timeStampString.split(":")

    if len(time) == 3:
        hours = float(time[0])
        minutes = float(time[1])
        seconds = float(time[2])
    else:
        hours = float(0)
        minutes = float(time[0])
        seconds = float(time[1])
        
    elapsedTimeMins = hours*60 + minutes + seconds/60 
    return elapsedTimeMins   



def main():

    currentVideos = GetAllVideoLinksChannel("UCkZJ6nMg5apbOXfBNq_lFJw")
    header = ['Vid', 'timeStamp','elapsedTime', 'goalScorer', 'primaryAssist', 'highlightGoal','GoalLink']
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
        titles, timeStamps,elapsedTime, goalScorers, primaryAssists, highlightGoals, goalLinks = GetGoals(thisDescription, thisTitle, vid)
        with open('goals.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(titles)):
                data = [titles[i], timeStamps[i], elapsedTime[i], goalScorers[i],primaryAssists[i], highlightGoals[i],goalLinks[i]]
                writer.writerow(data)




if __name__ == '__main__':
    main()