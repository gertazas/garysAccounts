import os
import re
import pdfplumber
import gspread
from datetime import datetime
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from google.oauth2.service_account import Credentials
from django.conf import settings
from collections import defaultdict
from .final_views import final_views


# Google Sheets Setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

creds = Credentials.from_service_account_file(
    "C:/Users/greta/.vscode/garysAccounts/credentials.json", scopes=SCOPE
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

def upload_bank(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("bank_statement")
        if not uploaded_file:
            return render(request, "upload_bank.html", {"error": "No file uploaded!"})

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, uploaded_file.name)

        if os.path.exists(file_path):
            os.remove(file_path)  # Remove existing file before saving new one

        with default_storage.open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        extracted_payments = extract_payments(file_path)
        if extracted_payments:
            update_google_sheets(extracted_payments)
            return render(request, "final_views.html", {"message": "Upload successful and data processed."})
        else:
            return render(request, "upload_bank.html", {"error": "No payments found in the file."})
    
    return render(request, "upload_bank.html")

def extract_payments(pdf_path):
    extracted_payments = []
    current_date = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    date_match = re.search(r"(\d{2} \w{3} \d{4})", line)
                    if date_match:
                        current_date = date_match.group(1)
                    amount_match = re.search(r"([\d,]+\.\d{2})", line)
                    if current_date and amount_match:
                        amount_str = amount_match.group(1).replace(",", "")
                        extracted_payments.append((current_date, float(amount_str)))
    return extracted_payments

def update_google_sheets(extracted_payments):
    dates_row = sheet.row_values(2)
    date_columns = {}
    
    for index, cell in enumerate(dates_row, start=1):
        try:
            parsed_date = datetime.strptime(cell.strip(), "%d %b %Y").date()
            date_columns[parsed_date] = index
        except ValueError:
            continue

    if not date_columns:
        print("Error: No valid date columns found in Google Sheets.")
        return

    row_positions = defaultdict(int)
    for date_str, payment in extracted_payments:
        try:
            extracted_date = datetime.strptime(date_str, "%d %b %Y").date()
            if extracted_date in date_columns:
                col_index = date_columns[extracted_date]
                row_positions[col_index] += 1
                row_number = row_positions[col_index] + 2  # Ensure rows start from 3
                sheet.update_cell(row_number, col_index, payment)
            else:
                print(f"Warning: Date {extracted_date} not found in Google Sheets.")
        except ValueError:
            print(f"Invalid extracted date format: {date_str}")
    print("Payments successfully updated in Google Sheets.")