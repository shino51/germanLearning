# This is a sample Python script.

import csv
import re

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup


def fetch_alltagsdeutch_links():
    url = "https://learngerman.dw.com/de/alltagsdeutsch-archiv-2025/a-71187473"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    www_links_section = soup.find("div", attrs={"class": "s1kcezzg"})
    www_links = www_links_section.find("div")
    entries = www_links.find_all("a", attrs={"class": "s13pardp"}, href=True)
    www_lists = []
    print("")
    for entry in entries:
        url = entry['href']
        title_tag = entry.find("h3", attrs={"class": "p13ybupf"})
        title = title_tag.get_text().strip()
        # print(title)
        # print(url)
        formatted_cell = '=HYPERLINK("{0}", "{1}")'
        print(formatted_cell.format(url, title))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    fetch_alltagsdeutch_links()
