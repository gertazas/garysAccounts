import re
import os
import gspread
import random
import time
import math
import random
from django.shortcuts import render, redirect
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = '1MrGvUcus3F8fyGlqVvWYB-udybH0qNlq5JLQY2g_gMs'

def random_number():
    rnumber = random.randint(50, 100)
    if rnumber % 5 == 0:
        print('rnumber:', rnumber)
        return rnumber
    else:
        random_number()

def final_views():
    print("Welcome to Gary Murphy's MoneyFlow Automation")
    return render(request, "final_views.html",  {"message": "Successful page load"})