from __future__ import annotations

import pytest

from webskrap.client import _resource_route_handler
from webskrap.models import ResourcePolicy


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
