
from json2html import json2html
from flask import Flask, make_response, render_template, request
from flask_bootstrap import Bootstrap

from db_controller import *
from models.data import DataModel, SearchQueryDateFilter
from utils import parse_date

app = Flask(__name__)
Bootstrap(app)


def parse_search_query(title: str | None, url: str | None, date: str | None) -> list[DataModel] | tuple[str, int]:
    if title:
        return search_by_title(title)
    elif url:
        return search_by_url(url)
    elif date:
        try:
            filter_type = SearchQueryDateFilter(
                request.args.get('radio-datefilter', 'after').lower().strip()
            )
            start_date = parse_date(date)
            match filter_type:
                case SearchQueryDateFilter.before:
                    return search_by_date_before(start_date)
                case SearchQueryDateFilter.after:
                    return search_by_date_after(start_date)
                case SearchQueryDateFilter.between:
                    end_date = request.args.get('datetime-picker-enddate')
                    if not end_date:
                        return 'No end date specified, but filter "between" was selected!', 400

                    end_date = parse_date(end_date)
                    return search_by_date_between(start_date, end_date)
        except ValueError:
            return 'Invalid date or search filter', 400
    return 'Invalid input', 500


@app.get('/search')
def search_data():
    title = request.args.get('db-search-title')
    url = request.args.get('db-search-url')
    date = request.args.get('datetime-picker-date')

    if res := parse_search_query(title, url, date):
        # The result of `parse_search_query` will be a tuple[str, int]
        # when an error has occurred; the string will identify the error,
        # and the int value will be the HTTP return code.
        if isinstance(res, tuple):
            return make_response(*res)
        item_list = {'items': [entry.to_json() for entry in res]}
        return make_response(json2html.convert(json=item_list), 200) #type: ignore
    return make_response('Record(s) not found', 404)


@app.post('/ingest/json')
def ingest_json():
    js_data = request.json
    if (not js_data) or ('items' not in js_data):
        return 'Invalid JSON', 400

    ingest_json_data(js_data)

    return '', 204


@app.route('/')
def homepage():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
