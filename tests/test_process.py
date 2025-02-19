#!/usr/bin/env python3

import unittest
import datetime
import pprint

from tconnectsync.process import process_time_range
from tconnectsync.parser.nightscout import NightscoutEntry

from .api.fake import TConnectApi
from .nightscout_fake import NightscoutApi
from .sync.test_basal import TestBasalSync
from .sync.test_bolus import TestBolusSync

class TestProcessTimeRange(unittest.TestCase):
    maxDiff = None

    def stub_therapy_timeline(self, time_start, time_end):
        pass

    def stub_therapy_timeline_csv(self, time_start, time_end):
        return {
            "readingData": [],
            "iobData": [],
            "basalData": [],
            "bolusData": []
        }

    def stub_last_uploaded_entry(self, event_type):
        return None

    def stub_last_uploaded_activity(self, activity_type):
        return None

    """No data in Nightscout. Uploads all basal data from tconnect."""
    def test_new_ciq_basal_data(self):
        tconnect = TConnectApi()

        start = datetime.datetime(2021, 4, 20, 12, 0)
        end = datetime.datetime(2021, 4, 21, 12, 0)

        def fake_therapy_timeline(time_start, time_end):
            self.assertEqual(time_start, start)
            self.assertEqual(time_end, end)

            return TestBasalSync.get_example_ciq_basal_events()

        tconnect.controliq.therapy_timeline = fake_therapy_timeline
        tconnect.ws2.therapy_timeline_csv = self.stub_therapy_timeline_csv

        nightscout = NightscoutApi()

        nightscout.last_uploaded_entry = self.stub_last_uploaded_entry
        nightscout.last_uploaded_activity = self.stub_last_uploaded_activity

        process_time_range(tconnect, nightscout, start, end, pretend=False)

        self.assertEqual(len(nightscout.uploaded_entries["treatments"]), 4)
        self.assertDictEqual(dict(nightscout.uploaded_entries), {
            "treatments": [
                NightscoutEntry.basal(0.8, 20.35, "2021-03-16 00:00:00-04:00", reason="tempDelivery"),
                NightscoutEntry.basal(0.799, 5.0, "2021-03-16 00:20:21-04:00", reason="profileDelivery"),
                NightscoutEntry.basal(0.797, 5.0, "2021-03-16 00:25:21-04:00", reason="algorithmDelivery"),
                NightscoutEntry.basal(0, 2693/60, "2021-03-16 00:30:21-04:00", reason="algorithmDelivery")
        ]})
        self.assertDictEqual(nightscout.put_entries, {})
        self.assertDictEqual(nightscout.deleted_entries, {})


    """Two basal entries in Nightscout. Two new basal entries in tconnect."""
    def test_partial_ciq_basal_data(self):
        tconnect = TConnectApi()

        start = datetime.datetime(2021, 4, 20, 12, 0)
        end = datetime.datetime(2021, 4, 21, 12, 0)

        def fake_therapy_timeline(time_start, time_end):
            self.assertEqual(time_start, start)
            self.assertEqual(time_end, end)

            return TestBasalSync.get_example_ciq_basal_events()

        tconnect.controliq.therapy_timeline = fake_therapy_timeline
        tconnect.ws2.therapy_timeline_csv = self.stub_therapy_timeline_csv

        nightscout = NightscoutApi()

        def fake_last_uploaded_entry(event_type):
            if event_type == "Temp Basal":
                return {
                    "created_at": "2021-03-16 00:20:21-04:00",
                    "duration": 5
                }

        nightscout.last_uploaded_entry = fake_last_uploaded_entry
        nightscout.last_uploaded_activity = self.stub_last_uploaded_activity

        process_time_range(tconnect, nightscout, start, end, pretend=False)

        self.assertEqual(len(nightscout.uploaded_entries["treatments"]), 2)
        self.assertDictEqual(dict(nightscout.uploaded_entries), {
            "treatments": [
                NightscoutEntry.basal(0.797, 5.0, "2021-03-16 00:25:21-04:00", reason="algorithmDelivery"),
                NightscoutEntry.basal(0, 2693/60, "2021-03-16 00:30:21-04:00", reason="algorithmDelivery")
        ]})
        self.assertDictEqual(nightscout.put_entries, {})
        self.assertDictEqual(nightscout.deleted_entries, {})


    """
    Two basal entries in Nightscout, the latter which needs to be updated
    with a longer duration. Two entirely new entries in tconnect."""
    def test_with_updated_duration_ciq_basal_data(self):
        tconnect = TConnectApi()

        start = datetime.datetime(2021, 4, 20, 12, 0)
        end = datetime.datetime(2021, 4, 21, 12, 0)

        def fake_therapy_timeline(time_start, time_end):
            self.assertEqual(time_start, start)
            self.assertEqual(time_end, end)

            return TestBasalSync.get_example_ciq_basal_events()

        tconnect.controliq.therapy_timeline = fake_therapy_timeline
        tconnect.ws2.therapy_timeline_csv = self.stub_therapy_timeline_csv

        nightscout = NightscoutApi()

        def fake_last_uploaded_entry(event_type):
            if event_type == "Temp Basal":
                return {
                    "created_at": "2021-03-16 00:20:21-04:00",
                    "duration": 3,
                    "_id": "nightscout_id"
                }

        nightscout.last_uploaded_entry = fake_last_uploaded_entry
        nightscout.last_uploaded_activity = self.stub_last_uploaded_activity

        process_time_range(tconnect, nightscout, start, end, pretend=False)

        self.assertEqual(len(nightscout.uploaded_entries["treatments"]), 2)
        self.assertDictEqual(nightscout.uploaded_entries, {
            "treatments": [
                NightscoutEntry.basal(0.797, 5.0, "2021-03-16 00:25:21-04:00", reason="algorithmDelivery"),
                NightscoutEntry.basal(0, 2693/60, "2021-03-16 00:30:21-04:00", reason="algorithmDelivery")
        ]})
        self.assertEqual(len(nightscout.put_entries["treatments"]), 1)
        self.assertDictEqual(dict(nightscout.put_entries), {
            "treatments": [
                {
                    "_id": "nightscout_id",
                    **NightscoutEntry.basal(0.799, 5.0, "2021-03-16 00:20:21-04:00", reason="profileDelivery")
                }
            ]
        })
        self.assertDictEqual(nightscout.deleted_entries, {})

    """No data in Nightscout. Uploads all bolus data from tconnect."""
    def test_new_ciq_bolus_data(self):
        tconnect = TConnectApi()

        start = datetime.datetime(2021, 4, 20, 12, 0)
        end = datetime.datetime(2021, 4, 21, 12, 0)

        tconnect.controliq.therapy_timeline = self.stub_therapy_timeline

        def fake_therapy_timeline_csv(time_start, time_end):
            return {
                **self.stub_therapy_timeline_csv(time_start, time_end),
                "bolusData": TestBolusSync.get_example_csv_bolus_events(),
            }

        tconnect.ws2.therapy_timeline_csv = fake_therapy_timeline_csv

        nightscout = NightscoutApi()

        nightscout.last_uploaded_entry = self.stub_last_uploaded_entry
        nightscout.last_uploaded_activity = self.stub_last_uploaded_activity

        process_time_range(tconnect, nightscout, start, end, pretend=False)

        pprint.pprint(nightscout.uploaded_entries)
        self.assertEqual(len(nightscout.uploaded_entries["treatments"]), 3)
        self.assertDictEqual(dict(nightscout.uploaded_entries), {
            "treatments": [
                NightscoutEntry.bolus(13.53, 75, "2021-04-01 12:58:26-04:00", notes="Standard/Correction"),
                NightscoutEntry.bolus(1.25, 0, "2021-04-01 23:23:17-04:00", notes="Standard (Override)"),
                NightscoutEntry.bolus(1.7, 0, "2021-04-02 01:00:47-04:00", notes="Automatic Bolus/Correction"),
        ]})
        self.assertDictEqual(nightscout.put_entries, {})
        self.assertDictEqual(nightscout.deleted_entries, {})



if __name__ == '__main__':
    unittest.main()