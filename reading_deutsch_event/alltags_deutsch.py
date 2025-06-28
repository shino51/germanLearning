# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup


def fetch_alltagsdeutch_links(alltagsdeutsch_url):
    response = requests.get(alltagsdeutsch_url)
    soup = BeautifulSoup(response.content, "html.parser")
    www_links_section = soup.find("div", attrs={"class": "s1kcezzg"})
    www_links = www_links_section.find("div")
    entries = www_links.find_all("a", attrs={"class": "s13pardp"}, href=True)
    print("")
    for entry in entries:
        alltagsdeutsch_url = entry['href']
        title_tag = entry.find("h3", attrs={"class": "p13ybupf"})
        title = title_tag.get_text().strip()

        formatted_cell = '=HYPERLINK("{0}", "{1}")'
        print(formatted_cell.format(alltagsdeutsch_url, title))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url = "https://learngerman.dw.com/de/alltagsdeutsch-archiv-2025/a-71187473"
    fetch_alltagsdeutch_links(url)
