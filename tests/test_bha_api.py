import hashlib
import io
import json
from pathlib import Path
from urllib import error

from inside_rails.bha_api import (
    ACCESS_PROFILE,
    BHA_ORIGIN,
    BHA_RESULTS_REFERER,
    BhaApiClient,
    default_bha_cache_dir,
)


ACTIVE_TOKEN = "Bearer current-public-frontend-token"
APP_JS = f"""
// $httpProvider.defaults.headers.common['Authorization'] = 'Bearer obsolete-token';
$httpProvider.defaults.headers.common['Authorization'] = '{ACTIVE_TOKEN}';
""".encode("utf-8")


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self._status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def getcode(self):
        return self._status

    def read(self):
        return self._body


def test_default_bha_cache_dir():
    assert default_bha_cache_dir("/repo", "notebook 28") == Path(
        "/repo/data/cache/notebook_28"
    )


def test_fixture_search_uses_frontend_authorization_and_safe_cache(
    tmp_path,
    monkeypatch,
):
    calls = []
    app_js_url = "https://example.test/app.js"

    def fake_urlopen(req, timeout):
        calls.append((req, timeout))
        if req.full_url == app_js_url:
            return FakeResponse(APP_JS)

        assert req.get_header("Authorization") == ACTIVE_TOKEN
        assert req.get_header("Origin") == BHA_ORIGIN
        assert req.get_header("Referer") == BHA_RESULTS_REFERER
        assert req.get_header("Accept") == "application/json"
        return FakeResponse(b'{"fixtures": [{"fixtureId": 123}]}')

    monkeypatch.setattr("inside_rails.bha_api.request.urlopen", fake_urlopen)

    client = BhaApiClient(
        tmp_path,
        api_root="https://example.test/bha/v1",
        app_js_url=app_js_url,
    )
    first = client.fixture_search("1995-01-01", "1995-01-01", results_available=True)
    second = client.fixture_search("1995-01-01", "1995-01-01", results_available=True)

    assert first.ok
    assert first.from_cache is False
    assert second.from_cache is True
    assert first.payload == {"fixtures": [{"fixtureId": 123}]}
    assert second.payload == first.payload
    assert len(calls) == 2  # one app.js request and one API request

    cached_text = first.cache_path.read_text(encoding="utf-8")
    cached = json.loads(cached_text)
    assert cached["provider"] == "British Horseracing Authority"
    assert cached["candidate_identity"] == "fixtures:1995-01-01:1995-01-01:page=1"
    assert cached["request_params"]["resultsAvailable"] == 1
    assert cached["response_status"] == 200
    assert cached["raw_response"] == '{"fixtures": [{"fixtureId": 123}]}'
    assert cached["access_profile"] == ACCESS_PROFILE
    assert cached["app_js_url"] == app_js_url
    assert cached["app_js_sha256"] == hashlib.sha256(APP_JS).hexdigest()
    assert cached["authorization_value_persisted"] is False
    assert ACTIVE_TOKEN not in cached_text
    assert "obsolete-token" not in cached_text


def test_http_error_is_cached_without_authorization_value(tmp_path, monkeypatch):
    app_js_url = "https://example.test/app.js"

    def fake_urlopen(req, timeout):
        if req.full_url == app_js_url:
            return FakeResponse(APP_JS)
        assert req.get_header("Authorization") == ACTIVE_TOKEN
        raise error.HTTPError(
            req.full_url,
            404,
            "Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"message":"missing"}'),
        )

    monkeypatch.setattr("inside_rails.bha_api.request.urlopen", fake_urlopen)

    client = BhaApiClient(
        tmp_path,
        api_root="https://example.test/bha/v1",
        app_js_url=app_js_url,
    )
    result = client.fixture_detail(1990, 999)

    assert result.ok is False
    assert result.response_status == 404
    assert result.error.startswith("http_error:")
    assert result.raw_response == '{"message":"missing"}'
    assert result.cache_path.exists()
    assert ACTIVE_TOKEN not in result.cache_path.read_text(encoding="utf-8")


def test_frontend_authorization_failure_is_cached_without_frontend_body(
    tmp_path,
    monkeypatch,
):
    app_js_url = "https://example.test/app.js"

    def fake_urlopen(req, timeout):
        assert req.full_url == app_js_url
        raise error.HTTPError(
            req.full_url,
            403,
            "Forbidden",
            hdrs=None,
            fp=io.BytesIO(b"credential-bearing frontend body must not be cached"),
        )

    monkeypatch.setattr("inside_rails.bha_api.request.urlopen", fake_urlopen)

    client = BhaApiClient(
        tmp_path,
        api_root="https://example.test/bha/v1",
        app_js_url=app_js_url,
    )
    result = client.fixture_search("1995-01-01", "1995-01-01")

    assert result.ok is False
    assert result.response_status is None
    assert result.error.startswith("authorization_error:")

    cached_text = result.cache_path.read_text(encoding="utf-8")
    cached = json.loads(cached_text)
    assert cached["app_js_response_status"] == 403
    assert cached["raw_response"] is None
    assert "credential-bearing frontend body" not in cached_text


def test_access_profile_changes_cache_identity(tmp_path):
    client = BhaApiClient(
        tmp_path,
        api_root="https://example.test/bha/v1",
        app_js_url="https://example.test/app.js",
    )
    request_url = "https://example.test/bha/v1/fixtures/?fromdate=1995-01-01"
    path = client._cache_path("fixtures:test", request_url)

    old_anonymous_digest = hashlib.sha256(request_url.encode("utf-8")).hexdigest()[:16]
    assert old_anonymous_digest not in path.name
