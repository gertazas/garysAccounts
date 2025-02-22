import os
import re
import pdfplumber
import gspread
from datetime import datetime
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from google.oauth2.service_account import Credentials
from django.shortcuts import render
from django.conf import settings


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
        os.makedirs(upload_dir, exist_ok=True)  # Ensure directory exists

        file_path = os.path.join(upload_dir, uploaded_file.name)

        with default_storage.open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        print(f"File saved at: {file_path}")

        extracted_payments = extract_payments(file_path)
        update_google_sheets(extracted_payments)

        return render(request, "upload_bank.html", {"message": "Processing complete!"})

    return render(request, "upload_bank.html")


# Function to get the latest uploaded PDF file
def get_latest_pdf():
    upload_dir = "media/uploads/"
    pdf_files = sorted(
        [f for f in os.listdir(upload_dir) if f.endswith(".pdf")],
        key=lambda f: os.path.getctime(os.path.join(upload_dir, f)),
        reverse=True
    )
    return os.path.join(upload_dir, pdf_files[0]) if pdf_files else None


# Function to parse dates correctly
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d %b %Y").date() if date_str else None
    except ValueError:
        return None


# Function to extract payments from a PDF
def extract_payments(pdf_path):
    extracted_payments = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    match = re.search(r"(\d{2} \w{3} \d{4})\s+.*?\s+([\d,]+\.\d{2})", line)
                    if match:
                        date_str = match.group(1)
                        amount_str = match.group(2).replace(",", "")
                        extracted_payments.append((date_str, float(amount_str)))

    print("Extracted Payments:", extracted_payments)
    return extracted_payments


from datetime import datetime
from collections import defaultdict

def update_google_sheets(extracted_payments):
    dates_row = sheet.row_values(2)  # Fetch header row with dates

    # Detect and clean up duplicate/non-date values
    date_counts = defaultdict(int)
    unique_dates = []
    
    for cell in dates_row:
        cell = cell.strip()  # Remove extra spaces
        try:
            parsed_date = datetime.strptime(cell, "%Y-%m-%d").date()  # Convert to date object
            date_counts[parsed_date] += 1
            unique_dates.append(cell)
        except ValueError:
            continue  # Skip invalid date values (e.g., '€0.00')

    # Identify duplicate dates
    duplicates = {d for d, count in date_counts.items() if count > 1}
    if duplicates:
        print(f"⚠ Warning: Duplicate dates found in Google Sheets: {duplicates}")
        return  # Stop execution to prevent errors

    # Map dates to column indexes
    dates_dict = {datetime.strptime(d, "%Y-%m-%d").date(): idx + 1 for idx, d in enumerate(unique_dates)}

    print("Parsed dates dictionary:", dates_dict)

    # Process extracted payments
    for date_str, payment in extracted_payments:
        try:
            extracted_date = datetime.strptime(date_str, "%d %b %Y").date()  # Convert extracted date
            if extracted_date in dates_dict:
                col_index = dates_dict[extracted_date]
                sheet.update_cell(3, col_index, payment)  # Update row 3 in the correct column
                print(f"✅ Updated Google Sheets: date={extracted_date}, col_index={col_index}, payment={payment}")
            else:
                print(f"⚠ Date {extracted_date} not found in Google Sheets.")
        except ValueError:
            print(f"❌ Invalid extracted date format: {date_str}")

    print("✅ Payments successfully updated in Google Sheets!")


# Main Execution for Testing
if __name__ == "__main__":
    pdf_path = get_latest_pdf()
    if pdf_path:
        extracted_payments = extract_payments(pdf_path)
        update_google_sheets(extracted_payments)
