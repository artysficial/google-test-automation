"""Google Fonts CSS API v2 (fonts.googleapis.com/css2): the API millions of sites load fonts from."""

import re

import pytest

pytestmark = pytest.mark.category("Fonts API")
BASE = "https://fonts.googleapis.com/css2"
MODERN_BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"}


def css(http, family, **params):
    return http.get(BASE, params={"family": family, "display": "swap", **params}, headers=MODERN_BROWSER, timeout=15)


@pytest.mark.severity("high")
def test_font_css_declares_requested_weights(http):
    """Requesting Inter 400 and 700 returns @font-face rules for both weights"""
    response = css(http, "Inter:wght@400;700")
    assert response.status_code == 200 and "text/css" in response.headers["content-type"]
    weights = set(re.findall(r"font-weight:\s*(\d+)", response.text))
    assert {"400", "700"} <= weights


@pytest.mark.severity("high")
def test_font_files_are_woff2_and_downloadable(http):
    """Font URLs are WOFF2 on fonts.gstatic.com and actually download"""
    urls = re.findall(r"url\((https://[^)]+)\)", css(http, "Inter:wght@400").text)
    assert urls and all(u.startswith("https://fonts.gstatic.com/") for u in urls)
    font = http.get(urls[-1], timeout=15)
    assert font.status_code == 200 and font.content[:4] == b"wOF2"


@pytest.mark.severity("medium")
def test_display_swap_is_honoured(http):
    """display=swap is applied to every @font-face (avoids invisible text while loading)"""
    text = css(http, "Roboto:wght@400").text
    assert text.count("font-display: swap") == text.count("@font-face") > 0


@pytest.mark.severity("medium")
def test_css_can_be_loaded_cross_origin(http):
    """The CSS is served with CORS so any site can use it"""
    assert css(http, "Inter").headers.get("access-control-allow-origin") == "*"


@pytest.mark.severity("medium")
def test_unknown_family_is_rejected(http):
    """An unknown font family returns 400"""
    assert css(http, "Definitely Not A Real Font Family").status_code == 400


@pytest.mark.severity("low")
def test_text_parameter_subsets_the_font(http):
    """text= returns a subset font for just those characters"""
    full = re.findall(r"url\((https://[^)]+)\)", css(http, "Inter").text)
    subset = re.findall(r"url\((https://[^)]+)\)", css(http, "Inter", text="QA").text)
    assert len(subset) == 1 and subset[0] not in full
