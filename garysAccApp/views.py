from django.shortcuts import render, redirect
from .models import TrailerSelection, WorkDay
from django.db import transaction
from django.contrib import messages
from django.utils.safestring import mark_safe
import time
import fitz  # PyMuPDF for PDF processing
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings


# Step 1: Select number of trailers
def trailer_selection(request):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Step 1: Ask for the number of trailers
    if request.method == "POST":
        trailer_counts = {day: int(request.POST.get(f"trailers_{day}", 0)) for day in days}
        request.session["trailer_counts"] = trailer_counts  # Store in session
        request.session.modified = True
        return redirect("trailer_step2")  # Refresh for Step 2

    return render(request, "trailer_selection.html", {
        "days": days,
        "trailer_counts": request.session.get("trailer_counts", {}),
    })


# Step 2: Enter Coffee & Milkshake Percentages
def trailer_step2(request):
    trailer_counts = request.session.get("trailer_counts", {})

    if "reset" in request.GET:
        request.session.flush()  # Clears ALL session data
        return redirect("trailer_selection")  # Redirect to Step 1

    if not trailer_counts:
        message = mark_safe("<script>setTimeout(() => { window.location.href='/trailer-selection/'; }, 3000);</script>")
        return render(request, "trailer_step2.html", {
            "trailer_counts": {},
            "step_completed": False,
            "message": message  # Pass JavaScript redirect
        })

    if request.method == "POST":
        coffee_data = {}
        milkshake_data = {}

        for day, count in trailer_counts.items():
            coffee_data[day] = []
            milkshake_data[day] = []
            
            for i in range(1, count + 1):
                coffee = request.POST.get(f"coffee_{day}_{i}", "0")
                milkshake = request.POST.get(f"milkshake_{day}_{i}", "0")
                coffee_data[day].append(float(coffee))
                milkshake_data[day].append(float(milkshake))

        request.session["coffee_data"] = coffee_data
        request.session["milkshake_data"] = milkshake_data
        return redirect("trailer_summary")

    return render(request, "trailer_step2.html", {
        "trailer_counts": trailer_counts,
        "step_completed": True,
        "message": ""
    })

def trailer_summary(request):
    workdays = WorkDay.objects.all()

    # Retrieve session data
    trailer_counts = request.session.get("trailer_counts", {})
    coffee_data = request.session.get("coffee_data", {})
    milkshake_data = request.session.get("milkshake_data", {})

    if "reset" in request.GET:
        request.session.pop("trailer_counts", None)
        request.session.pop("coffee_data", None)
        request.session.pop("milkshake_data", None)
        request.session.modified = True  # Ensure session updates
        return redirect("trailer_selection")  # Redirect back to Step 1


    if request.method == "POST":
        try:
            with transaction.atomic():
                for workday in workdays:
                    coffee = request.POST.get(f"coffee_{workday.day}", 0)
                    milkshake = request.POST.get(f"milkshake_{workday.day}", 0)
                    trailers_count = request.POST.get(f"trailers_{workday.day}", 0)
                    trailers_with_coffee = request.POST.get(f"trailers_coffee_{workday.day}", 0)

                    # Ensure fetched values are valid before saving
                    trailer_selection, created = TrailerSelection.objects.get_or_create(day=workday)
                    trailer_selection.coffee_percentage = float(coffee)
                    trailer_selection.milkshake_percentage = float(milkshake)
                    trailer_selection.trailers_count = int(trailers_count)
                    trailer_selection.trailers_with_coffee = int(trailers_with_coffee)
                    trailer_selection.save()

            messages.success(request, "Data saved successfully!")

            return render(request, "upload_bank.html", {
                "trailer_counts": trailer_counts,
                "coffee_data": coffee_data,
                "milkshake_data": milkshake_data
            })  
        except Exception as e:
            messages.error(request, f"Error saving data: {e}")

    return render(request, "trailer_summary.html", {
        "workdays": workdays,
        "trailer_counts": trailer_counts, 
        "coffee_data": coffee_data, 
        "milkshake_data": milkshake_data
    })


def upload_bank(request):
    extracted_text = ""
    
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "uploads"))
        filename = fs.save(pdf_file.name, pdf_file)
        file_path = fs.path(filename)

        # Extract text from PDF
        with fitz.open(file_path) as doc:
            extracted_text = "\n".join([page.get_text() for page in doc])

        # (Optional) Process extracted text here before sending to Google Sheets

    return render(request, "upload_bank.html", {"extracted_text": extracted_text})