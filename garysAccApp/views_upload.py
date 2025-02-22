import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from django.shortcuts import render, redirect
import pandas as pd
from django.shortcuts import render
from django.core.files.storage import default_storage
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



def upload_bank(request):
    if request.method == "POST" and request.FILES.get("bank_statement"):
        # Save uploaded file
        uploaded_file = request.FILES["bank_statement"]
        file_path = f"media/uploads/{uploaded_file.name}"
    
        with default_storage.open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        print(f"File saved at: {file_path}")

        # Extract payments & dates
        extracted_payments = extract_payments(file_path)

        # Save payments in the correct Excel format
        save_to_spreadsheet(extracted_payments, file_path)

        return render(request, "upload_bank.html", {"message": "Processing complete!"})

    return render(request, "upload_bank.html")


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

# Google Sheets Setup (re-use authentication from views.py)
creds = ServiceAccountCredentials.from_json_keyfile_name("/workspace/garysAccounts/credentials.json", SCOPE)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
# Get the first worksheet in the spreadsheet
worksheet = spreadsheet.get_worksheet(0)

# Open Google Sheet
SHEET_NAME = "Gary_Murphy"  # Change this to your sheet's name
sheet = client.open(SHEET_NAME).sheet1  

# Define PDF directory
pdf_folder = "/workspace/garysAccounts/media/uploads"

# Find the latest uploaded PDF
pdf_files = sorted(
    [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")],
    key=lambda f: os.path.getctime(os.path.join(pdf_folder, f)),
    reverse=True
)

if not pdf_files:
    print("No PDF files found.")
else:
    pdf_file = os.path.join(pdf_folder, pdf_files[0])  
    print(f"Processing PDF: {pdf_file}")  

    extracted_payments = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table[1:]:  # Skip header row
                    date_str = row[0].strip()
                    payments_in = row[3].strip() if row[3] else "0"

                    try:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                        extracted_payments.append((date_obj, payments_in))
                    except ValueError:
                        print(f"Skipping invalid date: {date_str}")

    # Load existing Google Sheets data
    dates_row = sheet.row_values(2)  # Read the row with date headers
    dates_dict = {datetime.strptime(d, "%d/%m/%Y").date(): idx for idx, d in enumerate(dates_row, start=10)}

    # Insert payments into the correct column
    for date, payment in extracted_payments:
        if date in dates_dict:
            col_index = dates_dict[date] + 1  # Convert to 1-based index for Google Sheets
            sheet.update_cell(3, col_index, payment)  # Insert payment in row 3 under correct date

    print("Payments successfully updated in Google Sheets!")
