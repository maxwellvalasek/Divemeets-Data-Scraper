from bs4 import BeautifulSoup
import mechanize
import re

def get_diver_number(name):
    br = mechanize.Browser()

    # Split name
    comps = name.split()
    if len(comps) != 2:
        raise Exception("Name provided must be two words (First Last)")
    first, last = comps

    # Submit member search form
    url = "https://secure.meetcontrol.com/divemeets/system/memberlist.php"
    br.open(url)
    br.select_form(nr=0)
    br.form["first"] = first
    br.form["last"] = last
    req = br.submit()
    soup = BeautifulSoup(req.read(), "html.parser")
    br.close()

    link = soup.find("a", attrs={"href": re.compile("profile.php")}).get("href")
    last_five = link[-5:]
    return last_five

