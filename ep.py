#!/usr/bin/env python3

import argparse
import requests
import sys
import time

from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
from itertools import chain
from prettytable import PrettyTable


Trip = namedtuple(
    'Trip', [
        'dispatch_station',
        'arrival_station',
        'dispatch_time',
        'arrival_time',
        'rate'])


def main():
    args = _parse_arguments()
    trips = _fetch_trips(args.dispatch, args.arrival)

    if not args.all:
        trips = _filter_dispatched_trips(trips)

    table = _create_table(trips)

    print(table)


def _parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('dispatch')
    parser.add_argument('arrival')
    parser.add_argument('--all', action='store_const', const=True)

    return parser.parse_args()


def _fetch_trips(dispatch, arrival):
    response = requests.get(
        'http://express-prigorod.ru/schedule',
        params={
            'dispatch': dispatch.encode('cp1251'),
            'arrival': arrival.encode('cp1251')
        })

    soup = BeautifulSoup(response.content.decode('cp1251'))
    schedule = soup.find(id='schedule')

    trips = []

    for row in schedule.tbody.find_all('tr'):
        cells = row.find_all('td')
        stations = _parse_stations(cells[1])
        rest = [item.text for item in cells[2:]]

        trips.append(Trip(*chain(stations, rest)))

    return trips


def _parse_stations(stations):
    return [item.text for item in stations.find_all('a')]


def _filter_dispatched_trips(trips):
    return [trip for trip in trips if _is_future_trip(trip)]


def _is_future_trip(trip):
    now = datetime.now().time()
    dispatch_time = datetime.fromtimestamp(
        time.mktime(time.strptime(trip.dispatch_time, '%H:%M'))).time()

    return dispatch_time > now


def _create_table(trips):
    pt = PrettyTable()
    pt.header = False
    for item in trips:
        pt.add_row(item)

    return pt


if __name__ == '__main__':
    sys.exit(main())
