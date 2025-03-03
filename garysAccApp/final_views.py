import re
import os
import gspread
import time
from django.shortcuts import render
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

def final_views(request):
    if getattr(request, "_processed_final_views", False):
        print("Skipping redundant execution.")
        return render(request, "final_views.html", {"message": "Skipped redundant execution."})

    request._processed_final_views = True
    
    try:
        print("Initializing Google Sheets API authentication...")
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
        if not creds.valid and creds.expired and creds.refresh_token:
            print("Refreshing credentials...")
            creds.refresh(Request())

        client = gspread.authorize(creds)
        worksheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
        print("Successfully authenticated and retrieved worksheet.")
        
        start_row, end_row = 3, 16
        sum_start_row, sum_end_row = 22, 37
        columns_to_sum = [10, 11, 12, 13, 14, 18]
        totals = {col: 0.0 for col in columns_to_sum}

        print("Starting summation of column values...")
        for row in range(start_row, end_row + 1):
            for col in columns_to_sum:
                try:
                    value = worksheet.cell(row, col).value
                    print(f"Reading cell ({row}, {col}): {value}")
                    if value:
                        value = float(value.replace('€', '').replace(',', ''))
                        totals[col] += value
                except Exception as e:
                    print(f"Error processing cell ({row}, {col}): {e}")
            time.sleep(4.1)  # Increased sleep time to handle API quota limits
        
        print("Updating sum calculations in row 17 and row 23...")
        for col in columns_to_sum:
            if col == 18:
                worksheet.update_cell(23, col, round(totals[col], 2))
                print(f"Updated cell (23, {col}) with sum: {round(totals[col], 2)}")
            else:
                worksheet.update_cell(17, col, round(totals[col], 2))
                print(f"Updated cell (17, {col}) with sum: {round(totals[col], 2)}")
            time.sleep(4.1)  # Added delay to prevent exceeding quota
        
        print("Calculating total sums in row 38 for columns 10 and 11 from rows 22 to 37...")
        total_sum_col10 = 0.0
        total_sum_col11 = 0.0
        
        for row in range(sum_start_row, sum_end_row + 1):
            for col, total_var in [(10, 'total_sum_col10'), (11, 'total_sum_col11')]:
                try:
                    value = worksheet.cell(row, col).value
                    print(f"Reading cell ({row}, {col}): {value}")
                    if value:
                        value = float(value.replace('€', '').replace(',', ''))
                        if col == 10:
                            total_sum_col10 += value
                        elif col == 11:
                            total_sum_col11 += value
                except Exception as e:
                    print(f"Error processing cell ({row}, {col}): {e}")
            time.sleep(4.1)
        
        worksheet.update_cell(38, 10, round(total_sum_col10, 2))
        worksheet.update_cell(38, 11, round(total_sum_col11, 2))
        print(f"Updated cell (38, 10) with sum: {round(total_sum_col10, 2)}")
        print(f"Updated cell (38, 11) with sum: {round(total_sum_col11, 2)}")
        
        print("All updates completed successfully.")
        return render(request, "final_views.html", {"message": "Successful page load"})
    
    except HttpError as e:
        print(f"Google API Error: {str(e)}")
        time.sleep(60)
        return final_views(request)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return render(request, "final_views.html", {"message": f"Unexpected Error: {str(e)}"})
