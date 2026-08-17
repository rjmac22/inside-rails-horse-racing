import io
import json
from pathlib import Path
from urllib import error

from inside_rails.bha_api import BhaApiClient, default_bha_cache_dir


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


def test_fixture_search_caches_and_reuses_response(tmp_path, monkeypatch):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append((req.full_url, timeout))
        return FakeResponse(b'{"fixtures": [{"fixtureId": 123}]}')

    monkeypatch.setattr("inside_rails.bha_api.request.urlopen", fake_urlopen)

    client = BhaApiClient(tmp_path, api_root="https://example.test/bha/v1")
    first = client.fixture_search("1995-01-01", "1995-01-01", results_available=True)
    second = client.fixture_search("1995-01-01", "1995-01-01", results_available=True)

    assert first.ok
    assert first.from_cache is False
    assert second.from_cache is True
    assert first.payload == {"fixtures": [{"fixtureId": 123}]}
    assert second.payload == first.payload
    assert len(calls) == 1

    cached = json.loads(first.cache_path.read_text(encoding="utf-8"))
    assert cached["provider"] == "British Horseracing Authority"
    assert cached["candidate_identity"] == "fixtures:1995-01-01:1995-01-01:page=1"
    assert cached["request_params"]["resultsAvailable"] == 1
    assert cached["response_status"] == 200
    assert cached["raw_response"] == '{"fixtures": [{"fixtureId": 123}]}'


def test_http_error_is_cached(tmp_path, monkeypatch):
    def fake_urlopen(req, timeout):
        raise error.HTTPError(
            req.full_url,
            404,
            "Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"message":"missing"}'),
        )

    monkeypatch.setattr("inside_rails.bha_api.request.urlopen", fake_urlopen)

    client = BhaApiClient(tmp_path, api_root="https://example.test/bha/v1")
    result = client.fixture_detail(1990, 999)

    assert result.ok is False
    assert result.response_status == 404
    assert result.error.startswith("http_error:")
    assert result.raw_response == '{"message":"missing"}'
    assert result.cache_path.exists()
