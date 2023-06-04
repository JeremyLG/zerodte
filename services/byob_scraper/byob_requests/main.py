import datetime
import glob
from io import StringIO
import logging
import os
import requests

import pandas as pd

from .settings import CONF
from .utils import headers, mapping_v2, generate_date_ranges

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def build_req_v2(
    max_premium,
    min_premium,
    width,
    stop,
    entries,
    start_date,
    end_date,
):
    def build_multiple_entries(entries: list[str]):
        """
        Build filtered entries through inverting et reverting mapping
        """
        inv_map = {v: k for k, v in mapping_v2.items()}
        filtered_mapping = {key: inv_map[key] for key in entries}
        return {v: k for k, v in filtered_mapping.items()}

    def build_date(dt: datetime.datetime) -> str:
        """
        Format a datetime in the correct way for the requests to be effective
        """
        return f"{dt.month}/{dt.day}/{dt.year}"

    start_date = build_date(start_date)
    if end_date:
        end_date = build_date(end_date)

    data = {
        "ctl00$ContentPlaceHolder1$ddDataset": "1",
        "ctl00$ContentPlaceHolder1$txtShare": "https://tradeautomationtoolbox.com/byob-ticks/?save=yaYw2Jg",
        "ctl00$ContentPlaceHolder1$ddStrikeSelection": "PremiumMax"
        if max_premium
        else "PremiumMin",
        "ctl00$ContentPlaceHolder1$txtStrikePremium": max_premium or min_premium,
        "ctl00$ContentPlaceHolder1$ddWidth": width,
        "ctl00$ContentPlaceHolder1$ddQuantitySelection": "Fixed",
        "ctl00$ContentPlaceHolder1$ddQuantity": "1",
        "ctl00$ContentPlaceHolder1$txtQuantityBP": "0",
        "ctl00$ContentPlaceHolder1$txtQuantityMax": "",
        "ctl00$ContentPlaceHolder1$txtAccountStart": "30000",
        "ctl00$ContentPlaceHolder1$ddStop": stop,
        "ctl00$ContentPlaceHolder1$ddProfitTarget": "P100",
        "ctl00$ContentPlaceHolder1$txtCommOpen": "3.2",
        "ctl00$ContentPlaceHolder1$txtCommClose": "3.2",
        "ctl00$ContentPlaceHolder1$txtFee": "0",
        "ctl00$ContentPlaceHolder1$txtSlipOpen": "0",
        "ctl00$ContentPlaceHolder1$txtSlipClose": "0.15",
        "ctl00$ContentPlaceHolder1$txtVIXMin": "0",
        "ctl00$ContentPlaceHolder1$txtVIXMax": "",
        "ctl00$ContentPlaceHolder1$txtPremiumMin": "0.5",
        "ctl00$ContentPlaceHolder1$txtPremiumMax": "",
        "ctl00$ContentPlaceHolder1$txtDateStart": start_date,
        "ctl00$ContentPlaceHolder1$txtDateEnd": end_date,
        "ctl00$ContentPlaceHolder1$txtTimeStart": "",
        "ctl00$ContentPlaceHolder1$txtTimeEnd": "",
        "ctl00$ContentPlaceHolder1$rblOptionType": "B",
        **build_multiple_entries(entries),
        "ctl00$ContentPlaceHolder1$ddTrend": "",
        "__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnExport",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": "j5HWoHoyaLaKQ6Y+skU8RvvqxOyx2bcnPSbfAcfe76JIX2w5bOarF0OKF5+kp0VnmbakIcUK3xTmb9fwJtdgKSLOtIw/UvslB5fsOshmxDA+fLJaob8CCSgXWmEwPVMWHmhdBWBckr2DF/se3hIWbKACY5WTGPuhgddJfOdrjETPSeA+MpqZn27dXPblwy2V130UQ5eY+HMkuNaoZ2fnrNwgEEFTqg6mrUsbKJsdCVHBbxWQpWucYfiefTOLipxrj/QLkJ8oV3AyvSVxW90jHIkVeevacxV4niG7EppJzvxRWlEb1/OPYXFyp/S7Agso4xpBZWrjv4zGcjilGFbsJ173p/mBoPsODj3m76CNqnCHcQAJewdQYi9r68FE2byJcv2KXlTHNvlMN8cD73767hmspMkZXxhEpfok2ZGfByKQOsiOft/HR9x2nnQPE4i2Qe3jP3OrCPtwYXxwrmFHG20L2n8sSMWXV5RJsRkP+IrP7PKsIaA57oJ9JKwvIvs5W7FbATHQkLywGEgwOt73FmU+9/s4nwWGTiAK9zaibQH9SYnBCYAvP3qn0yDPXVa+0j84CBD7Qestl00fbUmK51ObPgMEDvlCmdqkArAbsZrNuZ1MVmeOgeUI8UiZwVtu6co0Kxv8apLUJzxjbii06N1JRGq1JdE02MdVvsoUXBVn9STFI9Obajh/rdF5LyhFPtKyPYt/6SbeGH1ovdtzlWjG6Hj7OpqY1SwnqdIJGXX+6fDOT0FlmnBoP+W+nZw7vX9th4S7COdfQyrlJPoBSVrGhannpXcVTMZCjqUHRepa7PtOVFTlZmAppudd06ht336biwmoy9Hv2wvOtTU931Q/QpGQvsRqBVrJ0QS00iA5TuCINpiWxCWIXj39TtGPy0CP9nuniGHxCXT+1EndWY7B1o6C1S1QybtS2WcT0T+SW53D7E4lKw26a2qYxA/FiVxuM50PLQUGPBDIQgUrRamo5YM2/yPoyVeVPrkX2ZPYYp2cbhcSjIq6OhFSheRFcV7RP9ODVCttax3JFqozlXBgF2CiXSE3hG3WAuFmxgje6TGI9FkPDsgvoqDfUFIBGBexBVo0vaOCo2U1N8xaXMerxPeB0urTaCIDQQUKZPa9JZefy05fS3m9NQH3BgFPW22iw6Bohq2g06UUnWwdmb1XawlMw/WAF10laPaIYBpTU7QXA5JunHVjcICt/s8VXFo2N0wff/yQOHWt0zEn+WJLhCuvMdCFlRwozQdYR2qiBhQe7RoaM4Q5LqLYTL7vtmZVM5hrve4IHnQAwNnh72vlvhX0TnXiBXZG9xU/VKqmrBlBk69q0oKSUw42/kIi64ygEHnketi057VQs2iYJTJXOCuy4zSGkFRw3s460E9tYFQGgChwTlyc8wNIv/4WgQAreK+YJ3Czy/ZPGdVrbM3+WuwQqhjSXZ1cipOiuH+mTB1lDlcsdMdTMnAFymFa/M3lynoUDVPo/zow4BwVgjaD2mQxOr8rRi4k/pDTdQdCphaS96WM5+sSxuDQpaEFshJmXZKlci4Fwvz1vRXdZaw7eEKuyCyEKma58gwj1YyC0nwoyaB8Iap7xdy7PsypNKJJabd5juAYDuq4iIzB0aFhTfFsK3/cbohmVlHRA1aUp7KmoujrLohQOXL5tHwyl9wqYh2hA8hYpX39bJdWELhasLbcfey5ac8LbtxssjrDZrg3BSNxXxd1PPtiEGVBqvLrjXMKl2v+5ictz9+luc64p+vOiDV5moA2eQCYscOp8m7u+xC2Z/VBuhhWTVWVK1jC7eKXj4YyTSzw3AtrMHFNsxIBhTcIKORdrjr0XNs/oUNDspXlgLWPHZH1FTLR",
        "__VIEWSTATEGENERATOR": "3C0A46DB",
        "__EVENTVALIDATION": "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",
    }

    response = requests.post(
        "https://tradeautomationtoolbox.com/byob-ticks/",
        headers=headers,
        data=data,
    )
    try:
        return pd.read_csv(StringIO(response.text))
    except pd.errors.ParserError as e:
        with open("errors.txt", "a") as f:
            f.write(f"{max_premium}-{width}-{stop}-{start_date}-{end_date}")
            f.write("\n")


def get_last_date(directory: str) -> datetime.date | None:
    files = os.listdir(directory)
    if files:
        last_date = max([f.split(".")[0] for f in files])
        logging.info(last_date)
        try:
            return datetime.datetime.strptime(last_date, "%Y-%m-%d").date() + datetime.timedelta(days=1)
        except ValueError as e:
            logging.error(e)
            return None
    return None


if __name__ == "__main__":
    strategy_name = CONF.get("strategy_name")
    directory = f"../../data/byob/{strategy_name}"
    os.makedirs(directory) if not os.path.exists(directory) else None
    start_date = (
        get_last_date(directory) or CONF.get("start_date") or datetime.date(2020, 1, 1)
    )
    end_date = CONF.get("end_date") or datetime.date.today()
    dfs = []
    for experiment in CONF.get("strategies"):
        mini_experiments = [
            {
                **experiment,
                "start_date": st,
                "end_date": ed,
            }
            for st, ed in generate_date_ranges(start_date, end_date)
        ]
        for mini_experiment in mini_experiments:
            logging.info(f"Going for the experiment: {mini_experiment}")
            dfs.append(build_req_v2(**mini_experiment))
    if any(df is not None for df in dfs):
        csv_files = glob.glob(f"{directory}/*.csv")
        for file in csv_files:
            logging.info("concatening new data with existing file")
            df = pd.read_csv(file)
            dfs.append(df)
            logging.info("removing old csv file")
            os.remove(file)
        df = pd.concat(dfs)
        end_date = pd.to_datetime(df["EntryTime"]).dt.strftime("%Y-%m-%d").max()
        logging.info("saving data file")
        df.to_csv(f"{directory}/{end_date}.csv")
