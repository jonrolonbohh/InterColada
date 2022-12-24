# import numpy as np
from bs4 import BeautifulSoup
import re
import urllib.request
import requests




def GetDescription(url):
    soup = BeautifulSoup(requests.get(url).content,"lxml")
    pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
    description = pattern.findall(str(soup))[0].replace('\\n','\n')
    print(description)
    return description

def main():
    test = GetDescription("https://www.youtube.com/watch?v=bfODDz0ic8M")
    print(test)

    splitLines = test.split("\n")
    print(splitLines)


if __name__ == '__main__':
    main()