# MSA Market Intelligence — research architecture v0.1

Status: research-only specification. No order execution, live alerts, production deployment, or billing changes.

## Scope and ownership
- **msa-herme5-agent** (proposed rename of this repository): general agent runtime, task orchestration, bounded tools, approvals, persistence, reporting.
- **msa-market-intelligence** (proposed separate repository): market-data normalization, technical calculations, event studies, backtests, visualization.
- Primary instruments: XAUUSD and BTCUSD; contextual factors: USD index/proxies, US yields, scheduled economic releases, market sessions, liquidity and spread.
- Do not rename this repository until PR links, CI, external integrations, upstream remotes and Android clients have been audited.

## Data contracts
Each raw observation must carry: provider, instrument, provider_symbol, bid, ask, timestamp_utc, received_at_utc, source_sequence (if provided), and provenance. Never fabricate bid/ask or spread from midpoint-only candles.

Each completed candle must carry: instrument, timeframe_seconds, start_utc, end_utc, open, high, low, close, volume (with kind: tick/base/quote/unknown), source, aggregation_version, complete=true, and quality flags. A forming candle has complete=false and must never be used as a confirmed signal.

For spot XAUUSD and BTCUSD, distinguish provider-specific markets: broker quotes, exchange trades and composite indices are not interchangeable. Record market-hours policy, timezone, session alignment and missing intervals. All derived candles must use half-open buckets [start,end), with a documented UTC anchor and explicit broker-session adjustments where applicable.

## Candle lifecycle
1. Validate source timestamps, numerical values, ordering and duplicate identifiers.
2. Assign each observation to a deterministic interval; update forming O/H/L/C without rewriting finalized history.
3. Finalize only after a declared source watermark / closure policy; late data triggers a versioned correction event rather than silent mutation.
4. Aggregate higher timeframes only from validated lower-timeframe closed candles. If any required component is missing, mark aggregate incomplete.
5. Calculate indicators on completed candles only; expose provisional values separately with an explicit warning.
6. Reconcile source candles against independently retrieved provider candles where available.

## Research modules
- Technical: BBMA (BB bands, MA5/10 high/low, EMA50), candle morphology, volatility, swings, supply/demand, Fibonacci retracements/extensions, harmonic pattern candidates and invalidations.
- Indicator lab: inspect license and source, extract formula and input defaults from MQL4/MQL5/Pine Script, implement independently, and test numeric parity on identical candles. Never assert exact conversion for unavailable proprietary code.
- News: retain event identifier, scheduled/released timestamps, consensus, prior, revisions, actual, source URLs and source timestamps. Calculate normalized surprise only when units and historical volatility are comparable.
- Attribution: distinguish pre-event drift, announcement reaction, post-event continuation/reversal and unrelated technical movement; event windows are hypotheses, not proof of causality.
- Learning: point-in-time feature snapshots, purged walk-forward splits, out-of-sample scoring, calibration, drift detection, and reproducible evidence links.
- Forecasts: output horizon, scenario probabilities, calibrated closing-price intervals, expected adverse excursion, spread/slippage assumptions and invalidation conditions; abstain on poor-quality data.
- Telegram: generate annotated charts and source-backed reports in a local/staging preview. Sending is disabled by default and requires separate explicit approval.

## Test gates
- M1 -> M5 -> H1 -> D1 aggregation with interval boundaries, gaps, out-of-order events and daylight-saving/session changes.
- Closed-candle immutability and correction-version semantics.
- MQL/Pine reference fixture parity and anti-lookahead checks.
- News embargo/release timestamp leakage and revision handling.
- Spread, stale quotes, provider outages and BTC weekend vs gold closure.
- Walk-forward reproducibility, class imbalance, regime changes and probability calibration.
- Agent restart, duplicate jobs, SQLite lease fencing and bounded retries.
- Telegram chart rendering offline; no network delivery in tests.

## Research acceptance criteria
A milestone is VERIFIED only when code, independent test evidence and exact CI SHA exist. A statistical result is not a guaranteed trading outcome. Never claim a zero-loss signal or execute orders from research output.
