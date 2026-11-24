#!/usr/bin/env python3
"""Generate a low-multiplier variant of Aethersailor's full Clash template.

Every run fetches the current upstream template, applies the local
customisations, and writes the result. The workflow commits only when the
output actually changes, so the raw URL always serves a freshly generated
file without any manual syncing.

Two edits:
  1. "🐢 低倍率节点" becomes a fallback group whose members are nodes with a
     multiplier <= 0.6 (0.01, 0.5, 0.6 ...), with "🚀 手动选择" as the tail.
  2. "🚀 手动选择" no longer references "🐢 低倍率节点", which would otherwise
     form a proxy-group loop.
"""

import sys
import urllib.request
from pathlib import Path

UPSTREAM = (
    "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/"
    "refs/heads/main/cfg/Custom_Clash_Full.ini"
)
OUT = Path(__file__).resolve().parent / "out" / "Custom_Clash_Full_LowMultiplier.ini"

GROUP = "🐢 低倍率节点"
SELECT = "🚀 手动选择"
# 0.00-0.59 and 0.6; excludes 0.61+, 0.8, 1.x, 2 ...
LOW = r"0\.(?:[0-5]\d|[0-6])(?![0-9])"

GROUP_PREFIX = f"custom_proxy_group={GROUP}`"
SELECT_PREFIX = f"custom_proxy_group={SELECT}`"
PATCHED_GROUP = (
    GROUP_PREFIX + "fallback`" + LOW + "`[]" + SELECT
    + "`https://www.gstatic.com/generate_204`300,,50"
)


def build(text: str) -> str:
    out: list[str] = []
    hit_group = hit_select = False
    for line in text.split("\n"):
        if line.startswith(GROUP_PREFIX):
            hit_group = True
            line = PATCHED_GROUP
        elif line.startswith(SELECT_PREFIX):
            hit_select = True
            line = line.replace(f"`[]{GROUP}`", "`")
        out.append(line)
    if not hit_group or not hit_select:
        sys.exit(
            "upstream changed: expected group line not found "
            f"(group={hit_group}, select={hit_select})"
        )
    result = "\n".join(out)
    if PATCHED_GROUP not in result:
        sys.exit("self-check failed: patched group line missing")
    return result


def main() -> None:
    with urllib.request.urlopen(UPSTREAM, timeout=60) as resp:
        text = resp.read().decode("utf-8")
    result = build(text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.read_text(encoding="utf-8") == result:
        print("unchanged")
        return
    OUT.write_text(result, encoding="utf-8")
    print(f"written {OUT} ({len(result)} bytes)")


if __name__ == "__main__":
    main()
