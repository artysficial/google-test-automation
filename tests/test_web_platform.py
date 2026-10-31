"""google.com as a web platform, at the HTTP level."""

import pytest

pytestmark = pytest.mark.category("Web platform")


@pytest.fixture(scope="module")
def home(http):
    return http.get("https://www.google.com/", timeout=15)


@pytest.mark.severity("high")
def test_sign_in_is_never_served_over_http(http):
    """The sign-in page redirects plain HTTP to HTTPS"""
    response = http.get("http://accounts.google.com/", allow_redirects=False, timeout=15)
    assert response.status_code in (301, 302, 307, 308) and response.headers["location"].startswith("https://")


@pytest.mark.severity("high")
def test_sign_in_sends_hsts_for_all_subdomains(http):
    """The sign-in host sends HSTS covering subdomains for at least a year"""
    hsts = http.get("https://accounts.google.com/", allow_redirects=False, timeout=15).headers.get("strict-transport-security", "")
    max_age = int(hsts.split("max-age=")[1].split(";")[0]) if "max-age=" in hsts else 0
    assert max_age >= 31536000 and "includesubdomains" in hsts.lower()


@pytest.mark.severity("high")
def test_home_page_is_served(home):
    """The home page returns HTML"""
    assert home.status_code == 200 and "text/html" in home.headers["content-type"]


@pytest.mark.severity("medium")
def test_home_cannot_be_framed(home):
    """The home page is protected against clickjacking"""
    assert home.headers.get("x-frame-options", "").upper() in ("SAMEORIGIN", "DENY") or "frame-ancestors" in home.headers.get("content-security-policy", "")


@pytest.mark.severity("medium")
def test_xss_protection_headers(home):
    """X-XSS-Protection is disabled in favour of CSP, or a CSP is present"""
    assert home.headers.get("x-xss-protection") == "0" or "content-security-policy" in home.headers


@pytest.mark.severity("low")
def test_robots_txt_disallows_search_results(http):
    """robots.txt tells crawlers not to fetch /search"""
    text = http.get("https://www.google.com/robots.txt", timeout=15).text
    assert "Disallow: /search" in text


@pytest.mark.severity("low")
def test_security_txt_is_published(http):
    """A security.txt tells researchers how to report vulnerabilities (RFC 9116)"""
    response = http.get("https://www.google.com/.well-known/security.txt", timeout=15)
    assert response.status_code == 200 and "Contact:" in response.text


@pytest.mark.severity("medium")
def test_home_responds_quickly(home):
    """The home page answers within 2 seconds"""
    assert home.elapsed.total_seconds() < 2
