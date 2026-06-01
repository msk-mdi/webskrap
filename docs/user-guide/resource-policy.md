# Resource Policy

Resource policies control which request types are allowed.

```python
from webskrap import ResourcePolicy, SessionConfig

config = SessionConfig(resource_policy=ResourcePolicy.LITE)
```

## Policies

| Policy | Behavior |
| --- | --- |
| `ResourcePolicy.ALL` | Allows all resources. |
| `ResourcePolicy.LITE` | Blocks images, fonts, and media. |
| `ResourcePolicy.DOCUMENTS` | Blocks images, fonts, media, and stylesheets. |

Use `ALL` for maximum page fidelity. Use `LITE` when you want a faster page load while keeping stylesheets and scripts.
