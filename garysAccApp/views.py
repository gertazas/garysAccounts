from django.shortcuts import render, redirect
from .models import TrailerSelection, WorkDay

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
from django.utils.safestring import mark_safe
import time

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
    trailer_counts = request.session.get("trailer_counts", {})
    
    if not trailer_counts:
        return redirect("trailer_step2")  # Go back if no trailer data

    coffee_data = request.session.get("coffee_data", {})
    milkshake_data = request.session.get("milkshake_data", {})

    total_coffee = sum(sum(values) for values in coffee_data.values()) if coffee_data else 0
    total_milkshake = sum(sum(values) for values in milkshake_data.values()) if milkshake_data else 0

    return render(request, "trailer_summary.html", {
        "trailer_counts": trailer_counts,
        "coffee_data": coffee_data,
        "milkshake_data": milkshake_data,
        "total_coffee": total_coffee,
        "total_milkshake": total_milkshake
    })
