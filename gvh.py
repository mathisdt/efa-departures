import datetime
from typing import Optional, Dict, List

import pytz
from pyhafas.profile import BaseProfile, ProfileInterface
from pyhafas.types.fptf import Station, StationBoardLeg
from pyhafas.types.hafas_response import HafasResponse
from pyhafas.types.station_board_request import StationBoardRequestType


class GVHProfile(BaseProfile):
    """
    Profile of the HaFAS of Großraumverkehr Hannover (GVH) - regional in Hannover area
    """
    baseUrl = "https://gvh.hafas.de/hamm"
    defaultUserAgent = "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0"

    locale = 'de-DE'
    timezone = pytz.timezone('Europe/Berlin')

    requestBody = {
        'client': {
            'id': 'HAFAS',
            'l': 'vs_webapp',
            'name': 'webapp',
            'type': 'WEB',
            'v': '10109'
        },
        'ver': '1.62',
        'lang': 'deu',
        'auth': {
            'type': 'AID',
            'aid': 'IKSEvZ1SsVdfIRSK'
        }
    }

    availableProducts = {
        "ice": [1],
        "ic-ec": [2, 4],
        "re-rb": [8],
        "s-bahn": [16],
        "stadtbahn": [256],
        "bus": [32],
        "on-demand": [512]
    }

    defaultProducts = [
        "ice",
        "ic-ec",
        "re-rb",
        "s-bahn",
        "stadtbahn",
        "bus",
        "on-demand"
    ]

    def parse_lid_to_station(
            self: ProfileInterface,
            lid: str,
            name: str = "",
            latitude: float = 0,
            longitude: float = 0) -> Station:
        """
        Parses the LID given by HaFAS to a station object

        :param lid: Location identifier (given by HaFAS)
        :param name: Station name (optional, if not given, LID is used)
        :param latitude: Latitude of the station (optional, if not given, LID is used)
        :param longitude: Longitude of the station (optional, if not given, LID is used)
        :return: Parsed LID as station object
        """
        parsed_lid = lid.split(":")

        return Station(
            id=parsed_lid[1],
            lid=lid,
            name=name,
            latitude=latitude,
            longitude=longitude
        )

    def format_station_board_request(
            self: ProfileInterface,
            station: Station,
            request_type: StationBoardRequestType,
            date: datetime.datetime,
            max_trips: int,
            duration: int,
            products: Dict[str, bool],
            direction: Optional[Station]
    ) -> dict:
        """
        Creates the HaFAS request for a station board request (departure/arrival)

        :param station: Station to get departures/arrivals for
        :param request_type: ARRIVAL or DEPARTURE
        :param date: Date and time to get departures/arrival for
        :param max_trips: Maximum number of trips that can be returned
        :param products: Allowed products (e.g. ICE,IC)
        :param duration: Time in which trips are searched
        :param direction: Direction (end) station of the train. If none, filter will not be applied
        :return: Request body for HaFAS
        """
        return {
            'req': {
                'type': request_type.value,
                'stbLoc': {
                    'lid': station.lid
                },
                'dirLoc': {
                    'lid': direction.lid
                } if direction is not None else None,
                'maxJny': max_trips,
                'date': date.strftime("%Y%m%d"),
                'time': date.strftime("%H%M%S"),
                'dur': duration,
                'jnyFltrL': [
                    self.format_products_filter(products)
                ],
            },
            'meth': 'StationBoard'
        }

    def parse_station_board_request(
            self: ProfileInterface,
            data: HafasResponse,
            departure_arrival_prefix: str) -> List[StationBoardLeg]:
        """
        Parses the HaFAS data for a station board request

        :param data: Formatted HaFAS response
        :param departure_arrival_prefix: Prefix for specifying whether its for arrival or departure (either "a" or "d")
        :return: List of StationBoardLeg objects
        """
        legs = []
        if not data.res.get('jnyL', False):
            return legs
        else:
            for raw_leg in data.res['jnyL']:
                date = self.parse_date(raw_leg['date'])

                try:
                    platform = raw_leg['stbStop'][departure_arrival_prefix + 'PltfR']['txt'] if \
                        raw_leg['stbStop'].get(departure_arrival_prefix + 'PltfR') is not None else \
                        raw_leg['stbStop'][departure_arrival_prefix + 'PltfS']['txt']
                except KeyError:
                    platform = raw_leg['stbStop'].get(
                        departure_arrival_prefix + 'PlatfR',
                        raw_leg['stbStop'].get(
                            departure_arrival_prefix + 'PlatfS',
                            None))

                legs.append(StationBoardLeg(
                    id=raw_leg['jid'],
                    name=data.common['prodL'][raw_leg['prodX']]['name'],
                    direction=raw_leg.get('dirTxt'),
                    date_time=self.parse_datetime(
                        raw_leg['stbStop'][departure_arrival_prefix + 'TimeS'],
                        date
                    ),
                    station=self.parse_lid_to_station(data.common['locL'][raw_leg['stbStop']['locX']]['lid'],
                                                      name=data.common['locL'][raw_leg['stbStop']['locX']]['name']),
                    platform=platform,
                    delay=self.parse_datetime(
                        raw_leg['stbStop'][departure_arrival_prefix + 'TimeR'],
                        date) - self.parse_datetime(
                        raw_leg['stbStop'][departure_arrival_prefix + 'TimeS'],
                        date) if raw_leg['stbStop'].get(departure_arrival_prefix + 'TimeR') is not None else None,
                    cancelled=bool(raw_leg['stbStop'].get(departure_arrival_prefix + 'Cncl', False))
                ))
            return legs
