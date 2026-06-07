#!/usr/bin/env bash
# Ship an issue-cluster: branch -> (implement) -> QA gate -> PR (Closes #..) -> merge -> tag + release.
#
#   scripts/ship-cluster.sh start mNN/<cluster>
#   ...implement + add tests...
#   scripts/ship-cluster.sh ship "M0NN: <title>" <issue#...>
set -euo pipefail

PY="${PY:-.venv/bin/python}"
cmd="${1:-}"; shift || true

run_gate() {
  echo "== QA gate: ruff + pytest + playtest =="
  "$PY" -m ruff check .
  "$PY" -m pytest -q
  "$PY" -m tools.playtest
  echo "== (mypy advisory) =="; "$PY" -m mypy neo_handcricket || true
}

case "$cmd" in
  start)
    slug="${1:?branch slug required, e.g. m1/scoring}"
    git checkout main && git pull --ff-only origin main
    git checkout -b "$slug"
    echo "on branch $slug — implement, then: scripts/ship-cluster.sh ship \"<title>\" <issue...>"
    ;;

  ship)
    title="${1:?PR title required}"; shift
    issues=("$@")
    [ "${#issues[@]}" -gt 0 ] || { echo "provide at least one issue number"; exit 1; }
    run_gate
    branch="$(git rev-parse --abbrev-ref HEAD)"
    [ "$branch" != "main" ] || { echo "refusing to ship from main"; exit 1; }
    git push -u origin "$branch"
    body="## Summary
${title}

## Issues
"
    for n in "${issues[@]}"; do body+="Closes #${n}
"; done
    gh pr create --title "$title" --body "$body" --base main --head "$branch" || true
    gh pr merge --auto --squash --delete-branch || echo "auto-merge pending; will direct-merge when mergeable"
    state=""
    for _ in $(seq 1 30); do
      state=$(gh pr view "$branch" --json state --jq '.state' 2>/dev/null || echo "")
      [ "$state" = "MERGED" ] && break
      m=$(gh pr view "$branch" --json mergeable --jq '.mergeable' 2>/dev/null || echo "")
      [ "$m" = "MERGEABLE" ] && gh pr merge "$branch" --squash --delete-branch >/dev/null 2>&1 || true
      sleep 2
    done
    [ "$state" = "MERGED" ] || { echo "PR not merged yet — finish merge manually."; exit 1; }
    git checkout main && git pull --ff-only origin main
    # Version: minor = milestone, patch = next free. M00N -> v0.N (N<10), M010 -> v1.0, ...
    mnum="$(printf '%s' "$branch" | sed -n 's#^m\([0-9][0-9]*\)/.*#\1#p')"
    case "$mnum" in
      1) minor="0.1";; 2) minor="0.2";; 3) minor="0.3";; 4) minor="0.4";; 5) minor="0.5";;
      6) minor="0.6";; 7) minor="0.7";; 8) minor="0.8";; 9) minor="0.9";; 10) minor="1.0";;
      11) minor="1.1";; 12) minor="1.2";; 13) minor="1.3";; 14) minor="1.4";; 15) minor="1.5";;
      16) minor="1.6";; 17) minor="1.7";; 18) minor="1.8";; 19) minor="1.9";; 20) minor="2.0";;
      *) minor="";;
    esac
    if [ -n "$minor" ]; then
      git fetch --tags -q || true
      last="$(git tag -l "v$minor.*" | sed "s/^v$minor\.//" | sort -n | tail -1)"
      if [ -z "$last" ]; then patch=0; else patch=$((last + 1)); fi
      ver="v$minor.$patch"
      git tag -a "$ver" -m "$title"
      git push origin "$ver"
      gh release create "$ver" --title "$ver — $title" --notes "Cluster \`$branch\`." || true
      echo "shipped $ver"
    else
      echo "milestone $mnum unmapped — extend the version map in scripts/ship-cluster.sh"
    fi
    ;;
  *) echo "usage: ship-cluster.sh start|ship"; exit 1;;
esac
