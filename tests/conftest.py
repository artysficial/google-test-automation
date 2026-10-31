"""Shared fixtures: HTTP session and a Playwright browser."""

from __future__ import annotations

import os

import pytest
import requests

pytest_plugins = ["results_plugin"]

BLOCK_SIGNS = ("unusual traffic", "before you continue", "recaptcha", "/sorry/")


@pytest.fixture(scope="session")
def http():
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (portfolio test automation; +https://artysficial.github.io/)"
    yield session
    session.close()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        channel = os.environ.get("BROWSER_CHANNEL") or None
        instance = p.chromium.launch(channel=channel, headless=True)
        yield instance
        instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(locale="en-US", viewport={"width": 1366, "height": 900})
    tab = context.new_page()
    yield tab
    context.close()


def skip_if_blocked(page) -> None:
    """Google shows consent pages and reCAPTCHA to many automated browsers, especially from cloud IPs.
    That is expected bot protection, not a defect: report it as blocked."""
    if "/sorry/" in page.url or "consent.google" in page.url or any(s in page.content().lower() for s in BLOCK_SIGNS[:2]):
        pytest.skip("blocked: consent or reCAPTCHA shown to the automated browser")
