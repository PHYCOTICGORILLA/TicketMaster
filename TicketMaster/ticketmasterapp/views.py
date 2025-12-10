from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FavoriteEvent
import requests

def index(request):
    events = []

    if request.method == "POST":
        genre = request.POST.get("genre", "")
        city = request.POST.get("city", "")

        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": "sH4uVtw5apXFBbAE1bNKm9jyT9GqI0Nm",
            "classificationName": genre,
            "city": city
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if "_embedded" in data and "events" in data["_embedded"]:
                for item in data["_embedded"]["events"]:
                    image = item["images"][0]["url"] if item.get("images") else ""
                    name = item.get("name", "Unknown Event")

                    dates = item.get("dates", {})
                    date = dates.get("start", {}).get("localDate", "N/A")
                    time = dates.get("start", {}).get("localTime", "N/A")

                    venue_info = item["_embedded"]["venues"][0] if "_embedded" in item else {}
                    venue = venue_info.get("name", "Unknown Venue")
                    address = venue_info.get("address", {}).get("line1", "Unknown Address")

                    ticket_url = item.get("url", "#")

                    events.append({
                        "name": name,
                        "image": image,
                        "date": date,
                        "time": time,
                        "venue": venue,
                        "address": address,
                        "ticket_url": ticket_url,
                    })
            else:
                messages.info(request, "No events found. Try another search.")
        else:
            messages.error(request, "Error fetching data from Ticketmaster.")

    return render(request, "ticketmaster.html", {"events": events})

def add_favorite(request):
    if request.method == "POST":
        FavoriteEvent.objects.create(
            name=request.POST["name"],
            image=request.POST["image"],
            date=request.POST["date"],
            time=request.POST["time"],
            venue=request.POST["venue"],
            address=request.POST["address"],
            ticket_url=request.POST["ticket_url"],
        )
        messages.success(request, "Added to favorites!")
        return redirect("home")

def favorite_list(request):
    favorites = FavoriteEvent.objects.all().order_by("-created_at")
    return render(request, "favorites.html", {"favorites": favorites})

def delete_favorite(request, id):
    fav = get_object_or_404(FavoriteEvent, id=id)
    fav.delete()
    return redirect("favorite_list")

def update_favorite(request, id):
    fav = get_object_or_404(FavoriteEvent, id=id)

    if request.method == "POST":
        fav.name = request.POST["name"]
        fav.date = request.POST["date"]
        fav.time = request.POST["time"]
        fav.venue = request.POST["venue"]
        fav.address = request.POST["address"]
        fav.ticket_url = request.POST["ticket_url"]
        fav.save()

        return redirect("favorite_list")

    return render(request, "update_favorite.html", {"fav": fav})
