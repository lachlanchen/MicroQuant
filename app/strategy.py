from __future__ import annotations

def sma(values: list[float], period: int) -> list[float]:
    out: list[float] = []
    s = 0.0
    for i, v in enumerate(values):
        s += v
        if i >= period:
            s -= values[i - period]
        if i + 1 >= period:
            out.append(s / period)
        else:
            out.append(float("nan"))
    return out


def crossover_strategy(closes: list[float], fast: int = 20, slow: int = 50) -> dict:
    if slow <= 1 or fast <= 1:
        return {"signal": "hold", "reason": "invalid_periods"}
    if len(closes) < slow + 2:
        return {"signal": "hold", "reason": "insufficient_data"}
    s_fast = sma(closes, fast)
    s_slow = sma(closes, slow)
    # Look at last two points
    a1, b1 = s_fast[-2], s_slow[-2]
    a2, b2 = s_fast[-1], s_slow[-1]
    if a1 <= b1 and a2 > b2:
        return {"signal": "buy", "reason": "fast_cross_up"}
    if a1 >= b1 and a2 < b2:
        return {"signal": "sell", "reason": "fast_cross_down"}
    return {"signal": "hold", "reason": "no_cross"}

