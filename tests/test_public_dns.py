"""Google Public DNS JSON API (DNS-over-HTTPS, https://dns.google/resolve)."""

import pytest

pytestmark = pytest.mark.category("Public DNS (DoH)")
BASE = "https://dns.google/resolve"
TYPES = {"A": 1, "CNAME": 5, "MX": 15, "TXT": 16, "AAAA": 28}


def resolve(http, name, record="A", **params):
    return http.get(BASE, params={"name": name, "type": record, **params}, timeout=15)


@pytest.mark.severity("high")
def test_a_record_resolves(http):
    """google.com resolves to at least one IPv4 address"""
    body = resolve(http, "google.com").json()
    assert body["Status"] == 0  # NOERROR
    addresses = [a["data"] for a in body["Answer"] if a["type"] == TYPES["A"]]
    assert addresses and all(len(a.split(".")) == 4 for a in addresses)


@pytest.mark.severity("medium")
def test_aaaa_record_resolves(http):
    """google.com has IPv6 (AAAA) records"""
    body = resolve(http, "google.com", "AAAA").json()
    assert any(a["type"] == TYPES["AAAA"] and ":" in a["data"] for a in body["Answer"])


@pytest.mark.severity("medium")
def test_mx_records_have_priorities(http):
    """gmail.com publishes MX records with a priority and host"""
    answers = resolve(http, "gmail.com", "MX").json()["Answer"]
    for answer in answers:
        priority, host = answer["data"].split()
        assert priority.isdigit() and host.endswith(".")


@pytest.mark.severity("high")
def test_nonexistent_domain_returns_nxdomain(http):
    """A domain that does not exist returns NXDOMAIN (status 3)"""
    assert resolve(http, "this-domain-does-not-exist-artysficial.example").json()["Status"] == 3


@pytest.mark.severity("high")
def test_dnssec_validation_is_reported(http):
    """For a DNSSEC-signed zone the AD (authenticated data) flag is set"""
    body = resolve(http, "cloudflare.com", do="1").json()
    assert body["AD"] is True


@pytest.mark.severity("medium")
def test_broken_dnssec_is_refused(http):
    """A zone with a deliberately broken signature fails validation (SERVFAIL)"""
    assert resolve(http, "dnssec-failed.org").json()["Status"] == 2


@pytest.mark.severity("low")
def test_invalid_record_type_is_rejected(http):
    """An unknown record type is a client error"""
    assert resolve(http, "google.com", "NOTATYPE").status_code == 400


@pytest.mark.severity("low")
def test_answers_carry_ttls(http):
    """Every answer has a positive TTL"""
    assert all(a["TTL"] > 0 for a in resolve(http, "google.com").json()["Answer"])
