import os
import re
import pdfplumber
import gspread
from datetime import datetime
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from google.oauth2.service_account import Credentials
from django.conf import settings
from pdf2image import convert_from_path
import pytesseract
from collections import defaultdict

# Google Sheets Setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

creds = Credentials.from_service_account_file(
    "/workspace/garysAccounts/credentials.json", scopes=SCOPE
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

print("Google Sheets connection successful!")


def upload_bank(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("bank_statement")
        if not uploaded_file:
            return render(request, "upload_bank.html", {"error": "No file uploaded!"})

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, uploaded_file.name)

        with default_storage.open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        print(f"File saved at: {file_path}")

        extracted_payments = extract_payments(file_path)
        if extracted_payments:
            update_google_sheets(extracted_payments)
            return render(request, "upload_bank.html", {"message": "Processing complete!"})
        else:
            return render(request, "upload_bank.html", {"error": "No payments found!"})

    return render(request, "upload_bank.html")


# Function to extract all "Payments In" from a PDF
def extract_payments(pdf_path):
    payments_by_date = defaultdict(float)  # Store sum of payments per date

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                print(f"No text extracted from page {page.page_number}. Trying OCR...")
                text = extract_text_with_ocr(pdf_path, page.page_number)

            lines = text.split("\n")
            for line in lines:
                match = re.findall(r"(\d{2} \w{3} \d{4}).*?([\d,]+\.\d{2})\s*$", line)
                if match:
                    for date_str, amount_str in match:
                        amount = float(amount_str.replace(",", ""))
                        payments_by_date[date_str] += amount  # Add multiple payments for each date

    extracted_payments = [(date, total) for date, total in payments_by_date.items()]
    
    print("Extracted Payments:", extracted_payments)
    return extracted_payments


# OCR-based text extraction (if pdfplumber fails)
def extract_text_with_ocr(pdf_path, page_number):
    images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
    extracted_text = pytesseract.image_to_string(images[0])
    print(f"OCR Extracted Text from Page {page_number}:")
    print(extracted_text)
    return extracted_text


def update_google_sheets(extracted_payments):
    dates_row = sheet.row_values(2)  # Fetch header row with dates
    allowed_columns = [10, 11, 12, 13, 14, 18]  # Only these columns should be updated

    # Map sheet date columns to Google Sheets column indexes
    date_to_col = {}
    for idx, cell in enumerate(dates_row):
        cell = cell.strip()
        try:
            parsed_date = datetime.strptime(cell, "%Y-%m-%d").date()
            col_index = idx + 1
            if col_index in allowed_columns:
                date_to_col[parsed_date] = col_index
        except ValueError:
            continue

    print("Date to Column Mapping:", date_to_col)

    # Update Google Sheets
    for date_str, total_payment in extracted_payments:
        try:
            extracted_date = datetime.strptime(date_str, "%d %b %Y").date()
            if extracted_date in date_to_col:
                col_index = date_to_col[extracted_date]
                sheet.update_cell(3, col_index, total_payment)
                print(f"Updated Google Sheets: {extracted_date} (Column {col_index}) → €{total_payment}")
            else:
                print(f"Date {extracted_date} not found in allowed columns.")
        except ValueError:
            print(f"Invalid extracted date format: {date_str}")

    print("Payments successfully updated in Google Sheets!")


# Main Execution for Testing
if __name__ == "__main__":
    pdf_path = "/workspace/garysAccounts/media/uploads/test_statement.pdf"  # Test file
    extracted_payments = extract_payments(pdf_path)
    if extracted_payments:
        update_google_sheets(extracted_payments)
    else:
        print("No valid payments found.") 