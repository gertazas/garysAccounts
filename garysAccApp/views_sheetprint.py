from django.shortcuts import render, redirect
from django.contrib import messages
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time
from googleapiclient.errors import HttpError
from django.http import JsonResponse
from .models import TrailerSelection


# Google Sheets Setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

# Authorize Google Sheets
creds = Credentials.from_service_account_file(
    "C:/Users/greta/.vscode/garysAccounts/credentials.json", scopes=SCOPE
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # First sheet

def views_sheetprint(request):
    
    try:
        trailer_counts = request.session.get("trailer_counts", {})
        coffee_data = request.session.get("coffee_data", {})
        if request.method == "POST":
            start_date_str = request.POST.get("start_date")
            end_date_str = request.POST.get("end_date")

            if not start_date_str or not end_date_str:
                messages.error(request, "Both dates must be selected.")
                return redirect("views_sheetprint")

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            if start_date.weekday() != 0 or end_date.weekday() != 6 or (end_date - start_date).days != 6:
                messages.error(request, "Invalid date range. It must be a single Monday-Sunday week.")
                return redirect("views_sheetprint")
            
            sheet.update_cell(1, 1, f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")
            time.sleep(1)
            sheet.format("A1", {"textFormat": {"bold": True}})

            # dates from start to next Monday
            # Write each date separately to row 2 (Tuesday-Sunday)
            date_cells = {
                10: start_date + timedelta(days=1),  # Tuesday
                11: start_date + timedelta(days=2),  # Wednesday
                12: start_date + timedelta(days=3),  # Thursday
                13: start_date + timedelta(days=4),  # Friday
                14: start_date + timedelta(days=5),  # Saturday
                15: start_date + timedelta(days=6),  # Sunday
            }

            for col, date in date_cells.items():
                sheet.update_cell(2, col, date.strftime("%Y-%m-%d"))

            # Write next Monday’s date to row 2, column 18
            next_monday = end_date + timedelta(days=1)
            sheet.update_cell(2, 18, next_monday.strftime("%Y-%m-%d"))

            messages.success(request, "Google Sheet updated successfully!")

            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            row = 2
            trailer_counts = request.session.get("trailer_counts", {})

            for day in weekdays:
                sheet.update_cell(row, 1, day)
                sheet.format(f"A{row}", {"textFormat": {"bold": True}})
                time.sleep(1)

                count = trailer_counts.get(day, 0)

                for i in range(count):
                    sheet.update_cell(row + i, 2, f"Trailer {i + 1}")  # Column B
                    time.sleep(1)

                days_total_row = row + max(count, 1)
                sheet.update_cell(days_total_row, 1, "Days Total")
                time.sleep(1)

                # Apply black border under Days Total (columns 1-6)
                sheet.format(f"A{days_total_row}:F{days_total_row}", {"borders": {"bottom": {"style": "SOLID_THICK"}}})

                # Apply light grey color in columns 4-6 above the black line (same row as Days Total)
                sheet.format(f"C{days_total_row}:F{days_total_row}", {"backgroundColor": {"red": 0.937, "green": 0.937, "blue": 0.937}})

                row = days_total_row + 1

            # Weeks Total in light green 3 (Google Sheets color)
            sheet.update_cell(row, 1, "Weeks Total")
            sheet.format(f"A{row}:B{row}", {"backgroundColor": {"red": 0.851, "green": 0.918, "blue": 0.827}})
            time.sleep(1)
            
            # Cash Load under Weeks Total in light green 2
            sheet.update_cell(row + 1, 1, "Cash Load")
            sheet.format(f"A{row + 1}:B{row + 1}", {"backgroundColor": {"red": 0.717, "green": 0.882, "blue": 0.804}})
            time.sleep(1)

            # Money Down under Cash Load in light green 2
            sheet.update_cell(row + 2, 1, "Money Down")
            sheet.format(f"A{row + 2}:B{row + 2}", {"backgroundColor": {"red": 0.717, "green": 0.882, "blue": 0.804}})
            time.sleep(1)

            success_message = "Google Sheet updated successfully!"
            if success_message not in existing_messages:
                messages.success(request, success_message)

            messages.success(request, {"message": success_message})
            return redirect("upload_bank", {
                                "trailer_counts": trailer_counts,
                                "coffee_data": coffee_data,
                                })

        return render(request, "views_sheetprint.html", {
                                "trailer_counts": trailer_counts,
                                "coffee_data": coffee_data,
                                })
    except HttpError as e:
        print(f"Google API Error: {str(e)}")
        time.sleep(60)
        return pviews_sheetprint(request)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return render(request, "views_sheetprint.html", {"message": f"Unexpected Error: {str(e)}"})
