from datetime import date, datetime, timedelta
import json
from astral import LocationInfo
from astral.sun import sun
from icalendar import Calendar, Event
import pytz

# ---- config ----
with open("locations.json", "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)

LOCATION_KEY = "MUNICH"
START_DATE = date(2026, 1, 1)
END_DATE   = date(2026, 12, 31)

# ---- location ----
location_config = LOCATIONS[LOCATION_KEY]
lat = location_config["LAT"]
lon = location_config["LON"]
timezone = location_config["TIMEZONE"]
region = location_config["REGION"]
location_name = LOCATION_KEY.title()

tz = pytz.timezone(timezone)
location = LocationInfo(
    name=location_name,
    region=region,
    timezone=timezone,
    latitude=lat,
    longitude=lon,
)

# ---- calendar ----
cal = Calendar()
cal.add("prodid", "-//Sunrise Sunset Calendar//")
cal.add("version", "2.0")

current = START_DATE
while current <= END_DATE:
    s = sun(location.observer, date=current, tzinfo=tz)

    # Sunrise
    sunrise = Event()
    sunrise.add("summary", "🌅 Sunrise")
    sunrise.add("dtstart", s["sunrise"])
    sunrise.add("dtend", s["sunrise"] + timedelta(minutes=1))
    sunrise.add("dtstamp", datetime.now(tz))
    cal.add_component(sunrise)

    # Sunset
    sunset = Event()
    sunset.add("summary", "🌇 Sunset")
    sunset.add("dtstart", s["sunset"])
    sunset.add("dtend", s["sunset"] + timedelta(minutes=1))
    sunset.add("dtstamp", datetime.now(tz))
    cal.add_component(sunset)

    current += timedelta(days=1)

# ---- write file ----
with open("sunrise_sunset.ics", "wb") as f:
    f.write(cal.to_ical())

print("ICS file generated ✔", flush=True)
