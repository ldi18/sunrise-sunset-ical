from datetime import date, datetime, timedelta
import json

import pytz
from astral import LocationInfo
from astral.sun import sun
from icalendar import Calendar, Event

SUNRISE_LABEL = "🌅 Sunrise"
SUNSET_LABEL = "🌇 Sunset"
TARGET_SUMMARIES = {SUNRISE_LABEL, SUNSET_LABEL}

# ---- config ----
INPUT_ICAL = "sunrise_sunset.ics"
# Set to None to overwrite INPUT_ICAL.
OUTPUT_ICAL = None

with open("locations.json", "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)

LOCATION_KEY = "ATHENS"

# If START_DATE is None, today's date is used.
START_DATE = None
# If END_DATE is None, the latest existing sunrise/sunset date is used.
END_DATE = None

def to_event_date(component: Event) -> date | None:
    dtstart = component.get("dtstart")
    if dtstart is None:
        return None
    dt_value = dtstart.dt
    if isinstance(dt_value, datetime):
        return dt_value.date()
    if isinstance(dt_value, date):
        return dt_value
    return None


def to_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def is_target_event(component: Event) -> bool:
    summary = to_text(component.get("summary"))
    return summary in TARGET_SUMMARIES


def latest_target_event_date(calendar: Calendar) -> date | None:
    latest: date | None = None
    for component in calendar.walk("VEVENT"):
        if not is_target_event(component):
            continue
        event_date = to_event_date(component)
        if event_date is None:
            continue
        if latest is None or event_date > latest:
            latest = event_date
    return latest


def generate_events(
    calendar: Calendar,
    location: LocationInfo,
    tz,
    start_date: date,
    end_date: date,
) -> int:
    current = start_date
    generated = 0
    while current <= end_date:
        sun_data = sun(location.observer, date=current, tzinfo=tz)

        sunrise = Event()
        sunrise.add("summary", SUNRISE_LABEL)
        sunrise.add("dtstart", sun_data["sunrise"])
        sunrise.add("dtend", sun_data["sunrise"] + timedelta(minutes=1))
        sunrise.add("dtstamp", datetime.now(tz))
        calendar.add_component(sunrise)
        generated += 1

        sunset = Event()
        sunset.add("summary", SUNSET_LABEL)
        sunset.add("dtstart", sun_data["sunset"])
        sunset.add("dtend", sun_data["sunset"] + timedelta(minutes=1))
        sunset.add("dtstamp", datetime.now(tz))
        calendar.add_component(sunset)
        generated += 1

        current += timedelta(days=1)
    return generated


def main() -> None:
    location_config = LOCATIONS[LOCATION_KEY]
    lat = location_config["LAT"]
    lon = location_config["LON"]
    timezone = location_config["TIMEZONE"]
    region = location_config["REGION"]
    location_name = LOCATION_KEY.title()

    start_date = START_DATE or date.today()

    with open(INPUT_ICAL, "rb") as file_handle:
        calendar = Calendar.from_ical(file_handle.read())

    inferred_end = latest_target_event_date(calendar)
    if END_DATE is not None:
        end_date = END_DATE
    elif inferred_end is not None:
        end_date = inferred_end
    else:
        end_date = start_date

    if end_date < start_date:
        raise ValueError("END_DATE cannot be earlier than START_DATE.")

    to_keep = []
    removed = 0
    for component in calendar.subcomponents:
        if component.name != "VEVENT" or not is_target_event(component):
            to_keep.append(component)
            continue

        event_date = to_event_date(component)
        if event_date is None or event_date < start_date:
            to_keep.append(component)
            continue

        removed += 1

    calendar.subcomponents = to_keep

    tz = pytz.timezone(timezone)
    location = LocationInfo(
        name=location_name,
        region=region,
        timezone=timezone,
        latitude=lat,
        longitude=lon,
    )

    generated = generate_events(calendar, location, tz, start_date, end_date)

    output_path = OUTPUT_ICAL or INPUT_ICAL
    with open(output_path, "wb") as file_handle:
        file_handle.write(calendar.to_ical())

    print(
        f"Updated calendar: removed {removed} future events and added {generated} "
        f"events for {location_name} ({lat}, {lon}) from {start_date} to {end_date}.",
        flush=True,
    )


if __name__ == "__main__":
    main()
