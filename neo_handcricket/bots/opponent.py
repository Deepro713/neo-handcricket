"""Opponent modelling for the bot (pure logic).

Hand cricket is a repeated simultaneous-move (matching-pennies) game over 0..6:
there is no optimal *pure* strategy, so depth comes from reading the human while
staying unpredictable. This module predicts the human's **next** pick by blending
three weak models and then balances exploitation against the mixed-strategy
equilibrium:

  - **frequency** — which numbers the human favours lately;
  - **Win-Stay-Lose-Shift** — humans repeat a number that just worked and switch
    after a bad ball (needs per-pick outcomes);
  - **bigram / sequence** — which number tends to follow the last one.

`predict_next` returns a probability distribution over the human's next pick.
`exploit_mix` blends it toward uniform by an epsilon (0 = exploit hard, 1 =
uniform / unexploitable). `invert` turns a "where they'll go" distribution into a
"where to go to avoid them" distribution (for the bot when batting).

All functions are pure and deterministic; no RNG. Tunables live in ``config``.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from ..config import (
    OPP_WEIGHT_FREQ,
    OPP_WEIGHT_NGRAM,
    OPP_WEIGHT_WSLS,
)

N = 7
_UNIFORM = [1.0 / N] * N


def _normalize(dist: list[float]) -> list[float]:
    s = sum(dist)
    if s <= 0:
        return list(_UNIFORM)
    return [x / s for x in dist]


def _freq_model(picks: list[int]) -> list[float]:
    """Add-half-smoothed frequency of recent picks."""
    counts = Counter(p for p in picks if 0 <= p < N)
    total = sum(counts.values())
    smooth = 0.5
    return _normalize([(counts.get(i, 0) + smooth) / (total + smooth * N) for i in range(N)])


def _ngram_model(picks: list[int]) -> list[float]:
    """Bigram predictor: what usually follows the most recent pick."""
    if len(picks) < 2:
        return list(_UNIFORM)
    trans: dict[int, Counter[int]] = defaultdict(Counter)
    for a, b in zip(picks, picks[1:], strict=False):
        if 0 <= a < N and 0 <= b < N:
            trans[a][b] += 1
    last = picks[-1]
    follow = trans.get(last)
    if not follow:
        return list(_UNIFORM)
    total = sum(follow.values())
    smooth = 0.25
    return _normalize([(follow.get(i, 0) + smooth) / (total + smooth * N) for i in range(N)])


def _wsls_model(picks: list[int], outcomes: list[int]) -> list[float] | None:
    """Win-Stay-Lose-Shift: after a rewarding pick (outcome > 0) predict the human
    *stays* on that number; after a poor one predict they *shift* away from it.

    ``outcomes[i]`` is the reward sign for ``picks[i]`` (>0 good, <=0 bad). Returns
    None when there is no usable outcome history.
    """
    if not picks or not outcomes:
        return None
    last = picks[-1]
    if not (0 <= last < N):
        return None
    last_reward = outcomes[-1]
    if last_reward > 0:
        # Stay: concentrate on the last pick, a little leakage elsewhere.
        dist = [0.1 / (N - 1)] * N
        dist[last] = 0.9
        return _normalize(dist)
    # Shift: spread away from the last pick.
    dist = [1.0] * N
    dist[last] = 0.0
    return _normalize(dist)


def predict_next(picks: list[int], outcomes: list[int] | None = None) -> list[float]:
    """Predict the human's next pick as a distribution over 0..6."""
    if not picks:
        return list(_UNIFORM)
    freq = _freq_model(picks)
    ngram = _ngram_model(picks)
    wsls = _wsls_model(picks, outcomes or [])

    blended = [OPP_WEIGHT_FREQ * freq[i] + OPP_WEIGHT_NGRAM * ngram[i] for i in range(N)]
    if wsls is not None:
        blended = [blended[i] + OPP_WEIGHT_WSLS * wsls[i] for i in range(N)]
    return _normalize(blended)


def exploit_mix(dist: list[float], epsilon: float) -> list[float]:
    """Blend an exploit distribution toward uniform by ``epsilon`` in [0, 1].

    0 = exploit fully; 1 = uniform (unexploitable mixed strategy).
    """
    e = max(0.0, min(1.0, epsilon))
    return _normalize([(1.0 - e) * p + e * (1.0 / N) for p in dist])


def invert(dist: list[float]) -> list[float]:
    """Turn a "where the opponent will go" distribution into a "where to go to
    avoid them" distribution (high where they're unlikely)."""
    inv = [max(0.0, 1.0 - p) for p in dist]
    return _normalize(inv)
