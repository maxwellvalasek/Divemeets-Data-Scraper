from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from get_diver_number import get_diver_number
from datetime import datetime
from statistics import mean, stdev
import time

session = requests.Session()

def get_dmeets_html(phpUrl, **kwargs):
    url = "https://secure.meetcontrol.com/divemeets/system/" + phpUrl
    response = session.get(url, params=kwargs)
    if response.status_code == 200:
        text = response.text
        return BeautifulSoup(text, "html.parser")
    else:
        return None

def getDiverHrefs(diver_number):
    soup = get_dmeets_html("profile.php", number=diver_number)
    profile_table_rows = soup.find("table", width="100%").find_all("tr")
    profile_event_hrefs = [link.get('href') for row in profile_table_rows for link in row.find_all("a") if link.get('href')]
    return profile_event_hrefs

def parseMeetName(eventTable):
    meet_match = re.search(r"Meet:\s*<strong><a href=\"[^\"]+\">([^<]+)</a></strong>", eventTable)
    if meet_match:
        meet_name = meet_match.group(1)
        return meet_name
    else:
        return "Meet name not found"

def parseDateFromEventTable(eventTable):
    date_match = re.search(r"Date:\s*<strong>([a-zA-Z]{3} \d{1,2}, \d{4})", eventTable)
    if date_match:
        date_str = date_match.group(1)
        date_obj = datetime.strptime(date_str, "%b %d, %Y")
        formatted_date = date_obj.strftime("%m-%d-%Y")
        return formatted_date
    else:
        return "Date not found"

def parseBoardLevel(eventTable):
    soup = BeautifulSoup(eventTable, "html.parser")
    rows = soup.find_all("tr")
    for row in rows:
        td = row.find("td", {"colspan": True})
        if td:
            strong_tag = td.find("strong")
            if strong_tag:
                return strong_tag.get_text().strip()
    return "Event category not found"

def calculate_z_score(value, mean, std):
    return (value - mean) / std

def parseEventResults(diver_id, eventTable):
    soup = BeautifulSoup(eventTable, "html.parser")
    diver_info = []
    rows = soup.find_all("tr")
    for row in rows:
        diver_number_tag = row.find("a", href=re.compile("profile.php\?number=\d+"))
        place_tag = row.find("td", text=re.compile("^\d+$"))
        score_tag = row.find("a", href=re.compile("divesheetresultsext.php"))
        if diver_number_tag and place_tag and score_tag:
            diver_number = re.search("number=(\d+)", diver_number_tag['href']).group(1)
            place = place_tag.text.strip()
            score = float(score_tag.text.strip())
            diver_info.append((diver_number, place, score))
    if len(diver_info) < 2:
        return
    scores = [row[2] for row in diver_info]
    scores_mean = round(mean(scores), 2)
    scores_std = round(stdev(scores), 2)
    event_competitors_count = len(diver_info)
    for row in diver_info:
        if row[0] == diver_id:
            place = row[1]
            score = row[2]
            z_score = round(calculate_z_score(score, scores_mean, scores_std), 2)
            diver_row = (place, event_competitors_count, score, z_score, scores_mean, scores_std)
            return diver_row
    return

def getEventPage(diver_id, eventHref):
    modified_url = eventHref.replace("divesheetresultsext.php", "eventresultsext.php")
    modified_url = re.sub(r"(dvrnum=\d+&)|(sts=\d+&?)", "", modified_url).rstrip("&")
    event_results = get_dmeets_html(modified_url)
    event_table_string = str(event_results.find("table", border="0", width="100%"))
    eventData_meetName = parseMeetName(event_table_string)
    eventData_date = parseDateFromEventTable(event_table_string)
    eventData_board = parseBoardLevel(event_table_string)
    eventData_results = parseEventResults(diver_id, event_table_string)
    if(eventData_results):
        eventData_place = eventData_results[0]
        eventData_count_competitors = eventData_results[1]
        eventData_final_score = eventData_results[2]
        eventData_z_score = eventData_results[3]
        eventData_mean = eventData_results[4]
        eventData_std = eventData_results[5]
        eventData_combined = {
            "Date": eventData_date,
            "Meet Name": eventData_meetName,
            "Board": eventData_board,
            "Place": eventData_place,
            "Competitors Count": eventData_count_competitors,
            "Final Score": eventData_final_score,
            "Z-Score": eventData_z_score,
            "Mean": eventData_mean,
            "Standard Deviation": eventData_std
        }
        return eventData_combined
    else:
        return

def process_event_page(diver_number, href):
    event_page_data = getEventPage(diver_number, href)
    if event_page_data is not None:
        return event_page_data

def main(diverName):
    diver_number = get_diver_number(diverName)
    profile_event_hrefs = getDiverHrefs(diver_number)
    event_data = []
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_event_page, diver_number, href) for href in profile_event_hrefs]
        for future in as_completed(futures):
            event_page_data = future.result()
            if event_page_data is not None:
                event_data.append(event_page_data)
    
    event_data = [data for data in event_data if data is not None]
    df = pd.DataFrame(event_data)
    df.insert(0, "Diver", diverName)
    df.to_csv(f'diver_csvs/{diverName.replace(" ", "_")}.csv', index=False)

import sys
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the diver name as a command line argument.")
        sys.exit(1)
    
    diver_name = sys.argv[1]
    start_time = time.time()
    main(diver_name)
    print(f"{diver_name} took {time.time() - start_time} seconds")
