from datetime import datetime

import pymysql
import pymysql.cursors
import os

from models.data import DataModel


db_conn = pymysql.connect(host=os.environ['ENV_DB_HOST'],
                          port=int(os.environ['ENV_DB_PORT']),
                          user=os.environ['ENV_DB_USER'],
                          password=os.environ['ENV_DB_PSWD'])


def search_string(column: str, query: str) -> tuple:
    with db_conn.cursor() as crsr:
        sql_cmd = 'SELECT title, url, date_added FROM exercise.data WHERE ' + \
            f'{column} LIKE \'%{query}\' OR ' + \
            f'{column} LIKE \'{query}%\' OR ' + \
            f'{column} LIKE \'%{query}%\';'
        crsr.execute(sql_cmd)
        return crsr.fetchall()


def search_by_title(title: str) -> list[DataModel]:
    results = []
    for res in search_string('title', title):
        results.append(DataModel.from_db(*res))

    return results


def search_by_url(url: str) -> list[DataModel]:
    results = []
    for res in search_string('url', url):
        results.append(DataModel.from_db(*res))

    return results


def _search_by_date(date: datetime, comparison_operator: str) -> tuple:
    with db_conn.cursor() as crsr:
        sql_cmd = 'SELECT title, url, date_added FROM exercise.data WHERE ' + \
                  f'date_added {comparison_operator} %s'
        crsr.execute(sql_cmd, date)
        return crsr.fetchall()


def search_by_date_before(date: datetime) -> list[DataModel]:
    return [DataModel.from_db(*entry) for entry in _search_by_date(date, '<=')]


def search_by_date_after(date: datetime) -> list[DataModel]:
    return [DataModel.from_db(*entry) for entry in _search_by_date(date, '>=')]


def search_by_date_between(start_date: datetime, end_date: datetime) -> list[DataModel]:
    with db_conn.cursor() as crsr:
        sql_cmd = 'SELECT title, url, date_added FROM exercise.data WHERE ' + \
                  'date_added >= %s AND date_added <= %s'
        crsr.execute(sql_cmd, (start_date, end_date))
        query_results = crsr.fetchall()

    return [DataModel.from_db(*entry) for entry in query_results]


def ingest_json_data(js_data: dict):
    with db_conn.cursor() as crsr:
        for item in js_data['items']:
            try:
                # Create the data model to ensure datetime formatting is valid
                dm = DataModel.from_json(item)
                # Insert
                crsr.execute('INSERT INTO exercise.data ' +
                             '(title, url, date_added) VALUES (%s, %s, %s);',
                             dm.to_tuple())
            except ValueError:
                print(f'Invalid record: {item}')
                continue
            except Exception as e:
                print(f'Unspecified error: {e}')
                continue
    db_conn.commit()
