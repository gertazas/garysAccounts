import re
import os
import gspread
import time
import math
import random
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
        
        # Define row ranges
        row_range_1 = range(3, 17)  # Rows 3-16
        row_range_2 = range(22, 38) # Rows 22-37
        row_range_3 = range(3, 23) # Rows 3-23only for 18 col
        columns_to_sum = [10, 11, 12, 13, 14]
        
        # Initialize totals
        totals_rows_3_16 = {col: 0.0 for col in columns_to_sum}
        totals_rows_22_37 = {col: 0.0 for col in columns_to_sum}

        print("Fetching all sheet values at once to optimize performance...")
        data = worksheet.get_all_values()

        # Sum values for rows 3-16
        for row in row_range_1:
            for col in columns_to_sum:
                try:
                    value = data[row - 1][col - 1]  
                    if value:
                        value = float(str(value).replace('€', '').replace(',', ''))
                        totals_rows_3_16[col] += value
                except Exception as e:
                    print(f"Error processing cell ({row}, {col}): {e}")

        # Sum values for rows 22-37
        for row in row_range_2:
            for col in columns_to_sum:
                try:
                    value = data[row - 1][col - 1]
                    if value:
                        value = float(str(value).replace('€', '').replace(',', ''))
                        totals_rows_22_37[col] += value
                except Exception as e:
                    print(f"Error processing cell ({row}, {col}): {e}")

        print("Updating calculated sums to the worksheet...")
        
        # Write sums from rows 3-16 into row 17
        for col in columns_to_sum:
            worksheet.update_cell(17, col, round(totals_rows_3_16[col], 2))  # Fixing float precision
            print(f"Updated cell (17, {col}) with sum: {round(totals_rows_3_16[col], 2)}")
            time.sleep(4.1)  

        total_sum_18 = 0.0
        for row in row_range_3:
            try:
                value = data[row - 1][17]  # Column 18 (zero-based index is 17)
                if value:
                    value = float(str(value).replace('€', '').replace(',', ''))
                    total_sum_18 += value
            except Exception as e:
                print(f"Error processing cell ({row}, 18): {e}")

        # Update cell (23, 18) with the total sum
        worksheet.update_cell(23, 18, round(total_sum_18, 2))
        print(f"Updated cell (23, 18) with total sum: {round(total_sum_18, 2)}")

        # Wait for sheet updates before calculations
        print("Still loading more info...")
        time.sleep(61.0)

        # SUM COLUMN 17, ROWS 17-19, THEN UPDATE ROW 20, COLUMN 17
        total_sum_17 = 0.0
        rows_to_sum = [17, 18, 19]  # Rows to sum in Column 17

        for row in rows_to_sum:
            value = worksheet.cell(row, 17).value
            if value:
                try:
                    value = value.replace("€", "").replace(",", "").strip()
                    total_sum_17 += float(value)
                except ValueError:
                    print(f"Skipping invalid value in ({row}, 17): {value}")

        # Update row 20, column 17 with the total sum
        worksheet.update_cell(20, 17, round(total_sum_17, 2))
        print(f"Updated cell (20, 17) with sum: {round(total_sum_17, 2)}")

        # SUM COLUMN 10 (Wages) AND COLUMN 11 (Receipts) IN ROW 38, THEN UPDATE ROWS 18, 19 IN COLUMN 17
        totals_rows_22_37 = {}

        for col in range(10, 12):  # Columns 10 (Wages) and 11 (Receipts)
            total = 0.0
            for row in range(22, 38):  # Rows 22-37
                value = worksheet.cell(row, col).value
                if value:
                    try:
                        value = value.replace("€", "").replace(",", "").strip()
                        total += float(value)
                    except ValueError:
                        print(f"Skipping invalid value in ({row}, {col}): {value}")

            totals_rows_22_37[col] = total
            worksheet.update_cell(38, col, round(total, 2))  # Update Row 38 (Totals for Wages/Receipts)

        # Update wages (Column 10) in Row 18, Column 17
        worksheet.update_cell(18, 17, round(totals_rows_22_37[10], 2))
        # Update receipts (Column 11) in Row 19, Column 17
        worksheet.update_cell(19, 17, round(totals_rows_22_37[11], 2))

        print(f"Updated wages (18,17) with: {round(totals_rows_22_37[10], 2)}")
        print(f"Updated receipts (19,17) with: {round(totals_rows_22_37[11], 2)}")

        

        # Load and process row 23, column 18 value
        amount_row_14_col_R = worksheet.cell(23, 18).value
        amount_row_14_col_R = float(amount_row_14_col_R.replace('€', '').replace(',', ''))

        def get_random_number_70():
            return random.randint(0, 70)

        def get_random_number_50():
            return random.randint(0, 50)

        # Calculate financial breakdown
        saturday = round(amount_row_14_col_R * 0.45 + get_random_number_70(), 2)
        friday = round(amount_row_14_col_R * 0.33 + get_random_number_50(), 2)
        sunday = round(amount_row_14_col_R - saturday - friday, 2)
        time.sleep(4.1)
        worksheet.update_cell(17, 14, friday)
        worksheet.update_cell(17, 15, saturday)
        worksheet.update_cell(17, 16, sunday)

        print("Saturday:", saturday)
        print("Friday:", friday)
        print("Sunday:", sunday)
        time.sleep(4.1)
        # Sum up week statements
        week_statements_sum = 0
        for col in range(10, 18):  # Columns 10-17
            cell_value = worksheet.cell(17, col).value
            if cell_value:
                week_statements_sum += float(cell_value.replace('€', '').replace(',', ''))

        # # Process wages & receipts
        # wages = float(worksheet.cell(18, 17).value.replace('€', '').replace(',', ''))
        # receipts = float(worksheet.cell(19, 17).value.replace('€', '').replace(',', ''))
        # week_statements_sum = round(float(week_statements_sum), 2)  # Ensure rounding

        # total = round(wages + receipts + week_statements_sum, 2)

        # # Rounding calculations
        # roundtotal = math.ceil(total)
        # moneydiff = roundtotal - total
        # moneydown = round(moneydiff + random.uniform(5, 15), 2)

        # cashtotal = round(total + moneydown, 2)
        # cashdown = round(cashtotal - total, 2)

        # # Update sheet with calculations
        # worksheet.update_cell(20, 17, roundtotal) 
        worksheet.update_cell(17, 17, week_statements_sum)  # Now correctly rounded

        # # Ensure 'Cash Load' is correctly updated in Column 2
        # for row in range(1, worksheet.row_count + 1):
        #     label = worksheet.cell(row, 1).value
        #     if label == "Cash Load":
        #         worksheet.update_cell(row, 2, roundtotal)
        #         print(f"Updated 'Cash Load' in Column 2 (Row {row}) to: {roundtotal}")

        # # Fix 'Weeks Total' if necessary
        # for row in range(1, worksheet.row_count + 1):
        #     label = worksheet.cell(row, 1).value
        #     if label == "Weeks Total":
        #         week_total_col2 = worksheet.cell(row, 2).value
        #         if week_total_col2:
        #             try:
        #                 week_total_col2 = float(str(week_total_col2).replace("€", "").replace(",", ""))
        #                 if roundtotal != week_total_col2:
        #                     worksheet.update_cell(row, 2, roundtotal)
        #                     print(f"Updated 'Weeks Total' in Column 2 (Row {row}) to: {roundtotal}")
        #             except ValueError:
        #                 print(f"Skipping invalid value in (Row {row}, Column 2): {week_total_col2}")

        # UPDATE COLUMN 2 AFTER "CASH LOAD" WITH TOTAL FROM (20, 17)
        # Ensure moneydown is calculated before use
        wages = float(worksheet.cell(18, 17).value.replace("€", "").replace(",", ""))
        receipts = float(worksheet.cell(19, 17).value.replace("€", "").replace(",", ""))
        week_statements_sum = float(worksheet.cell(17, 17).value.replace("€", "").replace(",", ""))

        total_value = wages + receipts + week_statements_sum
 
        # Update sheet
        worksheet.update_cell(20, 17, total_value)

        print(f"Updated cell (20, 17) with precise sum: {total_value}")
# /////////////////////////////////////////////////////////////////////////////////////////////
        time.sleep(60)
        moneydiff = total_value - total_value
        moneydown = round(moneydiff + random.uniform(5, 15), 2)  # Ensure moneydown is defined
        cashtotal = round(total_value + moneydown, 2)
        cashdown = round(cashtotal - total_value, 2)

        # Find 'Cash Load' row
        cash_load_row = None
        for row in range(1, worksheet.row_count + 1):
            if worksheet.cell(row, 1).value == "Cash Load":
                cash_load_row = row
                break

        if cash_load_row:
            try:
                worksheet.update_cell(cash_load_row - 1, 2, cashtotal)  # Above 'Cash Load'
                worksheet.update_cell(cash_load_row, 2, total_value)  # 'Cash Load' row
                worksheet.update_cell(cash_load_row + 1, 2, cashdown)  # Below 'Cash Load'

                print(f"Updated column 2 above 'Cash Load' (Row {cash_load_row - 1}) with: {cashtotal}")
                print(f"Updated column 2 after 'Cash Load' (Row {cash_load_row}) with: {total_value}")
                print(f"Updated column 2 below 'Cash Load' (Row {cash_load_row + 1}) with: {cashdown}")

            except ValueError:
                print(f"Skipping invalid total value at (20, 17): {total_value}")
        else:
            print("Could not find 'Cash Load' in column 1.")

        return render(request, "final_views.html", {"message": "Successful page load"})
    
    except HttpError as e:
        print(f"Google API Error: {str(e)}")
        time.sleep(60)
        return final_views(request)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return render(request, "final_views.html", {"message": f"Unexpected Error: {str(e)}"})
