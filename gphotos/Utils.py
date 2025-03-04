#!/usr/bin/env python3
# coding: utf8
import re
from datetime import datetime
from tempfile import NamedTemporaryFile
from os import utime, unlink, getcwd
import logging

log = logging.getLogger(__name__)

DATE_NORMALIZE = re.compile(r'(\d\d\d\d).(\d\d).(\d\d).(\d\d).(\d\d).(\d\d)')
SHORT_DATE_NORMALIZE = re.compile(r'(\d\d\d\d).(\d\d).(\d\d)')
PatType = type(DATE_NORMALIZE)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_ONLY = "%Y-%m-%d"
MINIMUM_DATE = None


# incredibly windows cannot handle dates below 1980
def safe_str_time(date_time: datetime, date_format: str) -> str:
    global MINIMUM_DATE
    if date_time < MINIMUM_DATE:
        date_time = MINIMUM_DATE
    return date_time.strftime(date_format)


def safe_timestamp(d: datetime) -> float:
    global MINIMUM_DATE
    if d < MINIMUM_DATE:
        d = MINIMUM_DATE
    return d


def date_to_string(date_t: datetime):
    return date_t.strftime(DATE_FORMAT)


def maximum_date() -> datetime:
    return datetime.max


def minimum_date() -> datetime:
    global MINIMUM_DATE
    with NamedTemporaryFile(dir=getcwd()) as t:
        # determine the minimum date that is usable on the
        # current platform (is there a better way to do this?)
        min_dates = (1800, 1900, 1970, 1971, 1980)

        for min_date in min_dates:
            try:
                d = datetime.min.replace(year=min_date)
                utime(t.name, (d.timestamp(), d.timestamp()))
            except (ValueError, OverflowError, OSError):
                continue
            break

    if not d:
        raise ValueError('cannot set file modification date')
    MINIMUM_DATE = d
    log.debug('MINIMUM_DATE = %s' % MINIMUM_DATE)
    return MINIMUM_DATE


def date_string_normalize(date_in: str,
                          pattern_in: PatType,
                          pattern_out: str) -> datetime:
    result = None
    matches = pattern_in.match(date_in)
    if matches:
        normalized = pattern_out.format(*matches.groups())
        result = datetime.strptime(normalized, DATE_FORMAT)
    return result


def string_to_date(date_string: str) -> datetime:
    result = None
    if date_string:
        result = date_string_normalize(date_string, DATE_NORMALIZE,
                                       '{}-{}-{} {}:{}:{}')
        if result is None:
            result = date_string_normalize(date_string, SHORT_DATE_NORMALIZE,
                                           '{}-{}-{} 00:00:00')
        if result is None:
            log.warning('WARNING: time string %s illegal', date_string)

    return result
