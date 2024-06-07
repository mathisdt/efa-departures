#!/usr/bin/env python3

from pyhafas import HafasClient
from pyhafas.profile import DBProfile
import datetime
import zoneinfo
import re


def extract_departures_filtered(departures, target, end_time, dep_filter=None):
    for dep in departures:
        if dep.cancelled:
            continue
        if dep_filter is not None and not dep_filter(dep):
            continue
        result_item = {"stopName": re.sub(r'(^Hannover[ /]|, Hannover$| \(Hannover\)$)', '', dep.station.name),
                       "line": re.sub(r'^(STR|Bus) ', '', dep.name),
                       "direction": re.sub(r'(^Hannover[ /]|, Hannover$| \(Hannover\)$)', '', dep.direction),
                       "plan": dep.dateTime}
        if dep.delay is not None and dep.delay >= datetime.timedelta(minutes=1):
            result_item["realtime"] = dep.dateTime + dep.delay
        if get_time(result_item) < end_time:
            target[f'{dep.dateTime.strftime("%Y-%m-%d-%H-%M")}-{int(re.sub(r"[^0-9]", "", result_item["line"])):03d}'] = result_item


def get_time(entry):
    if "realtime" not in entry:
        return entry["plan"]
    else:
        return entry["realtime"]


def get_time_str(entry):
    if "realtime" not in entry or entry["realtime"] == entry["plan"]:
        return f'{entry["plan"].strftime("%H:%M")} Uhr'
    else:
        return f'{entry["realtime"].strftime("%H:%M")} Uhr ' \
               f'(<span class="toolate">' \
               f'{entry["plan"].strftime("%H:%M")} Uhr</span>)'


def entry_as_html_tr(entry):
    tr = f'<tr><td class="line">' \
         f'{entry["line"]}</td><td>{entry["direction"]}</td>' \
         f'<td>{get_time_str(entry)}<span class="stop"> @ {entry["stopName"]}</span></td></tr>'
    return tr


if __name__ == "__main__":
    client = HafasClient(DBProfile())
    now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("Europe/Berlin"))
    end_time = now + datetime.timedelta(minutes=40)

    location_bahnstrift = client.locations("Bahnstrift, Hannover")[0]
    departures_bahnstrift = client.departures(station=location_bahnstrift.id, date=now, max_trips=40)
    location_alteheide = client.locations("Alte Heide, Hannover")[0]
    departures_alteheide = client.departures(station=location_alteheide.id, date=now, max_trips=40)
    departures = {}
    extract_departures_filtered(departures_bahnstrift, departures, end_time,
                                lambda dep: re.search(r"Alte Heide", dep.direction) is None)
    extract_departures_filtered(departures_alteheide, departures, end_time,
                                lambda dep: re.search(r"\b2$", dep.name) is None and
                                            re.search(r"\b135$", dep.name) is None)
    departures = dict(sorted(departures.items()))

    print('<html><head><title>Abfahrten</title>'
          '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><style>'
          '.stop {color:#909090}'
          '.line {text-align:right;font-weight:bold;font-family: monospace;font-size: x-large;}'
          '.toolate {text-decoration:line-through;}'
          '</style>'
          '<body style="line-height: 1.5em; background-color: #000; color: #ffffff"><table>')
    for departure in departures.values():
        print(entry_as_html_tr(departure))
    print('</table></body></html>')
