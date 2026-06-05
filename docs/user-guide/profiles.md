# Profiles

Profiles describe browser-visible settings such as viewport, locale, timezone, language headers, and device characteristics.

## Built-in profiles

```python
from webskrap import get_profile, list_profiles

for profile in list_profiles():
    print(profile.name)

profile = get_profile("desktop-chrome")
```

Built-in profile names:

- `desktop-chrome`
- `desktop-edge`
- `mobile-chrome`

## Custom profile

```python
from webskrap import BrowserProfile, Viewport

profile = BrowserProfile(
    name="fr-desktop",
    viewport=Viewport(width=1440, height=900),
    screen=Viewport(width=1440, height=900),
    locale="fr-FR",
    timezone_id="Europe/Paris",
    navigator_languages=["fr-FR", "fr", "en-US", "en"],
)
```

Pass it to a session:

```python
session = await client.session("fr", profile=profile)
```
