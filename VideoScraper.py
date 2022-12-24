# import numpy as np
import json
from bs4 import BeautifulSoup
import re
import urllib
import requests




def GetAllVideoLinksChannel(channel_id):
    api_key = "AIzaSyCADRh61QrKZUoII2GUzZ_89QnVTYa_izs"

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

def GetDescription(url):
    soup = BeautifulSoup(requests.get(url).content,"lxml")
    pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
    description = pattern.findall(str(soup))[0].replace('\\n','\n')
    print(description)
    return description



def main():

    currentVideos = GetAllVideoLinksChannel("UCkZJ6nMg5apbOXfBNq_lFJw")

    for count, vid in enumerate(currentVideos):
        print("Current vid %i"%(count))
        test = GetDescription(vid)
        print(test)

    # splitLines = test.split("\n")
    # print(splitLines)


if __name__ == '__main__':
    main()