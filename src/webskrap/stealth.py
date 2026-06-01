from __future__ import annotations

import json

from playwright.async_api import BrowserContext

from webskrap.models import BrowserProfile, StealthConfig


async def apply_stealth(
    context: BrowserContext,
    profile: BrowserProfile,
    config: StealthConfig,
) -> None:
    if not config.enabled:
        return
    await context.add_init_script(script=build_stealth_script(profile, config))


def build_stealth_script(profile: BrowserProfile, config: StealthConfig) -> str:
    payload = {
        "languages": profile.navigator_languages,
        "hardwareConcurrency": profile.hardware_concurrency,
        "deviceMemory": profile.device_memory,
        "webglVendor": profile.webgl_vendor,
        "webglRenderer": profile.webgl_renderer,
        "patchWebdriver": config.patch_webdriver,
        "patchChromeRuntime": config.patch_chrome_runtime,
        "patchPermissions": config.patch_permissions,
        "patchPlugins": config.patch_plugins,
        "patchWebgl": config.patch_webgl,
        "patchCanvas": config.patch_canvas,
        "patchHardware": config.patch_hardware,
    }
    encoded = json.dumps(payload, separators=(",", ":"))
    return f"""
(() => {{
  const profile = {encoded};
  const defineGetter = (target, prop, getter) => {{
    try {{
      Object.defineProperty(target, prop, {{ get: getter, configurable: true }});
    }} catch (_) {{}}
  }};

  if (profile.patchWebdriver) {{
    defineGetter(Navigator.prototype, "webdriver", () => undefined);
  }}

  defineGetter(Navigator.prototype, "languages", () => profile.languages.slice());
  defineGetter(Navigator.prototype, "language", () => profile.languages[0]);

  if (profile.patchHardware) {{
    defineGetter(Navigator.prototype, "hardwareConcurrency", () => profile.hardwareConcurrency);
    defineGetter(Navigator.prototype, "deviceMemory", () => profile.deviceMemory);
  }}

  if (profile.patchPlugins) {{
    defineGetter(Navigator.prototype, "plugins", () => [1, 2, 3, 4, 5]);
    defineGetter(Navigator.prototype, "mimeTypes", () => [1, 2, 3]);
  }}

  if (profile.patchChromeRuntime && !window.chrome) {{
    try {{
      Object.defineProperty(window, "chrome", {{
        configurable: true,
        value: {{
          app: {{ isInstalled: false }},
          csi: () => ({{}}),
          loadTimes: () => ({{}}),
          runtime: {{}}
        }}
      }});
    }} catch (_) {{}}
  }}

  if (profile.patchPermissions && navigator.permissions && navigator.permissions.query) {{
    const originalQuery = navigator.permissions.query.bind(navigator.permissions);
    navigator.permissions.query = (parameters) => {{
      if (parameters && parameters.name === "notifications") {{
        return Promise.resolve({{ state: Notification.permission }});
      }}
      return originalQuery(parameters);
    }};
  }}

  if (profile.patchWebgl) {{
    const patchWebGL = (proto) => {{
      if (!proto || !proto.getParameter) return;
      const original = proto.getParameter;
      proto.getParameter = function(parameter) {{
        if (parameter === 37445) return profile.webglVendor;
        if (parameter === 37446) return profile.webglRenderer;
        return original.apply(this, arguments);
      }};
    }};
    patchWebGL(window.WebGLRenderingContext && window.WebGLRenderingContext.prototype);
    patchWebGL(window.WebGL2RenderingContext && window.WebGL2RenderingContext.prototype);
  }}

  if (profile.patchCanvas && window.HTMLCanvasElement) {{
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {{
      try {{
        const context = this.getContext("2d");
        if (context && this.width && this.height) {{
          const x = Math.min(1, this.width - 1);
          const y = Math.min(1, this.height - 1);
          const imageData = context.getImageData(x, y, 1, 1);
          imageData.data[0] = (imageData.data[0] + 1) % 255;
          context.putImageData(imageData, x, y);
        }}
      }} catch (_) {{}}
      return originalToDataURL.apply(this, arguments);
    }};
  }}
}})();
"""
