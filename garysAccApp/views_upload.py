import os
from django.shortcuts import render
import fitz  # PyMuPDF for PDF processing
import gspread  # Google Sheets API
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from django.core.files.storage import default_storage

# Google Sheets Setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file('/workspace/garysAccounts/credentials.json', scopes=SCOPE)
SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

# Check if credentials are valid, refresh if necessary
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = creds.refresh(Request())

# Authorize the credentials with gspread
client = gspread.authorize(creds)

# Open the spreadsheet by its ID
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# Get the first worksheet in the spreadsheet
worksheet = spreadsheet.get_worksheet(0)

# Ensure the temp folder exists
temp_dir = 'temp/'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

def extract_payments_from_pdf(pdf_path):
    """Extract only 'Payments In' from the bank statement PDF"""
    doc = fitz.open(pdf_path)
    payments = []

    for page_num, page in enumerate(doc):
        text = page.get_text("html")  # Try HTML extraction for structured data
        print(f"--- Page {page_num + 1} ---")
        print(text)  # Print the raw HTML content to debug

        # Parse the HTML to find payment data (you can adjust the logic based on HTML structure)
        lines = text.split("<br>")
        for line_num, line in enumerate(lines):
            print(f"Line {line_num + 1}: {line}")  # Debug each line
            
            # Try to match "Payment In" or similar phrases (case insensitive)
            if "Payment In" in line or "Deposit" in line:
                print(f"Found payment line: {line}")  # Print the matching line for debugging
                
                # Example for extracting date and amount (you may need to adjust this)
                parts = line.split()  # This could be different for HTML, adjust as necessary
                print(f"Line parts: {parts}")  # Check the parts split by space
                
                try:
                    date_str, amount = parts[0], parts[-1]
                    print(f"Extracted date: {date_str}, amount: {amount}")
                    date = datetime.strptime(date_str, "%d/%m/%Y").date()
                    payments.append((date, amount))
                except Exception as e:
                    print(f"Error extracting date/amount: {e}")
    
    return payments


def find_column_for_date(date_str):
    """Find the correct column based on the start of the week date in row 2."""
    # The week start dates are assumed to be in row 2, columns starting from 10
    for col in range(10, worksheet.col_count + 1):
        cell_value = worksheet.cell(2, col).value
        if cell_value == date_str:
            return col
    return None  # If no matching date is found

def upload_bank(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]

        # Ensure the temp folder exists
        temp_dir = 'temp/'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save the uploaded file
        file_path = default_storage.save("temp/" + pdf_file.name, pdf_file)
        absolute_path = default_storage.path(file_path)
        print(f"File saved at: {absolute_path}")  # Print absolute path

        # Check if the file exists before processing
        if os.path.exists(absolute_path):
            # Extract "Payments In" from the statement
            payments = extract_payments_from_pdf(absolute_path)
            print('payments:', payments)
        else:
            print(f"File does not exist at: {absolute_path}")
            return render(request, "upload_bank.html", {"message": "Error: File not found!"})

        # Process payments and update Google Sheets
        for payment_date, amount in payments:
            # Format the date to match the format in the sheet (e.g., "DD/MM/YYYY")
            date_str = payment_date.strftime("%d/%m/%Y")
            print('date_str:', date_str)
            # Find the corresponding column in the sheet
            column_index = find_column_for_date(date_str)
            print('column_index:', column_index)
            if column_index:
                # Find the first empty row in the column
                row_index = 3  # Start at row 3 (skipping row 2 which has the dates)
                while worksheet.cell(row_index, column_index).value:
                    row_index += 1  # Move down until an empty cell is found
                
                # Place the payment amount in the first empty row of the correct column
                worksheet.update_cell(row_index, column_index, str(amount))
            else:
                print(f"Could not find matching column for date {date_str}")

        return render(request, "upload_bank.html", {"message": "Payments updated successfully!"})

    return render(request, "upload_bank.html")
