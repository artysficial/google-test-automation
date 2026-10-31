"""Light browser smoke tests (Playwright). Consent pages and reCAPTCHA are reported as 'blocked'."""

import pytest

from conftest import skip_if_blocked

pytestmark = pytest.mark.category("UI smoke (Playwright)")


def open_home(page):
    page.goto("https://www.google.com/?hl=en", wait_until="domcontentloaded", timeout=45000)
    skip_if_blocked(page)


@pytest.mark.severity("high")
def test_home_page_has_a_search_box(page):
    """The home page shows the search box and the Google title"""
    open_home(page)
    assert page.title() == "Google"
    assert page.locator('textarea[name="q"], input[name="q"]').first.is_visible()


@pytest.mark.severity("high")
def test_search_shows_results(page):
    """Typing a query and pressing Enter lists results (often blocked from cloud IPs)"""
    open_home(page)
    box = page.locator('textarea[name="q"], input[name="q"]').first
    box.fill("software quality assurance")
    box.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    skip_if_blocked(page)
    page.wait_for_selector("#search, #rso", timeout=20000)
    assert page.locator("#search a h3, #rso a h3").count() >= 3


@pytest.mark.severity("medium")
def test_search_box_is_accessible(page):
    """The search box has an accessible name and the page declares a language"""
    open_home(page)
    box = page.locator('textarea[name="q"], input[name="q"]').first
    assert box.get_attribute("aria-label") or box.get_attribute("title")
    assert page.locator("html").get_attribute("lang")


@pytest.mark.severity("low")
def test_home_page_has_no_console_errors(page):
    """The home page loads without JavaScript errors"""
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    open_home(page)
    page.wait_for_timeout(1500)
    assert errors == []
