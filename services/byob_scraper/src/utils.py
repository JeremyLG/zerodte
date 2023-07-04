import datetime
import glob
import os

import pandas as pd
from fake_useragent import UserAgent

user_agent = UserAgent()

HEADERS = {
    "authority": "tradeautomationtoolbox.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "fr-FR;q=0.9",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://tradeautomationtoolbox.com",
    "referer": "https://tradeautomationtoolbox.com/byob-ticks/?save=MGKV96a",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": user_agent.random,
}

BYOB_MAPPING = {
    "ctl00$ContentPlaceHolder1$chkTranche$0": "09:33:00",
    "ctl00$ContentPlaceHolder1$chkTranche$1": "09:45:00",
    "ctl00$ContentPlaceHolder1$chkTranche$2": "10:00:00",
    "ctl00$ContentPlaceHolder1$chkTranche$3": "10:15:00",
    "ctl00$ContentPlaceHolder1$chkTranche$4": "10:30:00",
    "ctl00$ContentPlaceHolder1$chkTranche$5": "10:45:00",
    "ctl00$ContentPlaceHolder1$chkTranche$6": "11:00:00",
    "ctl00$ContentPlaceHolder1$chkTranche$7": "11:15:00",
    "ctl00$ContentPlaceHolder1$chkTranche$8": "11:30:00",
    "ctl00$ContentPlaceHolder1$chkTranche$9": "11:45:00",
    "ctl00$ContentPlaceHolder1$chkTranche$10": "12:00:00",
    "ctl00$ContentPlaceHolder1$chkTranche$11": "12:15:00",
    "ctl00$ContentPlaceHolder1$chkTranche$12": "12:30:00",
    "ctl00$ContentPlaceHolder1$chkTranche$13": "12:45:00",
    "ctl00$ContentPlaceHolder1$chkTranche$14": "13:00:00",
    "ctl00$ContentPlaceHolder1$chkTranche$15": "13:15:00",
    "ctl00$ContentPlaceHolder1$chkTranche$16": "13:30:00",
    "ctl00$ContentPlaceHolder1$chkTranche$17": "13:45:00",
    "ctl00$ContentPlaceHolder1$chkTranche$18": "14:00:00",
    "ctl00$ContentPlaceHolder1$chkTranche$19": "14:15:00",
    "ctl00$ContentPlaceHolder1$chkTranche$20": "14:30:00",
    "ctl00$ContentPlaceHolder1$chkTranche$21": "14:45:00",
    "ctl00$ContentPlaceHolder1$chkTranche$22": "15:00:00",
    "ctl00$ContentPlaceHolder1$chkTranche$23": "15:15:00",
    "ctl00$ContentPlaceHolder1$chkTranche$24": "15:30:00",
    "ctl00$ContentPlaceHolder1$chkTranche$25": "15:45:00",
}


def build_multiple_entries(entries: list[str] | None):
    """
    Build filtered entries through inverting et reverting the byob mapping
    """
    if entries:
        inv_map = {v: k for k, v in BYOB_MAPPING.items()}
        filtered_mapping = {key: inv_map[key] for key in entries}
        return {v: k for k, v in filtered_mapping.items()}
    return BYOB_MAPPING


def generate_date_ranges(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> list[(datetime.datetime, datetime.datetime)]:
    """
    Build multiple intervals of 6 months maximum from two start and end dates
    """
    date_ranges = []
    while start_date <= end_date:
        next_end_date = start_date + datetime.timedelta(days=6 * 30)  # 6 months
        if next_end_date > end_date:
            next_end_date = end_date
        date_ranges.append((start_date, next_end_date))
        start_date = next_end_date + datetime.timedelta(
            days=1
        )  # Start from the next day
    return date_ranges


def get_last_date(directory: str) -> datetime.date | None:
    """
    Return last date from filenames of a directory if it exists and can be parsed to datetime
    """
    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        return None
    if files:
        last_date = max([f.split(".")[0] for f in files])
        try:
            return datetime.datetime.strptime(
                last_date, "%Y-%m-%d"
            ).date() + datetime.timedelta(days=1)
        except ValueError:
            return None
    return None


def split_list_equal_size(lst: list, num_sublists: int):
    """
    Split a list into multiple equal sized sublists
    """
    avg = len(lst) // num_sublists
    remainder = len(lst) % num_sublists
    sublists = []
    index = 0
    for _ in range(num_sublists):
        sublist_size = avg + int(remainder > 0)
        sublists.append(lst[index : index + sublist_size])
        index += sublist_size
        remainder -= 1
    return sublists


def read_csv_wildcard(directory: str, delete=False):
    """
    Read csv files from wildcard path and return dataframe
    """
    csv_files = glob.glob(f"{directory}/*.csv")
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)
        if delete:
            os.remove(file)
    return pd.concat(dfs)


def is_any_dataframe_not_none(dfs: list[pd.DataFrame]):
    """
    Check that a list of dataframes has at least a non null element
    """
    return any(df is not None for df in dfs)


def is_existing_csv_file(directory: str) -> pd.DataFrame | None:
    """
    Check that a directory has at least a csv file
    """
    csv_files = glob.glob(f"{directory}/*.csv")
    for file in csv_files:
        df = pd.read_csv(file)
        os.remove(file)
        return df
