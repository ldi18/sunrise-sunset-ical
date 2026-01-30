from datetime import date, datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from icalendar import Calendar, Event
import pytz

# ---- config ----
LAT = 48.13743
LON = 11.57549
TIMEZONE = "Europe/Berlin"
START_DATE = date(2026, 1, 1)
END_DATE   = date(2026, 12, 31)

# ---- location ----
tz = pytz.timezone(TIMEZONE)
location = LocationInfo(
    name="Munich",
    region="DE",
    timezone=TIMEZONE,
    latitude=LAT,
    longitude=LON,
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
with open("sunrise_sunset_munich_2026.ics", "wb") as f:
    f.write(cal.to_ical())

print("ICS file generated ✔", flush=True)
