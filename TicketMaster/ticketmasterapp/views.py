import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FavoriteEvent
import requests

def get_ticketmaster_events(city, genre):
    try:
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": "sH4uVtw5apXFBbAE1bNKm9jyT9GqI0Nm",
            "city": city,
            "classificationName": genre,
            "sort": "date,asc",
            "size": 20
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None

def index(request):
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        genre = request.POST.get('genre', '').strip()

        if not city and not genre:
            messages.info(request, "Please enter both a city and a genre before searching.")
            return redirect('home')

        if not city:
            messages.info(request, "Please enter a city.")
            return redirect('home')

        if not genre:
            messages.info(request, "Please enter a genre.")
            return redirect('home')

        events_data = get_ticketmaster_events(city, genre)

        if events_data is None:
            messages.info(request, 'The server encountered an issue while fetching data. Please try again later.')
            return redirect('home')

        events = events_data.get('_embedded', {}).get('events', [])

        if not events:
            messages.info(request, f'No events found for "{genre}" in "{city}".')
            return redirect('home')

        event_list = []

        for event in events:
            event_name = event.get('name', 'Unknown Event')
            event_img = (event.get('images') or [{}])[0].get('url', '')
            local_date = event.get('dates', {}).get('start', {}).get('localDate')

            if local_date:
                try:
                    date_obj = datetime.datetime.strptime(local_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%a %b %d %Y")
                except:
                    formatted_date = "Date not available"
            else:
                formatted_date = "Date not available"

            local_time = event.get('dates', {}).get('start', {}).get('localTime')
            if local_time:
                try:
                    h, m, s = local_time.split(":")
                    dt = datetime.datetime.now().replace(hour=int(h), minute=int(m), second=0)
                    formatted_time = dt.strftime("%I:%M %p")
                except:
                    formatted_time = "Time not available"
            else:
                formatted_time = "Time not available"

            venue = event.get('_embedded', {}).get('venues', [{}])[0]
            venue_name = venue.get('name', 'Unknown Venue')
            venue_address = venue.get('address', {}).get('line1', 'Address not available')
            venue_city = venue.get('city', {}).get('name', 'Unknown City')
            venue_state = venue.get('state', {}).get('stateCode', 'Unknown State')

            ticket_url = event.get('url', '#')

            event_list.append({
                'name': event_name,
                'image': event_img,
                'date': formatted_date,
                'time': formatted_time,
                'venue': venue_name,
                'address': f"{venue_address}, {venue_city}, {venue_state}",
                'ticket_url': ticket_url
            })

        return render(request, 'ticketmaster.html', {'events': event_list})

    return render(request, 'ticketmaster.html')

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
