#!/usr/bin/env python3

import aiohttp
import asyncio
import datetime
import json
import re


class EFA:
    """
    Inspiration: https://finalrewind.org/interblag/entry/efa-json-api/
    """
    def __init__(self, url, proximity_search=False):
        self.dm_url = url + "/XML_DM_REQUEST"
        self.dm_post_data = {
            "language": "de",
            "mode": "direct",
            "outputFormat": "JSON",
            "type_dm": "stop",
            "useProxFootSearch": "0",
            "useRealtime": "1",
        }

        if proximity_search:
            self.dm_post_data["useProxFootSearch"] = "1"

    async def get_departures(self, place, name, ts):
        self.dm_post_data.update(
            {
                "itdDateDay": ts.day,
                "itdDateMonth": ts.month,
                "itdDateYear": ts.year,
                "itdTimeHour": ts.hour,
                "itdTimeMinute": ts.minute,
                "name_dm": name,
            }
        )
        if place is None:
            self.dm_post_data.pop("place_dm", None)
        else:
            self.dm_post_data.update({"place_dm": place})
        async with aiohttp.ClientSession() as session:
            async with session.post(self.dm_url, data=self.dm_post_data) as response:
                # EFA may return JSON with a text/html Content-Type, which response.json() does not like.
                departures = json.loads(await response.text())
        return departures


def extract_departures_filtered(response, target, end_time, dep_filter=None):
    for dep in response["departureList"]:
        if dep_filter is not None and not dep_filter(dep):
            continue
        result_item = {"stopName": dep["nameWO"],
                       "line": dep["servingLine"]["number"],
                       "direction": re.sub(r'^Hannover[ /]', '', dep["servingLine"]["direction"]),
                       "plan": {
                           "year": f'{int(dep["dateTime"]["year"]):04d}',
                           "month": f'{int(dep["dateTime"]["month"]):02d}',
                           "day": f'{int(dep["dateTime"]["day"]):02d}',
                           "hour": f'{int(dep["dateTime"]["hour"]):02d}',
                           "minute": f'{int(dep["dateTime"]["minute"]):02d}'}}
        if "realDateTime" in dep:
            result_item["realtime"] = {
                "year": f'{int(dep["realDateTime"]["year"]):04d}',
                "month": f'{int(dep["realDateTime"]["month"]):02d}',
                "day": f'{int(dep["realDateTime"]["day"]):02d}',
                "hour": f'{int(dep["realDateTime"]["hour"]):02d}',
                "minute": f'{int(dep["realDateTime"]["minute"]):02d}'}
        if get_time(result_item) < end_time:
            target[f'{result_item["plan"]["year"]}-{result_item["plan"]["month"]}-{result_item["plan"]["day"]}'
                   f'-{result_item["plan"]["hour"]}-{result_item["plan"]["minute"]}-{int(result_item["line"]):03d}'] \
                = result_item


def get_time(entry):
    if "realtime" not in entry:
        return datetime.datetime(int(entry["plan"]["year"]), int(entry["plan"]["month"]), int(entry["plan"]["day"]),
                                 int(entry["plan"]["hour"]), int(entry["plan"]["minute"]))
    else:
        return datetime.datetime(int(entry["realtime"]["year"]), int(entry["realtime"]["month"]),
                                 int(entry["realtime"]["day"]),
                                 int(entry["realtime"]["hour"]), int(entry["realtime"]["minute"]))


def get_time_str(entry):
    if "realtime" not in entry or entry["realtime"] == entry["plan"]:
        return f'{entry["plan"]["hour"]}:{entry["plan"]["minute"]} Uhr'
    else:
        return f'{entry["realtime"]["hour"]}:{entry["realtime"]["minute"]} Uhr ' \
               f'(<span class="toolate">' \
               f'{entry["plan"]["hour"]}:{entry["plan"]["minute"]} Uhr</span>)'


def entry_as_html_tr(entry):
    tr = f'<tr><td class="line">' \
         f'{entry["line"]}</td><td>{entry["direction"]}</td>' \
         f'<td>{get_time_str(entry)}<span class="stop"> @ {entry["stopName"]}</span></td></tr>'
    return tr


async def main():
    now = datetime.datetime.now()
    end_time = now + datetime.timedelta(minutes=40)
    response_bahnstrift = await EFA("https://www.efa.de/efa/").get_departures(
        "Bahnstrift", "Hannover", now)
    response_alteheide = await EFA("https://www.efa.de/efa/").get_departures(
        "Alte Heide", "Hannover", now)
    departures = {}
    extract_departures_filtered(response_bahnstrift, departures, end_time,
                                lambda dep: dep["servingLine"]["direction"] != "Hannover/Alte Heide")
    extract_departures_filtered(response_alteheide, departures, end_time,
                                lambda dep: dep["servingLine"]["number"] != "2" and
                                            dep["servingLine"]["number"] != "135")
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


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
