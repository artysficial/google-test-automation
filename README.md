# Google Test Automation

[![Tests and dashboard](https://github.com/artysficial/google-test-automation/actions/workflows/tests.yml/badge.svg)](https://github.com/artysficial/google-test-automation/actions/workflows/tests.yml)
[![Dashboard](https://img.shields.io/badge/dashboard-live-0071e3)](https://artysficial.github.io/google-test-automation/)

Weekly automated checks of Google's public platforms, from API contracts to a real browser, with a dashboard
published on every run.

**[View the live dashboard →](https://artysficial.github.io/google-test-automation/)**

## Layers

| Layer | What is checked |
| --- | --- |
| Public DNS (DoH) | `dns.google/resolve`: A/AAAA/MX answers, NXDOMAIN, DNSSEC validation (AD flag) and a deliberately broken zone (SERVFAIL), TTLs, bad input |
| Fonts API | `fonts.googleapis.com/css2`: requested weights, WOFF2 delivery from gstatic, `font-display: swap`, CORS, unknown family, `text=` subsetting |
| Calendar feed (iCal) | the public Indonesian holidays feed: RFC 5545 validity, required properties, unique UIDs, Independence Day on 17 August, current year present |
| Books API | ISBN search accuracy, volume schema, lookup by id, pagination without duplicates, `maxResults` cap, language filter, errors |
| Web platform | sign-in never over HTTP, HSTS with subdomains, clickjacking/XSS headers, robots.txt, security.txt (RFC 9116), response time |
| UI smoke (Playwright) | search box, search results, accessible name and language, no console errors |

## Things the suite taught me

- `http://www.google.com` is still served over plain HTTP (no redirect), and `google.com` is not on the public HSTS
  preload list. What Google does protect is sign-in: `accounts.google.com` always redirects to HTTPS and sends
  HSTS with `includeSubDomains`. The tests assert that, rather than an assumption.
- The Books API's keyless quota is shared by every caller worldwide and runs out daily, so that layer uses a free
  `GOOGLE_API_KEY` when one is configured and reports *not configured* otherwise.
- Searching from a cloud IP usually triggers reCAPTCHA. That check reports *blocked*, separate from failures.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium      # or BROWSER_CHANNEL=msedge / chrome
export GOOGLE_API_KEY=...                  # optional: Books API layer
python -m pytest && python tools/build_dashboard.py
```

Built by [Rahmadani Tyas Ningrum](https://artysficial.github.io/) · MIT licence
