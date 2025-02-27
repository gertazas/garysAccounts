from django.shortcuts import render, redirect
from django.contrib import messages
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from .views_upload import upload_bank



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

def views_sheetprint(request):
    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        if not start_date_str or not end_date_str:
            messages.error(request, "Both dates must be selected.")
            return redirect("views_sheetprint")

        # Convert to datetime objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Validate Monday - Sunday range
        if start_date.weekday() != 0 or end_date.weekday() != 6:
            messages.error(request, "Invalid date range. It must be a Monday-Sunday week.")
            return redirect("views_sheetprint")

        # ✅ Step 1: Write the date range to Cell (1,1) without extra spaces
        sheet.update_cell(1, 1, f"{start_date.strftime('%d %b %Y')}-{end_date.strftime('%d %b %Y')}")

        # ✅ Step 2: Write each date separately to row 2 (Tuesday-Sunday)
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

        # ✅ Step 3: Write next Monday’s date to row 2, column 18
        next_monday = end_date + timedelta(days=1)
        sheet.update_cell(2, 18, next_monday.strftime("%Y-%m-%d"))

        messages.success(request, "Google Sheet updated successfully!")
        return redirect("upload_bank")

    return render(request, "views_sheetprint.html")
