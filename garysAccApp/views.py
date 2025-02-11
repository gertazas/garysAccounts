from django.shortcuts import render, redirect
from .models import TrailerSelection, WorkDay

# Step 1: Ask for the number of trailers per day
def trailer_step1(request):
    workdays = WorkDay.objects.all()  # Get all available workdays

    if request.method == "POST":
        trailer_counts = {day.day: int(request.POST.get(f"trailers_{day.day}", 0)) for day in workdays}
        request.session["trailer_counts"] = trailer_counts  # Store trailer count in session
        return redirect("trailer_step2")  # Move to step 2

    return render(request, "trailer_step1.html", {"workdays": workdays})


# Step 2: Collect Coffee & Milkshake Data for Each Trailer
def trailer_step2(request):
    trailer_counts = request.session.get("trailer_counts", {})  # Get stored trailer data

    if not trailer_counts:
        return redirect("trailer_step1")  # Go back if no data

    if request.method == "POST":
        coffee_data = {}
        milkshake_data = {}

        for day_code, count in trailer_counts.items():
            coffee_data[day_code] = []
            milkshake_data[day_code] = []

            for i in range(1, count + 1):  # Generate inputs for each trailer
                coffee = request.POST.get(f"coffee_{day_code}_{i}", "0")
                milkshake = request.POST.get(f"milkshake_{day_code}_{i}", "0")
                coffee_data[day_code].append(float(coffee))
                milkshake_data[day_code].append(float(milkshake))

        request.session["coffee_data"] = coffee_data
        request.session["milkshake_data"] = milkshake_data
        return redirect("trailer_summary")  # Move to summary

    return render(request, "trailer_step2.html", {
        "trailer_counts": trailer_counts  # Send trailer data to the template
    })



# Step 3: Show Summary & Totals
def trailer_summary(request):
    coffee_data = request.session.get("coffee_data", {})
    milkshake_data = request.session.get("milkshake_data", {})

    total_coffee = sum(sum(values) for values in coffee_data.values())
    total_milkshake = sum(sum(values) for values in milkshake_data.values())

    return render(request, "trailer_summary.html", {
        "coffee_data": coffee_data,
        "milkshake_data": milkshake_data,
        "total_coffee": total_coffee,
        "total_milkshake": total_milkshake
    })

# Main Trailer Selection
def trailer_selection(request):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Step 1: Ask for the number of trailers
    if "trailer_counts" not in request.session:
        step = 1  # First step
        if request.method == "POST":
            trailer_counts = {day: int(request.POST.get(f"trailers_{day}", 0)) for day in days}
            request.session["trailer_counts"] = trailer_counts  # Store in session
            return redirect("trailer_selection")  # Refresh for Step 2
    
    # Step 2: Enter Coffee & Milkshake % for Each Trailer
    else:
        step = 2
        trailer_counts = request.session["trailer_counts"]
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
            return redirect("trailer_summary")  # Move to summary step

    return render(request, "trailer_selection.html", {
        "days": days,
        "trailer_counts": request.session.get("trailer_counts", {}),
        "step": step
    })
