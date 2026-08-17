from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
from urllib import error, parse, request

BHA_API_ROOT = "https://api09.horseracing.software/bha/v1"
DEFAULT_TIMEOUT_SECONDS = 30.0
PROVIDER_NAME = "British Horseracing Authority"


@dataclass(frozen=True)
class BhaResponse:
    candidate_identity: str
    request_url: str
    request_params: dict[str, Any]
    requested_at_utc: str
    response_status: int | None
    raw_response: str | None
    payload: Any
    error: str | None
    cache_path: Path
    from_cache: bool

    @property
    def ok(self) -> bool:
        return (
            self.error is None
            and self.response_status is not None
            and 200 <= self.response_status < 300
        )


class BhaApiClient:
    """Small cached client for the structured BHA public service."""

    def __init__(
        self,
        cache_dir: Path | str,
        *,
        api_root: str = BHA_API_ROOT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = "Inside-Rails-Research/0.1",
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api_root = api_root.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def fixture_search(
        self,
        from_date: date | str,
        to_date: date | str,
        *,
        results_available: bool | None = None,
        order: str = "asc",
        page: int = 1,
        per_page: int = 100,
        refresh: bool = False,
    ) -> BhaResponse:
        params: dict[str, Any] = {
            "fromdate": _date_text(from_date),
            "todate": _date_text(to_date),
            "order": order,
            "page": page,
            "per_page": per_page,
        }
        if results_available is not None:
            params["resultsAvailable"] = 1 if results_available else 0
        candidate_identity = f"fixtures:{params['fromdate']}:{params['todate']}:page={page}"
        return self.get_json(
            "/fixtures/",
            params=params,
            candidate_identity=candidate_identity,
            refresh=refresh,
        )

    def fixture_detail(
        self,
        fixture_year: int,
        fixture_id: int | str,
        *,
        refresh: bool = False,
    ) -> BhaResponse:
        return self.get_json(
            f"/fixtures/{fixture_year}/{fixture_id}",
            candidate_identity=f"fixture:{fixture_year}:{fixture_id}",
            refresh=refresh,
        )

    def fixture_races(
        self,
        fixture_year: int,
        fixture_id: int | str,
        *,
        refresh: bool = False,
    ) -> BhaResponse:
        return self.get_json(
            f"/fixtures/{fixture_year}/{fixture_id}/races",
            candidate_identity=f"fixture-races:{fixture_year}:{fixture_id}",
            refresh=refresh,
        )

    def race_detail(
        self,
        year_of_race: int,
        race_id: int | str,
        division_sequence: int | str,
        *,
        refresh: bool = False,
    ) -> BhaResponse:
        race_ref = f"{year_of_race}:{race_id}:{division_sequence}"
        return self.get_json(
            f"/races/{year_of_race}/{race_id}/{division_sequence}",
            candidate_identity=f"race:{race_ref}",
            refresh=refresh,
        )

    def race_results(
        self,
        year_of_race: int,
        race_id: int | str,
        division_sequence: int | str,
        *,
        refresh: bool = False,
    ) -> BhaResponse:
        race_ref = f"{year_of_race}:{race_id}:{division_sequence}"
        return self.get_json(
            f"/races/{year_of_race}/{race_id}/{division_sequence}/results",
            candidate_identity=f"race-results:{race_ref}",
            refresh=refresh,
        )

    def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        candidate_identity: str,
        refresh: bool = False,
    ) -> BhaResponse:
        clean_params = {str(key): value for key, value in (params or {}).items()}
        request_url = self._request_url(path, clean_params)
        cache_path = self._cache_path(candidate_identity, request_url)

        if cache_path.exists() and not refresh:
            return self._read_cache(cache_path, from_cache=True)

        requested_at = datetime.now(timezone.utc).isoformat()
        raw_response: str | None = None
        status: int | None = None
        payload: Any = None
        request_error: str | None = None

        http_request = request.Request(
            request_url,
            headers={
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
            method="GET",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                status = response.getcode()
                raw_response = response.read().decode("utf-8")
            try:
                payload = json.loads(raw_response)
            except json.JSONDecodeError as exc:
                request_error = f"invalid_json: {exc}"
        except error.HTTPError as exc:
            status = exc.code
            raw_response = exc.read().decode("utf-8", errors="replace")
            request_error = f"http_error: {exc}"
        except error.URLError as exc:
            request_error = f"url_error: {exc}"
        except TimeoutError as exc:
            request_error = f"timeout_error: {exc}"

        cache_record = {
            "provider": PROVIDER_NAME,
            "candidate_identity": candidate_identity,
            "request_url": request_url,
            "request_params": clean_params,
            "requested_at_utc": requested_at,
            "response_status": status,
            "raw_response": raw_response,
            "payload": payload,
            "error": request_error,
        }
        _write_json_atomic(cache_path, cache_record)
        return self._response_from_record(cache_path, cache_record, from_cache=False)

    def _request_url(self, path: str, params: Mapping[str, Any]) -> str:
        normalized_path = "/" + path.lstrip("/")
        base = f"{self.api_root}{normalized_path}"
        if not params:
            return base
        return f"{base}?{parse.urlencode(sorted(params.items()))}"

    def _cache_path(self, candidate_identity: str, request_url: str) -> Path:
        digest = hashlib.sha256(request_url.encode("utf-8")).hexdigest()[:16]
        safe_identity = "".join(
            char if char.isalnum() or char in {"-", "_", "."} else "_"
            for char in candidate_identity
        ).strip("_")
        safe_identity = safe_identity[:100] or "bha-request"
        return self.cache_dir / f"{safe_identity}__{digest}.json"

    def _read_cache(self, cache_path: Path, *, from_cache: bool) -> BhaResponse:
        with cache_path.open("r", encoding="utf-8") as handle:
            record = json.load(handle)
        return self._response_from_record(cache_path, record, from_cache=from_cache)

    @staticmethod
    def _response_from_record(
        cache_path: Path,
        record: Mapping[str, Any],
        *,
        from_cache: bool,
    ) -> BhaResponse:
        return BhaResponse(
            candidate_identity=str(record["candidate_identity"]),
            request_url=str(record["request_url"]),
            request_params=dict(record.get("request_params") or {}),
            requested_at_utc=str(record["requested_at_utc"]),
            response_status=record.get("response_status"),
            raw_response=record.get("raw_response"),
            payload=record.get("payload"),
            error=record.get("error"),
            cache_path=cache_path,
            from_cache=from_cache,
        )


def default_bha_cache_dir(repo_root: Path | str, namespace: str) -> Path:
    """Return the ignored local cache directory for one BHA investigation."""
    root = Path(repo_root)
    safe_namespace = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in namespace
    ).strip("_")
    if not safe_namespace:
        raise ValueError("namespace must contain at least one usable character")
    return root / "data" / "cache" / safe_namespace


def _date_text(value: date | str) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temporary_path.replace(path)
