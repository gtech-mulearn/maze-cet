import json
import os

import gspread
from gspread import SpreadsheetNotFound


def get_questions(learning_station):
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))

        filename = os.path.join(current_directory, "google_api_support_file.json")

        with open(filename, "r", encoding="utf-8") as json_file:
            credentials = json.load(json_file)
            service_account = gspread.service_account_from_dict(credentials)

        google_sheet = service_account.open("iedc")
        work_sheet = google_sheet.worksheet("python")
        work_sheet_data = work_sheet.get_all_records()

        response_list = []

        for data in work_sheet_data:
            response_dict = {
                'question': data['Question'],
                'answer': data['Answer'],
                'options': {
                    'a': data['A'],
                    'b': data['B'],
                    'c': data['C'],
                    'd': data['D']
                }
            }

            response_list.append(response_dict)

        return response_list

    except FileNotFoundError:
        return "Error: The 'google_api_support_file.json' file was not found."
    except SpreadsheetNotFound:
        return "Error: The Google Sheet 'iedc' was not found."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
