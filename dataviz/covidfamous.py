from wikiscrape import *

response = requests.get("https://en.wikipedia.org/wiki/List_of_deaths_due_to_coronavirus_disease_2019")
soup = bs4.BeautifulSoup(response.content, "lxml")
links = [a["href"].replace("/wiki/","") for a in find_tags(soup, all_("span", id="List_of_deaths_in_2020"), parents_("h2"), next_siblings_("table"), all_("tr"), all_("th", limit=1), all_("a"))]
links = [x for x in links if "https://" not in x]

# df = score_by_name(links)
