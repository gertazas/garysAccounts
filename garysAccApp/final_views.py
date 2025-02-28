import re
import os
import gspread
import random
import time
import math
import random
from django.shortcuts import render, redirect
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

def random_number():
    rnumber = random.randint(50, 100)
    if rnumber % 5 == 0:
        print('rnumber:', rnumber)
        return rnumber
    else:
        random_number()

def final_views(request):
    print("Welcome to Gary Murphy's MoneyFlow Automation")
    
    # Load credentials from credentials.json
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)

    # Check if credentials are valid, refresh if necessary
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = creds.refresh(Request())

    try:
        # Authorize the credentials with gspread
        client = gspread.authorize(creds)

        # Open the spreadsheet by its ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)

        # Get the first worksheet in the spreadsheet
        worksheet = spreadsheet.get_worksheet(0)
        # Retrieve values from the worksheet
        values = worksheet.get_all_values()

        # Number of read requests you are making
        total_read_requests = 6  # 6 read requests: 4 columns (10, 11, 12, 13) + 1 for the first API call + 1 for the last API call

        # Duration over which you want to spread the requests (in seconds)
        desired_duration_seconds = 60

        # Minimum sleep duration to stay within rate limits
        min_sleep_duration = desired_duration_seconds / total_read_requests

        # Define the range of rows to sum
        start_row = 3
        end_row = 16
        wages_and_receipts_start_row = 22
        wages_and_receipts_end_row = 37

        # Initialize the total sums for columns 10, 11, 12, and 13 as floats
        total_sum_col10 = 0.0
        total_sum_col11 = 0.0
        total_sum_col12 = 0.0
        total_sum_col13 = 0.0
        total_sum_col18 = 0.0
        total_sum_wages = 0.0
        total_sum_receipts = 0.0

        # Iterate through the rows and calculate the sums for columns 10, 11, 12, and 13
        for row_num in range(start_row, end_row + 1):
            # Column 10
            print(f'Loading info column 10...')
            cell_value_col10 = worksheet.cell(row_num, 10).value
            if cell_value_col10 is not None:
                cell_value_col10 = cell_value_col10.replace('€', '').replace(',', '')
                try:
                    cell_value_col10 = float(cell_value_col10)
                    total_sum_col10 += cell_value_col10
                except ValueError:
                    pass
            time.sleep(4.1)
            # Column 11
            cell_value_col11 = worksheet.cell(row_num, 11).value
            if cell_value_col11 is not None:
                cell_value_col11 = cell_value_col11.replace('€', '').replace(',', '')
                try:
                    cell_value_col11 = float(cell_value_col11)
                    total_sum_col11 += cell_value_col11
                except ValueError:
                    pass

            # Column 12
            cell_value_col12 = worksheet.cell(row_num, 12).value
            if cell_value_col12 is not None:
                cell_value_col12 = cell_value_col12.replace('€', '').replace(',', '')
                try:
                    cell_value_col12 = float(cell_value_col12)
                    total_sum_col12 += cell_value_col12
                except ValueError:
                    pass
            time.sleep(4.1)
            # Column 13
            cell_value_col13 = worksheet.cell(row_num, 13).value
            if cell_value_col13 is not None:
                cell_value_col13 = cell_value_col13.replace('€', '').replace(',', '')
                try:
                    cell_value_col13 = float(cell_value_col13)
                    total_sum_col13 += cell_value_col13
                except ValueError:
                    pass
        print('10', total_sum_col10)
        print('11', total_sum_col12)
        print('12', total_sum_col11)
        print('13', total_sum_col13)
        
        print('wages', total_sum_wages)
        print('receipts', total_sum_receipts)

        print(f'Loading info column 18...')
        time.sleep(60.1)
        for row_num_18  in range(3, 23):
            # Column 18
            cell_value_col18 = worksheet.cell(row_num_18, 18).value
            if cell_value_col18 is not None:
                cell_value_col18 = cell_value_col18.replace('€', '').replace(',', '')
                try:
                    cell_value_col18 = float(cell_value_col18)
                    total_sum_col18 += cell_value_col18
                    print('18', total_sum_col18)
                except ValueError:
                    pass
            
        return render(request, "final_views.html", {"message": "Successful page load"})
    
    except Exception as e:
        return render(request, "final_views.html", {"message": f"Error: {str(e)}"})
final_views(Request)