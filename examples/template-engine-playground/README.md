# Example: Web Development — Template Engine Playground

**[▶ Try it live](https://byoe-templates.netlify.app)**

The rendering core inside Jinja, EJS, Blade, and Django templates.
Type a template + JSON data, watch it **compile to tokens** and render live.

Example project for the [web-development learning path](../../topics/js-bundler/).

## Syntax

```
{{ user.name }}                          → variable
{% for u in users %}…{% endfor %}        → loop
{% if user.hireable %}…{% endif %}       → conditional
```

## What it teaches

- **Lexing**: the template is split into text / variable / tag tokens (shown live).
- **Rendering**: the token stream is walked with a data context; dot paths resolve.
- **Nesting**: `for`/`if` blocks find their matching end tag with a depth counter.

~80 lines of JS in `index.html` — no dependencies.

## Exercises

1. Add **filters**: `{{ name | upper }}`.
2. Add **HTML auto-escaping** (the security feature every real engine needs).
3. Add **template inheritance** (`{% extends %}` / `{% block %}`).
