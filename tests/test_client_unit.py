from __future__ import annotations

import pytest

from webskrap.client import WebSkrapError, WebSkrapSession, _resource_route_handler
from webskrap.models import ResourcePolicy, SessionConfig
from webskrap.profiles import get_profile


class _Request:
    def __init__(self, resource_type: str) -> None:
        self.resource_type = resource_type


class _Route:
    def __init__(self, resource_type: str) -> None:
        self.request = _Request(resource_type)
        self.aborted = False
        self.continued = False

    async def abort(self) -> None:
        self.aborted = True

    async def continue_(self) -> None:
        self.continued = True


class _Mouse:
    def __init__(self) -> None:
        self.moves: list[tuple[float, float, int | None]] = []
        self.clicks: list[tuple[float, float, dict[str, object]]] = []

    async def move(self, x: float, y: float, *, steps: int | None = None) -> None:
        self.moves.append((x, y, steps))

    async def click(self, x: float, y: float, **options: object) -> None:
        self.clicks.append((x, y, options))


class _Keyboard:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    async def down(self, key: str) -> None:
        self.events.append(("down", key))

    async def up(self, key: str) -> None:
        self.events.append(("up", key))


class _Locator:
    def __init__(self, box: dict[str, float] | None = None, count: int = 1) -> None:
        self.box = box or {"x": 10, "y": 20, "width": 100, "height": 40}
        self.element_count = count
        self.waits: list[dict[str, object]] = []
        self.scrolled: list[dict[str, object]] = []

    async def wait_for(self, **options: object) -> None:
        self.waits.append(options)

    async def scroll_into_view_if_needed(self, **options: object) -> None:
        self.scrolled.append(options)

    async def bounding_box(self, **options: object) -> dict[str, float] | None:
        return self.box

    async def count(self) -> int:
        return self.element_count


class _Page:
    def __init__(self, locator: _Locator | None = None) -> None:
        self._locator = locator or _Locator()
        self.mouse = _Mouse()
        self.keyboard = _Keyboard()
        self.clicks: list[tuple[str, dict[str, object]]] = []
        self.timeouts: list[float] = []
        self.locators: list[str] = []

    def locator(self, selector: str) -> _Locator:
        self.locators.append(selector)
        return self._locator

    async def click(self, selector: str, **options: object) -> None:
        self.clicks.append((selector, options))

    async def wait_for_timeout(self, timeout: float) -> None:
        self.timeouts.append(timeout)


def _session() -> WebSkrapSession:
    return WebSkrapSession(
        name="test",
        context=None,  # type: ignore[arg-type]
        config=SessionConfig(),
        profile=get_profile(None),
    )


@pytest.mark.asyncio
async def test_lite_resource_policy_blocks_heavy_assets() -> None:
    handler = _resource_route_handler(ResourcePolicy.LITE)
    route = _Route("image")

    await handler(route)

    assert route.aborted is True
    assert route.continued is False


@pytest.mark.asyncio
async def test_lite_resource_policy_allows_documents() -> None:
    handler = _resource_route_handler(ResourcePolicy.LITE)
    route = _Route("document")

    await handler(route)

    assert route.aborted is False
    assert route.continued is True


@pytest.mark.asyncio
async def test_human_click_false_delegates_to_page_click() -> None:
    page = _Page()

    await _session().human_click(
        page,  # type: ignore[arg-type]
        "label[for='radio1']",
        human=False,
        timeout=1000,
        strict=True,
    )

    assert page.clicks == [("label[for='radio1']", {"timeout": 1000, "strict": True})]
    assert page.mouse.clicks == []


@pytest.mark.asyncio
async def test_human_click_waits_moves_and_clicks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("webskrap.client.uniform", lambda _start, _end: 0)
    locator = _Locator()
    page = _Page(locator)

    await _session().human_click(
        page,  # type: ignore[arg-type]
        "label[for='radio1']",
        position={"x": 20, "y": 10},
        timeout=1500,
        button="left",
        click_count=1,
        delay=25,
        modifiers=["Shift"],
    )

    assert page.locators == ["label[for='radio1']"]
    assert locator.waits == [{"state": "visible", "timeout": 1500}]
    assert locator.scrolled == [{"timeout": 1500}]
    assert page.timeouts == [0, 0]
    assert page.mouse.moves == [(30, 30, 1), (30, 30, 14)]
    assert page.mouse.clicks == [(30, 30, {"button": "left", "click_count": 1, "delay": 25})]
    assert page.keyboard.events == [("down", "Shift"), ("up", "Shift")]


@pytest.mark.asyncio
async def test_human_click_trial_does_not_click() -> None:
    page = _Page()

    await _session().human_click(
        page,  # type: ignore[arg-type]
        "label[for='radio1']",
        trial=True,
    )

    assert page.mouse.moves == []
    assert page.mouse.clicks == []


@pytest.mark.asyncio
async def test_human_click_raises_for_missing_bounding_box() -> None:
    page = _Page(_Locator(box=None))
    page._locator.box = None

    with pytest.raises(WebSkrapError, match="visible bounding box"):
        await _session().human_click(page, "label[for='radio1']")  # type: ignore[arg-type]
