"""Google Books API v1. Public data; the keyless quota is shared by everyone, so a free
GOOGLE_API_KEY is used when available."""

import os

import pytest

pytestmark = pytest.mark.category("Books API")
BASE = "https://www.googleapis.com/books/v1/volumes"
ISBN = "9780132350884"  # Clean Code, Robert C. Martin
KEY = os.environ.get("GOOGLE_API_KEY")


def get(http, url, **params):
    response = http.get(url, params={**params, **({"key": KEY} if KEY else {})}, timeout=15)
    if response.status_code == 429:
        pytest.skip("not configured: shared keyless quota exhausted; set GOOGLE_API_KEY")
    return response


def search(http, **params):
    return get(http, BASE, **params)


@pytest.mark.severity("high")
def test_isbn_search_finds_the_book(http):
    """Searching by ISBN returns the right title and author"""
    items = search(http, q=f"isbn:{ISBN}").json()["items"]
    info = items[0]["volumeInfo"]
    assert "Clean Code" in info["title"]
    assert any("Martin" in author for author in info["authors"])


@pytest.mark.severity("high")
def test_volume_has_the_documented_schema(http):
    """A volume carries id, volumeInfo, saleInfo and accessInfo with typed fields"""
    volume = search(http, q=f"isbn:{ISBN}").json()["items"][0]
    assert {"id", "volumeInfo", "saleInfo", "accessInfo"} <= set(volume)
    info = volume["volumeInfo"]
    assert isinstance(info["title"], str) and isinstance(info.get("pageCount", 0), int)
    identifiers = {i["type"]: i["identifier"] for i in info["industryIdentifiers"]}
    assert identifiers.get("ISBN_13") == ISBN


@pytest.mark.severity("medium")
def test_volume_lookup_by_id_matches_search(http):
    """Fetching a volume by id returns the same book as the search result"""
    hit = search(http, q=f"isbn:{ISBN}").json()["items"][0]
    volume = get(http, f"{BASE}/{hit['id']}").json()
    assert volume["id"] == hit["id"]
    assert volume["volumeInfo"]["title"] == hit["volumeInfo"]["title"]


@pytest.mark.severity("medium")
def test_pagination_returns_distinct_pages(http):
    """startIndex/maxResults pages through results without repeating volumes"""
    first = search(http, q="software testing", maxResults=10, startIndex=0).json()["items"]
    second = search(http, q="software testing", maxResults=10, startIndex=10).json()["items"]
    ids = [v["id"] for v in first + second]
    assert len(first) == len(second) == 10
    assert len(set(ids)) >= 18  # the index can shift slightly between calls


@pytest.mark.severity("medium")
def test_max_results_above_forty_is_rejected(http):
    """maxResults is capped at 40"""
    assert search(http, q="testing", maxResults=41).status_code == 400


@pytest.mark.severity("low")
def test_language_filter_is_applied(http):
    """langRestrict limits results to the requested language"""
    items = search(http, q="pengujian perangkat lunak", langRestrict="id", maxResults=10).json().get("items", [])
    assert items and all(v["volumeInfo"].get("language") == "id" for v in items)


@pytest.mark.severity("low")
def test_nonsense_query_returns_no_items(http):
    """A query with no matches returns totalItems 0 and no items"""
    body = search(http, q="intitle:qzxwvjkqzxwvjk").json()
    assert body["totalItems"] == 0 and "items" not in body


@pytest.mark.severity("low")
def test_missing_query_is_rejected(http):
    """A search without q is a 400"""
    assert search(http).status_code == 400
