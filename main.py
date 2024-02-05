# Get Diver Data
from concurrent.futures import ThreadPoolExecutor
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np
from get_dnum import get_diver_number
import re
from datetime import datetime
import re
from execInfo import execution_info
from statistics import mean, stdev
import aiohttp
import asyncio

session = requests.Session()

async def get_dmeets_html(phpUrl, **kwargs):
    url = "https://secure.meetcontrol.com/divemeets/system/" + phpUrl
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=kwargs) as response:
            if response.status == 200:
                text = await response.text()
                return BeautifulSoup(text, "html.parser")
            else:
                return None

async def getDiverHrefs(diver_number):
    soup = await get_dmeets_html("profile.php", number=diver_number)
    profile_table_rows = soup.find("table", width="100%").find_all("tr")
    profile_event_hrefs = [link.get('href') for row in profile_table_rows for link in row.find_all("a") if link.get('href')]
    return profile_event_hrefs

def parseDateFromEventTable(eventTable):
    date_match = re.search(r"Date:\s*<strong>([a-zA-Z]{3} \d{1,2}, \d{4})", eventTable)
    if date_match:
        date_str = date_match.group(1)
        date_obj = datetime.strptime(date_str, "%b %d, %Y")
        formatted_date = date_obj.strftime("%m-%d-%Y")
        return formatted_date
    else:
        return("Date not found")
    
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

    # Find all rows in the table
    rows = soup.find_all("tr")
    for row in rows:
        # Find the diver number
        diver_number_tag = row.find("a", href=re.compile("profile.php\?number=\d+"))
        place_tag = row.find("td", text=re.compile("^\d+$"))
        score_tag = row.find("a", href=re.compile("divesheetresultsext.php"))
        if diver_number_tag and place_tag and score_tag:
            diver_number = re.search("number=(\d+)", diver_number_tag['href']).group(1)
            place = place_tag.text.strip()
            score = float(score_tag.text.strip())  # Convert score to float for calculations
            diver_info.append((diver_number, place, score))

    if len(diver_info) < 2:  # Check for insufficient data points
        return

    scores = [row[2] for row in diver_info]  # Extract scores from diver_info
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


async def getEventPage(diver_id, eventHref):
    modified_url = eventHref.replace("divesheetresultsext.php", "eventresultsext.php")
    modified_url = re.sub(r"(dvrnum=\d+&)|(sts=\d+&?)", "", modified_url).rstrip("&")
    event_results = await get_dmeets_html(modified_url)
    event_table_string = str(event_results.find("table", border="0", width="100%"))

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
            "Board": eventData_board,
            "Place": eventData_place,
            "Competitors Count": eventData_count_competitors,
            "Final Score": eventData_final_score,
            "Z-Score": eventData_z_score,
            "Mean": eventData_mean,
            "Standard Deviation": eventData_std
        }
        return eventData_combined
    else: return
    
async def main(diverName):
    diver_number = get_diver_number(diverName)
    profile_event_hrefs = await getDiverHrefs(diver_number)
    tasks = [getEventPage(diver_number, href) for href in profile_event_hrefs]
    
    event_data = await asyncio.gather(*tasks)
    # Filter out None results and proceed with your data processing
    event_data = [data for data in event_data if data is not None]

    # Convert event_data to DataFrame and save as before
    df = pd.DataFrame(event_data)
    df.insert(0, "Diver", diverName)
    df.to_csv(f'csv/{diverName.replace(" ", "_")}.csv', index=False)

import time

if __name__ == "__main__":
    diver_name = "Max Valasek"
    start_time = time.time()
    asyncio.run(main(diver_name))
    print(f"{diver_name} took {time.time() - start_time} seconds")




