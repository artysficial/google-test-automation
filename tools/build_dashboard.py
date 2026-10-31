"""Builds site/index.html from reports/results.json."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation_dashboard import build  # noqa: E402

build(
    ROOT,
    title="Google Test Automation",
    eyebrow="SDET · API & UI automation",
    summary="Weekly automated checks of Google's public platforms: Public DNS over HTTPS, the Fonts API, the Calendar holiday feed, the Books API, google.com's web security posture and a polite browser smoke suite.",
    repo="google-test-automation",
    layers={
        "Calendar feed (iCal)": "Indonesian public holidays feed: RFC 5545 validity, required fields, unique UIDs, known dates",
        "Books API": "Search accuracy, schema, lookup by id, pagination, limits, language filter, errors (with GOOGLE_API_KEY)",
        "Books API contract": "Keyless: search and lookup methods, required q, paging limits, filters and Volume schema from the Discovery document",
        "Public DNS (DoH)": "A/AAAA/MX resolution, NXDOMAIN, DNSSEC validation and failure, TTLs, bad input",
        "Fonts API": "Weights, WOFF2 delivery, font-display, CORS, unknown family, subsetting",
        "Web platform": "Sign-in HTTPS and HSTS, clickjacking and XSS headers, robots.txt, security.txt, response time",
        "UI smoke (Playwright)": "Search box, search results, accessibility basics, console errors",
    },
    notes=[
        "Blocked means Google showed a consent page or reCAPTCHA to the CI browser, which is normal for cloud IP addresses. It is reported separately so it never hides a real regression.",
        "Not configured means the Books API's shared keyless quota was used up; add a free GOOGLE_API_KEY repository secret to run that layer every time. The keyless Books API contract layer runs either way.",
        "Every API used is official and public; the browser layer is a handful of page loads per weekly run.",
        "Each check is retried once to absorb network blips before it is reported as failed.",
    ],
)
