from django.shortcuts import render, redirect
from django.contrib import messages
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time

# Google Sheets Setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

# Authorize Google Sheets
creds = Credentials.from_service_account_file(
    "/workspace/garysAccounts/credentials.json", scopes=SCOPE
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # First sheet
sheet.format("B:B", {"backgroundColor": {"red": 0.9, "green": 1, "blue": 0.9}})

def views_sheetprint(request):
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

        # Reset column B (trailers) to white only up to the last "Days Total" row (before Weeks Total)
        sheet.format(f"B:B", {"backgroundColor": {"red": 1, "green": 1, "blue": 1}})  # White

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

        messages.success(request, "Google Sheet updated successfully!")
        return redirect("upload_bank")

    return render(request, "views_sheetprint.html", {"trailer_counts": request.session.get("trailer_counts", {})})
