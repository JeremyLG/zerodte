from datetime import date, timedelta

from fake_useragent import UserAgent

user_agent = UserAgent()

headers = {
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

mapping_v2 = {
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


def generate_date_ranges(start_date, end_date):
    date_ranges = []
    while start_date <= end_date:
        next_end_date = start_date + timedelta(days=6*30)  # 6 months
        if next_end_date > end_date:
            next_end_date = end_date
        date_ranges.append((start_date, next_end_date))
        start_date = next_end_date + timedelta(days=1)  # Start from the next day
    return date_ranges
