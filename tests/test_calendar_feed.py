"""Google Calendar public iCalendar feed: Indonesian public holidays (keyless, RFC 5545)."""

import re
from datetime import date

import pytest

pytestmark = pytest.mark.category("Calendar feed (iCal)")
FEED = "https://calendar.google.com/calendar/ical/en.indonesian%23holiday%40group.v.calendar.google.com/public/basic.ics"


@pytest.fixture(scope="module")
def calendar(http):
    response = http.get(FEED, timeout=20)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    # RFC 5545 line folding: continuation lines start with a space
    text = response.text.replace("\r\n ", "")
    events = [
        {key: value for key, value in re.findall(r"^([A-Z-]+)(?:;[^:]*)?:(.*)$", block, re.M)}
        for block in text.split("BEGIN:VEVENT")[1:]
    ]
    return text, events


@pytest.mark.severity("high")
def test_feed_is_valid_icalendar(calendar):
    """The feed is a VCALENDAR with version 2.0 and at least one event"""
    text, events = calendar
    assert text.startswith("BEGIN:VCALENDAR") and "VERSION:2.0" in text and text.rstrip().endswith("END:VCALENDAR")
    assert len(events) > 20


@pytest.mark.severity("high")
def test_every_event_has_the_required_properties(calendar):
    """Every event has a UID, a start date and a summary"""
    for event in calendar[1]:
        assert {"UID", "DTSTART", "SUMMARY"} <= set(event)


@pytest.mark.severity("medium")
def test_event_uids_are_unique(calendar):
    """No two events share a UID (duplicates break calendar sync)"""
    uids = [e["UID"] for e in calendar[1]]
    assert len(uids) == len(set(uids))


@pytest.mark.severity("high")
def test_independence_day_is_always_17_august(calendar):
    """Indonesian Independence Day falls on 17 August in every year listed"""
    dates = [e["DTSTART"][:8] for e in calendar[1] if e["SUMMARY"].strip() == "Indonesian Independence Day"]
    assert dates and all(d.endswith("0817") for d in dates)


@pytest.mark.severity("medium")
def test_current_year_is_covered(calendar):
    """The feed lists holidays for the current year"""
    years = {e["DTSTART"][:4] for e in calendar[1]}
    assert str(date.today().year) in years


@pytest.mark.severity("low")
def test_dates_are_valid(calendar):
    """Every start date is a real calendar date"""
    for event in calendar[1]:
        raw = event["DTSTART"][:8]
        date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
