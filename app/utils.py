from dateutil import parser as dt_parser
from datetime import datetime


def parse_date(date: str) -> datetime:
    return dt_parser.parse(date, ignoretz=True, fuzzy=True)