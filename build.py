#!/usr/bin/env python3
"""Generate a low-multiplier variant of Aethersailor's full Clash template.

Every run fetches the current upstream template, applies the local
customisations, and writes the result. The workflow commits only when the
output actually changes, so the raw URL always serves a freshly generated
file without any manual syncing.

Edits:
  1. "🐢 低倍率节点" becomes a fallback group whose members are nodes with a
     multiplier <= 0.6 (0.01, 0.5, 0.6 ...), with "🚀 手动选择" as the tail.
  2. Every other group keeps only nodes whose multiplier is > 0.6, or that
     carry no multiplier at all; the <= 0.6 nodes live in the low group only.
     The condition has to be anchored: the regex engine searches, so an
     unanchored lookahead would re-match later in the name and let the
     excluded node back in.
  3. "🚀 手动选择" no longer references "🐢 低倍率节点", which would otherwise
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
# Anchored exclusion for every other group: no <= 0.6 multiplier in the name.
EXCLUDE = r"^(?!.*" + LOW + ")"

GROUP_PREFIX = f"custom_proxy_group={GROUP}`"
SELECT_PREFIX = f"custom_proxy_group={SELECT}`"
PATCHED_GROUP = (
    GROUP_PREFIX + "fallback`" + LOW + "`[]" + SELECT
    + "`https://www.gstatic.com/generate_204`300,,50"
)


def patch_group_line(line: str) -> str:
    """Rebuild one custom_proxy_group line with the local rules applied."""
    if line.startswith(GROUP_PREFIX):
        return PATCHED_GROUP
    if line.startswith(SELECT_PREFIX):
        line = line.replace(f"`[]{GROUP}`", "`")
    parts = line.split("`")
    for i in range(2, len(parts)):
        entry = parts[i]
        if entry.startswith("http://") or entry.startswith("https://"):
            break  # health-check url and the remaining params stay untouched
        if not entry or entry.startswith("[]") or entry.startswith(EXCLUDE):
            continue
        # Keep the upstream search semantics (patterns such as "港" match
        # mid-name) while anchoring only the exclusion at the start.
        parts[i] = EXCLUDE + ".*?(?:" + entry + ")"
    return "`".join(parts)


def build(text: str) -> str:
    out: list[str] = []
    hit_group = hit_select = False
    for line in text.split("\n"):
        if line.startswith("custom_proxy_group="):
            hit_group = hit_group or line.startswith(GROUP_PREFIX)
            hit_select = hit_select or line.startswith(SELECT_PREFIX)
            line = patch_group_line(line)
        out.append(line)
    if not hit_group or not hit_select:
        sys.exit(
            "upstream changed: expected group line not found "
            f"(group={hit_group}, select={hit_select})"
        )
    result = "\n".join(out)
    if PATCHED_GROUP not in result:
        sys.exit("self-check failed: patched group line missing")
    if EXCLUDE + ".*?(?:" not in result:
        sys.exit("self-check failed: exclusion missing from select groups")
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
    print(f"written {OUT} ({len(result.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
