import requests
import datetime
import csv

from .common import parse_date, ApiException

class WS2Api:
    BASE_URL = 'https://tconnectws2.tandemdiabetes.com/'

    userGuid = None

    def __init__(self, userGuid):
        self.userGuid = userGuid

    def get(self, endpoint, query):
        r = requests.get(self.BASE_URL + endpoint, query)
        if r.status_code != 200:
            raise ApiException(r.status_code, "WS2 API HTTP %s response: %s" % (str(r.status_code), r.text))
        return r.text


    def _split_empty_sections(self, text):
        sections = [[]]
        sectionIndex = 0
        for line in text.splitlines():
            if len(line.strip()) > 0:
                sections[sectionIndex].append(line)
            else:
                sections.append([])
                sectionIndex += 1

        return sections + [None] * (4 - len(sections))

    def _csv_to_dict(self, rawdata):
        data = []
        if not rawdata or len(rawdata) == 0:
            return data
        headers = rawdata[0].split(",")
        for row in csv.reader(rawdata[1:]):
            data.append({headers[i]: row[i] for i in range(len(row)) if i < len(headers)})

        return data


    def therapy_timeline_csv(self, start=None, end=None):
        startDate = parse_date(start)
        endDate = parse_date(end)

        req_text = self.get('therapytimeline2csv/%s/%s/%s?format=csv' % (self.userGuid, startDate, endDate), {})

        sections = self._split_empty_sections(req_text)

        readingData = None
        iobData = None
        basalData = None
        bolusData = None

        for s in sections:
            if s and len(s) > 2:
                firstrow = s[1].replace('"', '').strip()
                if firstrow.startswith("t:slim X2 Insulin Pump"):
                    readingData = s
                elif firstrow.startswith("IOB"):
                    iobData = s
                elif firstrow.startswith("Basal"):
                    basalData = s
                elif firstrow.startswith("Bolus"):
                    bolusData = s


        return {
            "readingData": self._csv_to_dict(readingData),
            "iobData": self._csv_to_dict(iobData),
            "basalData": self._csv_to_dict(basalData),
            "bolusData": self._csv_to_dict(bolusData)
        }
