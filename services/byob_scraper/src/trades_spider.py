import datetime
from pathlib import Path

import pandas as pd
import scrapy
import scrapy.http
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from .config import CONF, DEFAULT_DT, ENTRIES_PATH, TRADES_PATH
from .utils import get_last_date, is_any_dataframe_not_none, read_csv_wildcard


def byob_parse_table(table) -> pd.DataFrame:
    """
    Parse a table from scrapy xpath to pandas dataframe
    """
    data = []
    rows = table.xpath(".//tr")
    for row in rows:
        cells = row.xpath(".//td|.//th")
        row_data = []
        for cell in cells:
            cell_text = cell.xpath(".//text()").get(default="").strip()
            row_data.append(cell_text)
        data.append(row_data)
    return pd.DataFrame(data[1:], columns=data[0])


def merge(df: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Cross join two pandas dataframes
    """
    df["dummy"] = 1
    df2["dummy"] = 1
    result = pd.merge(df, df2, on="dummy")
    return result.drop(columns="dummy")


class ByobSpider(scrapy.Spider):
    name = "byob"

    def __init__(self, strategy: str, ids: list[int], **kwargs):
        super().__init__(**kwargs)
        self.output_dir: str = Path(f"{TRADES_PATH}-{strategy}")
        self.ids: list[int] = ids
        self.dfs: list = []

    def start_requests(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        urls = [
            (
                id,
                f"https://tradeautomationtoolbox.com/byob-ticks/trade.aspx?tradeid={id}",
            )
            for id in self.ids
        ]
        for id, url in urls:
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"id": id})

    def parse(self, response: scrapy.http.Response, id: int):
        tables = response.css("table")
        i = 0
        df_trade_information = pd.DataFrame()
        for table in tables:
            df = byob_parse_table(table)
            if i == 0:
                df_transposed = df.transpose().reset_index()
                df_final = df_transposed.rename(columns=df_transposed.iloc[0])
                df_trade_information = df_final.drop(df_final.index[0])
            if i == 1:
                df_merged = merge(df, df_trade_information)
                df_merged["TradeID"] = id
                self.dfs.append(df_merged)
            i += 1

    def close(self):
        if is_any_dataframe_not_none(self.dfs):
            # self.dfs.append(is_existing_csv_file(self.output_dir))
            df = pd.concat(self.dfs)
            end_date = (
                pd.to_datetime(df["Time"], errors="coerce")
                .dt.strftime("%Y-%m-%d")
                .max()
            )
            df.to_csv(f"{self.output_dir}/{end_date}.csv", index=False)


def run():
    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    runner = CrawlerRunner()
    for conf in CONF:
        entries_last_run = get_last_date(f"{ENTRIES_PATH}-{conf.strategy_name}")
        trades_last_run = get_last_date(f"{TRADES_PATH}-{conf.strategy_name}") or (
            DEFAULT_DT - datetime.timedelta(days=1)
        )
        max_date = trades_last_run + datetime.timedelta(days=30 * 6)
        if entries_last_run is not None and (trades_last_run < entries_last_run):
            df = read_csv_wildcard(f"{ENTRIES_PATH}-{conf.strategy_name}")
            df["EntryDate"] = pd.to_datetime(df["EntryTime"], errors="coerce").dt.date
            trade_ids = df[
                (df["EntryDate"] > trades_last_run) & (df["EntryDate"] <= max_date)
            ]["TradeID"].tolist()
            runner.crawl(ByobSpider, strategy=conf.strategy_name, ids=trade_ids)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    run()
