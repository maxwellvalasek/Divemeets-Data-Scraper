# Divemeets Data Scraper
Retrive and calculate competition performances from [www.divemeets.com](https://secure.meetcontrol.com/divemeets/system/index.php) for an individual diver. 

## Installation
Install the required packages:
    `pip install -r requirements.txt`

Valid diver names can be found on the [divemeets website](https://secure.meetcontrol.com/divemeets/system/memberlist.php)

## Usage: 

### Get Event Data: `python EventData.py "Conrad Eck"`
* Creates a csv containing event performance history for the given diver at `diver_csvs/<diver_name>.csv`
* Calculates the `Z-Score`, `Mean`, and `Standard Deviation` of the divers score compared to others for each event

| Diver      | Date       | Meet Name                               | Board                    | Place | Competitors Count | Final Score | Z-Score | Mean  | Standard Deviation |
|------------|------------|-----------------------------------------|--------------------------|-------|-------------------|-------------|---------|-------|-------------------|
| Conrad Eck | 06-16-2022 | 2022 USA Diving Zone E Championships   | 16-18 Boys Platform J.O  | 5     | 23                | 440.95      | 0.84    | 372.55| 81.5              |

*Example row from Conrad_Eck.csv*

### Merge CSV Data: `python merge_csv_data.py`
* Merges csv data for each diver within `diver_csvs/` for comparative analysis
* Produces `merged_data/divers_combined.csv`

