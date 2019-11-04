# MIT License
#
# Copyright (c) 2019 Nirmal AK, nirmal@merklescience.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import requests
from time import time
from math import floor
from datetime import datetime, timedelta

CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "")

class CryptoCompareRequestException(Exception):
    pass

def get_hour_id_from_ts(timestamp: int) -> int:
    """
    returns the number of hours elapsed since 1st Jan 2000
    """
    base_ts = datetime(2000, 1, 1).timestamp()
    seconds_to_hour = 60 * 60
    return floor((int(timestamp) - base_ts) / seconds_to_hour)


def get_day_id_from_ts(timestamp: int) -> int:
    """
    returns the number of days elapsed since 1st Jan 2000
    """
    base_ts = datetime(2000, 1, 1).timestamp()
    seconds_to_day = 60 * 60 * 24
    return floor((int(timestamp) - base_ts) / seconds_to_day)


def get_ts_from_hour_id(hour_id: int) -> int:
    base_date = datetime(2000, 1, 1)
    reference_date = base_date + timedelta(hours=hour_id)
    return floor(reference_date.timestamp())


def get_ts_from_day_id(day_id: int) -> int:
    base_date = datetime(2000, 1, 1)
    reference_date = base_date + timedelta(days=day_id)
    return floor(reference_date.timestamp())


def _make_request(
        resource: str, 
        from_currency_code: str,
        to_currency_code: str,
        timestamp: int,
        access_token: str,
        exchange_code: str,
        num_records: int,
        api_version: str
    ) -> requests.Response:
    """
    API documentation for cryptocompare can be found at https://min-api.cryptocompare.com/documentation
    """
    base_url = f"https://min-api.cryptocompare.com/data/{api_version}/{resource}"
    params = {
        "fsym": from_currency_code,
        "tsym": to_currency_code,
        "e": exchange_code,
        "limit": num_records,
        "toTs": timestamp,
        "api_key": access_token
    }

    return requests.get(base_url, params=params)


def get_coin_price(
        from_currency_code: str, 
        timestamp: int,
        resource="histohour",
        to_currency_code: str="USD",
        exchange_code: str="CCCAGG",
        num_records: int=1,
        api_version: str ="v2",
        access_token: str=CRYPTOCOMPARE_API_KEY,
    ):
    """
    Prices are retrieved from hourly price resource as prices 
    are available for historical data from when available
    """
    response = _make_request(
        resource=resource,
        from_currency_code=from_currency_code,
        to_currency_code=to_currency_code,
        timestamp=int(timestamp),
        access_token=access_token,
        exchange_code=exchange_code,
        num_records=num_records,
        api_version=api_version,
    )
    if not response.status_code == 200:
        raise CryptoCompareRequestException

    payload = response.json()
    if payload["Type"] != 100:
        raise CryptoCompareRequestException(payload.get("Message", ""))

    data = payload["Data"]["Data"]
    avg_price = sum(item["open"] for item in data) / len(data)
    return round(avg_price, 2)
