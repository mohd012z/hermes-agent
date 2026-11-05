"""Deterministic two-sum evaluation; trusted candidate functions only."""
from __future__ import annotations
import random
from dataclasses import dataclass

@dataclass(frozen=True)
class Evaluation:
    passed: int
    failed: int
    seed: int

def reference(values: list[int], target: int):
    seen = {}
    for j, value in enumerate(values):
        i = seen.get(target - value)
        if i is not None:
            return (i, j)
        seen[value] = j
    return None

def evaluate(candidate, *, seed=20261105, trials=500):
    if not 0 <= trials <= 100000:
        raise ValueError("invalid trial count")
    rng = random.Random(seed)
    cases = [([],0),([3,3],6),([0,0],0),([-4,8,2],4),([1,2,3],100)]
    cases.extend(([rng.randint(-30,30) for _ in range(rng.randrange(35))],rng.randint(-60,60)) for _ in range(trials))
    passed = failed = 0
    for values, target in cases:
        possible = any(values[i]+values[j]==target for i in range(len(values)) for j in range(i+1,len(values)))
        try:
            answer = candidate(values.copy(), target)
            if answer is None:
                ok = not possible
            else:
                ok = (isinstance(answer,tuple) and len(answer)==2
                      and all(type(x) is int for x in answer)
                      and 0 <= answer[0] < answer[1] < len(values)
                      and values[answer[0]]+values[answer[1]]==target)
        except Exception:
            ok = False
        passed += bool(ok)
        failed += not ok
    return Evaluation(passed, failed, seed)
