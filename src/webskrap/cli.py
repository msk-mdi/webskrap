from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Literal, cast

import typer
from rich.console import Console
from rich.table import Table

from webskrap.client import WaitUntil, WebSkrapClient
from webskrap.models import ResourcePolicy, SessionConfig, WebRtcIPHandlingPolicy
from webskrap.profiles import get_profile, list_profiles

app = typer.Typer(help="WebSkrap browser scraping toolkit.")
console = Console()
Driver = Literal["playwright", "patchright"]


@app.command("profiles")
def profiles_command() -> None:
    table = Table(title="WebSkrap Profiles")
    table.add_column("Name")
    table.add_column("Viewport")
    table.add_column("Locale")
    table.add_column("Timezone")
    table.add_column("Mobile")

    for profile in list_profiles():
        table.add_row(
            profile.name,
            f"{profile.viewport.width}x{profile.viewport.height}",
            profile.locale,
            profile.timezone_id,
            "yes" if profile.is_mobile else "no",
        )

    console.print(table)


@app.command("doctor")
def doctor_command() -> None:
    asyncio.run(_doctor())


async def _doctor() -> None:
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        console.print(f"[red]Playwright import failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    try:
        manager = async_playwright()
        playwright = await manager.start()
        browser = await playwright.chromium.launch(headless=True)
        await browser.close()
        await playwright.stop()
    except Exception as exc:
        console.print("[yellow]Playwright is installed, but Chromium did not launch.[/yellow]")
        console.print(str(exc))
        console.print("Run: python -m playwright install chromium")
        raise typer.Exit(code=1) from exc

    console.print("[green]Playwright and Chromium are ready.[/green]")


@app.command("fetch")
def fetch_command(
    url: Annotated[str, typer.Argument(help="URL to fetch.")],
    profile: Annotated[
        str,
        typer.Option("--profile", "-p", help="Bundled profile name."),
    ] = "desktop-chrome",
    headed: Annotated[bool, typer.Option("--headed", help="Run with a visible browser.")] = False,
    driver: Annotated[
        str,
        typer.Option("--driver", help="Browser driver: playwright or patchright."),
    ] = "playwright",
    channel: Annotated[
        str | None,
        typer.Option("--channel", help="Browser channel, e.g. chrome."),
    ] = None,
    screenshot: Annotated[
        Path | None,
        typer.Option("--screenshot", help="Write a full-page screenshot to this path."),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write HTML to this file."),
    ] = None,
    wait_until: Annotated[
        str,
        typer.Option("--wait-until", help="commit, domcontentloaded, load, or networkidle."),
    ] = "domcontentloaded",
    timeout_ms: Annotated[
        float,
        typer.Option("--timeout-ms", min=1, help="Navigation timeout."),
    ] = 30_000,
    resource_policy: Annotated[
        ResourcePolicy,
        typer.Option("--resource-policy", help="Resource routing preset."),
    ] = ResourcePolicy.ALL,
    patchright_context_profile: Annotated[
        bool,
        typer.Option(
            "--patchright-context-profile",
            help="Apply locale/timezone/media profile metadata in Patchright contexts.",
        ),
    ] = False,
    reduce_fingerprint_surface: Annotated[
        bool,
        typer.Option(
            "--reduce-fingerprint-surface",
            help="Disable Chromium WebGL and canvas readback with native browser flags.",
        ),
    ] = False,
    launch_args: Annotated[
        list[str] | None,
        typer.Option(
            "--launch-arg",
            help="Additional browser launch argument. Repeat for multiple args.",
        ),
    ] = None,
    webrtc_ip_handling_policy: Annotated[
        str | None,
        typer.Option(
            "--webrtc-ip-handling-policy",
            help=(
                "Chromium WebRTC IP policy: default, default_public_and_private_interfaces, "
                "default_public_interface_only, or disable_non_proxied_udp."
            ),
        ),
    ] = None,
) -> None:
    asyncio.run(
        _fetch(
            url=url,
            profile=profile,
            headed=headed,
            driver=driver,
            channel=channel,
            screenshot=screenshot,
            output=output,
            wait_until=wait_until,
            timeout_ms=timeout_ms,
            resource_policy=resource_policy,
            patchright_context_profile=patchright_context_profile,
            reduce_fingerprint_surface=reduce_fingerprint_surface,
            launch_args=launch_args or [],
            webrtc_ip_handling_policy=webrtc_ip_handling_policy,
        )
    )


async def _fetch(
    *,
    url: str,
    profile: str,
    headed: bool,
    driver: str,
    channel: str | None,
    screenshot: Path | None,
    output: Path | None,
    wait_until: str,
    timeout_ms: float,
    resource_policy: ResourcePolicy,
    patchright_context_profile: bool,
    reduce_fingerprint_surface: bool,
    launch_args: list[str],
    webrtc_ip_handling_policy: str | None,
) -> None:
    selected_profile = get_profile(profile)
    config = SessionConfig(
        driver=_parse_driver(driver),
        headless=not headed,
        channel=channel,
        navigation_timeout_ms=timeout_ms,
        resource_policy=resource_policy,
        patchright_context_profile=patchright_context_profile,
        reduce_fingerprint_surface=reduce_fingerprint_surface,
        launch_args=launch_args,
        webrtc_ip_handling_policy=_parse_webrtc_ip_handling_policy(webrtc_ip_handling_policy),
    )

    async with WebSkrapClient() as client:
        result = await client.fetch(
            url,
            profile=selected_profile,
            config=config,
            wait_until=_parse_wait_until(wait_until),
            screenshot=screenshot or False,
            timeout_ms=timeout_ms,
        )

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.text, encoding="utf-8")

    console.print(f"[bold]Status:[/bold] {result.status}")
    console.print(f"[bold]Final URL:[/bold] {result.final_url}")
    console.print(f"[bold]Title:[/bold] {result.title}")
    if result.screenshot_path:
        console.print(f"[bold]Screenshot:[/bold] {result.screenshot_path}")
    if output:
        console.print(f"[bold]HTML:[/bold] {output}")


def _parse_wait_until(value: str) -> WaitUntil:
    valid = ("commit", "domcontentloaded", "load", "networkidle")
    if value not in valid:
        allowed = ", ".join(valid)
        raise typer.BadParameter(f"must be one of: {allowed}")
    return cast(WaitUntil, value)


def _parse_driver(value: str) -> Driver:
    valid = ("playwright", "patchright")
    if value not in valid:
        allowed = ", ".join(valid)
        raise typer.BadParameter(f"must be one of: {allowed}")
    return cast(Driver, value)


def _parse_webrtc_ip_handling_policy(
    value: str | None,
) -> WebRtcIPHandlingPolicy | None:
    if value is None:
        return None
    valid = (
        "default",
        "default_public_and_private_interfaces",
        "default_public_interface_only",
        "disable_non_proxied_udp",
    )
    if value not in valid:
        allowed = ", ".join(valid)
        raise typer.BadParameter(f"must be one of: {allowed}")
    return cast(WebRtcIPHandlingPolicy, value)
