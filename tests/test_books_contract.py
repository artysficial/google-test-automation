"""Books API v1 contract, read from Google's public Discovery document. It is keyless and outside the shared
search quota, so this layer runs on every build even when the live Books checks report not configured."""

import pytest

pytestmark = pytest.mark.category("Books API contract")
DISCOVERY = "https://www.googleapis.com/discovery/v1/apis/books/v1/rest"


@pytest.fixture(scope="module")
def spec(http):
    response = http.get(DISCOVERY, timeout=15)
    assert response.status_code == 200, f"discovery document returned {response.status_code}"
    return response.json()


def volumes(spec, name):
    return spec["resources"]["volumes"]["methods"][name]


@pytest.mark.severity("high")
def test_discovery_document_is_public(http):
    """The API description is served without a key as JSON for books v1 over REST"""
    response = http.get(DISCOVERY, timeout=15)
    assert response.status_code == 200 and response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert (body["name"], body["version"], body["protocol"]) == ("books", "v1", "rest")


@pytest.mark.severity("high")
def test_volume_search_is_a_get_that_requires_q(spec):
    """volumes.list is GET books/v1/volumes, q is required and the response is a Volumes list"""
    search = volumes(spec, "list")
    assert search["httpMethod"] == "GET" and search["path"] == "books/v1/volumes"
    assert search["parameters"]["q"]["required"] is True and search["parameterOrder"] == ["q"]
    assert search["response"]["$ref"] == "Volumes"


@pytest.mark.severity("medium")
def test_paging_limits_are_documented(spec):
    """maxResults is an integer from 0 to 40 and startIndex starts at 0"""
    params = volumes(spec, "list")["parameters"]
    assert params["maxResults"]["type"] == "integer"
    assert (params["maxResults"]["minimum"], params["maxResults"]["maximum"]) == ("0", "40")
    assert params["startIndex"]["minimum"] == "0"


@pytest.mark.severity("medium")
def test_volume_lookup_takes_an_id_in_the_path(spec):
    """volumes.get is books/v1/volumes/{volumeId} and returns a single Volume"""
    lookup = volumes(spec, "get")
    assert lookup["path"] == "books/v1/volumes/{volumeId}" and lookup["parameterOrder"] == ["volumeId"]
    assert lookup["parameters"]["volumeId"]["location"] == "path"
    assert lookup["response"]["$ref"] == "Volume"


@pytest.mark.severity("medium")
def test_volume_schema_documents_the_fields_under_test(spec):
    """A Volume has id, volumeInfo, saleInfo and accessInfo; pageCount is an integer and ISBN_13 an identifier type"""
    volume = spec["schemas"]["Volume"]["properties"]
    assert {"id", "volumeInfo", "saleInfo", "accessInfo"} <= set(volume)
    info = volume["volumeInfo"]["properties"]
    assert {"title", "authors", "language", "industryIdentifiers"} <= set(info)
    assert info["pageCount"]["type"] == "integer"
    assert "ISBN_13" in info["industryIdentifiers"]["items"]["properties"]["type"]["description"]


@pytest.mark.severity("low")
def test_search_filters_are_documented(spec):
    """langRestrict, orderBy (relevance, newest) and printType are available on search"""
    params = volumes(spec, "list")["parameters"]
    assert params["langRestrict"]["type"] == "string"
    assert {"relevance", "newest"} <= set(params["orderBy"]["enum"])
    assert "BOOKS" in params["printType"]["enum"]


@pytest.mark.severity("low")
def test_search_response_reports_a_total(spec):
    """A Volumes response carries an integer totalItems alongside the items"""
    listing = spec["schemas"]["Volumes"]["properties"]
    assert listing["totalItems"]["type"] == "integer" and "items" in listing
