#!/usr/bin/env python3

import unittest
from tconnectsync.parser.tconnect import TConnectEntry

class TestTConnectEntryBasal(unittest.TestCase):
    def test_parse_ciq_basal_entry(self):
        self.assertEqual(
            TConnectEntry.parse_ciq_basal_entry({
                "y": 0.8,
                "duration": 1221,
                "x": 1615878000
            }),
            {
                "time": "2021-03-16 00:00:00-04:00",
                "delivery_type": "",
                "duration_mins": 1221/60,
                "basal_rate": 0.8,
            }
        )

        self.assertEqual(
            TConnectEntry.parse_ciq_basal_entry({
                "y": 0.797,
                "duration": 300,
                "x": 1615879521
            }, delivery_type="algorithmDelivery"),
            {
                "time": "2021-03-16 00:25:21-04:00",
                "delivery_type": "algorithmDelivery",
                "duration_mins": 5,
                "basal_rate": 0.797,
            }
        )

class TestTConnectEntryBolus(unittest.TestCase):
    entryStdCorrection = {
        "Type": "Bolus",
        "Description": "Standard/Correction",
        "BG": "141",
        "IOB": "",
        "BolusRequestID": "7001.000",
        "BolusCompletionID": "7001.000",
        "CompletionDateTime": "2021-04-01T12:58:26",
        "InsulinDelivered": "13.53",
        "FoodDelivered": "12.50",
        "CorrectionDelivered": "1.03",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-04-01T12:53:36",
        "RequestDateTime": "2021-04-01T12:53:36",
        "BolusType": "Carb",
        "BolusRequestOptions": "Standard/Correction",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "75",
        "UserOverride": "0",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "12.50",
        "CorrectionBolusSize": "1.03",
        "ActualTotalBolusRequested": "13.53",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Correction & Food Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110",
        "IndexID": "0",
        "Note": "1181649"
    }
    def test_parse_bolus_entry_std_correction(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStdCorrection),
            {
                "description": "Standard/Correction",
                "complete": "1",
                "completion": "Completed",
                "request_time": "2021-04-01 12:53:36-04:00",
                "completion_time": "2021-04-01 12:58:26-04:00",
                "insulin": "13.53",
                "carbs": "75",
                "user_override": "0",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
        })
    
    entryStd = {
        "Type": "Bolus",
        "Description": "Standard",
        "BG": "159",
        "IOB": "2.13",
        "BolusRequestID": "7007.000",
        "BolusCompletionID": "7007.000",
        "CompletionDateTime": "2021-04-01T23:23:17",
        "InsulinDelivered": "1.25",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "0.00",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-04-01T23:21:58",
        "RequestDateTime": "2021-04-01T23:21:58",
        "BolusType": "Carb",
        "BolusRequestOptions": "Standard",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "0",
        "UserOverride": "1",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "0.00",
        "ActualTotalBolusRequested": "1.25",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Food Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110 | Override: Pump calculated Bolus = 0.0 units",
        "IndexID": "0",
        "Note": "1182867"
    }
    def test_parse_bolus_entry_std(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStd),
            {
                "description": "Standard",
                "complete": "1",
                "completion": "Completed",
                "request_time": "2021-04-01 23:21:58-04:00",
                "completion_time": "2021-04-01 23:23:17-04:00",
                "insulin": "1.25",
                "carbs": "0",
                "user_override": "1",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
        })
    
    entryStdAutomatic = {
        "Type": "Bolus",
        "Description": "Automatic Bolus/Correction",
        "BG": "",
        "IOB": "3.24",
        "BolusRequestID": "7010.000",
        "BolusCompletionID": "7010.000",
        "CompletionDateTime": "2021-04-02T01:00:47",
        "InsulinDelivered": "1.70",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "1.70",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-04-02T00:59:13",
        "RequestDateTime": "2021-04-02T00:59:13",
        "BolusType": "Automatic Correction",
        "BolusRequestOptions": "Automatic Bolus/Correction",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "0",
        "UserOverride": "0",
        "TargetBG": "160",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "1.70",
        "ActualTotalBolusRequested": "1.70",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Correction Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:0 - Target BG 160",
        "IndexID": "0",
        "Note": "1183132"
    }
    def test_parse_bolus_entry_std_automatic(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStdAutomatic),
            {
                "description": "Automatic Bolus/Correction",
                "complete": "1",
                "completion": "Completed",
                "request_time": "2021-04-02 00:59:13-04:00",
                "completion_time": "2021-04-02 01:00:47-04:00",
                "insulin": "1.70",
                "carbs": "0",
                "user_override": "0",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
        })



if __name__ == '__main__':
    unittest.main()