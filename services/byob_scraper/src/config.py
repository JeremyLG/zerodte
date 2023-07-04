import datetime

from pydantic import BaseModel


class Conf(BaseModel):
    width: str
    stop: str
    min_premium: float | None
    max_premium: float | None
    entries: list[str] | None

    @property
    def premium(self):
        return self.max_premium or self.min_premium

    @property
    def strategy_name(self):
        return f"{self.premium}-{self.width}-{self.stop}"


CONF = [
    Conf(width="-25", stop="1x", max_premium=2.1),
    Conf(width="-25", stop="1.5x", max_premium=2.1),
]

BYOB_PATH = "../../data/byob/"
ENTRIES_PATH = f"{BYOB_PATH}/all-entries"
TRADES_PATH = f"{BYOB_PATH}/all-trades"

DEFAULT_DT = datetime.date(2020, 1, 1)
