"""Completa los valores secretos de la configuración local."""

import re
import secrets
from pathlib import Path


def main() -> None:
    path = Path(".env")
    content = path.read_text(encoding="utf-8")
    pattern = r"(?m)^JWT_SECRET=(.*)$"

    def secret_value(match: re.Match[str]) -> str:
        current = match.group(1).strip()
        if len(current) < 16 or current == "cambie-esta-clave-en-produccion":
            return f"JWT_SECRET={secrets.token_urlsafe(32)}"
        return match.group(0)

    content, replacements = re.subn(pattern, secret_value, content)
    if replacements != 1:
        raise RuntimeError("JWT_SECRET no está definido correctamente en .env.")
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
