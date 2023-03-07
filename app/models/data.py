
from enum import Enum
from datetime import datetime

from constants import DB_DATETIME_FMT
from utils import parse_date


class DataModel:
    def __init__(self, title: str, uri: str, date: str | datetime):
        self.title = title
        self.uri = uri

        if isinstance(date, datetime):
            self.date = date
        else:
            try:
                self.date = parse_date(date)
            except ValueError as e:
                print(e)
                raise e

    def to_tuple(self) -> tuple[str, ...]:
        return self.title, self.uri, self.date.strftime(DB_DATETIME_FMT)

    def to_json(self) -> dict[str, str]:
        return {
            'title': self.title,
            'uri': self.uri,
            'date': self.date.strftime(DB_DATETIME_FMT),
        }

    @staticmethod
    def from_json(data: dict[str, str]) -> 'DataModel':
        return DataModel(title=data['title'],
                         uri=data['uri'],
                         date=data['date'])

    @staticmethod
    def from_db(title: str, url: str, date: datetime):
        return DataModel(title=title,
                         uri=url,
                         date=date)


class SearchQueryDateFilter(Enum):
    before = 'before'
    after = 'after'
    between = 'between'
