# Stress Test Report — MindGuard v1.2 Beta 1

**Date:** 2026-04-14
**Tool:** Locust 2.43.4 (headless mode)
**Target:** `https://mindguard-five.vercel.app` (Vercel, sin1 region)
**Test file:** `tests/stress/locustfile.py`

---

## Executive Summary

MindGuard production on Vercel **handles 50 CCU comfortably** (3.37% error rate, all rate-limiter 429s — zero server failures). At 200 CCU the aggregate error rate rises to 19.5%, but **100% of errors are HTTP 429 (Too Many Requests)** from Flask-Limiter — the application server, Vercel runtime, and NeonDB never returned a single 5xx error.

**Verdict: GO for Beta 1** with up to 50 concurrent users. The rate limiter is working as designed and is the only bottleneck.

---

## Stage 1: Baseline — 50 CCU, 3 minutes

| Metric | Value |
|--------|-------|
| Total requests | 2,404 |
| Failures | 81 (3.37%) |
| Throughput | 13.4 req/s |
| P50 response | 200ms |
| P95 response | 510ms |
| P99 response | 1,100ms |
| Error types | 100% HTTP 429 |
| 5xx errors | **0** |

### Per-Endpoint Breakdown (Stage 1)

| Endpoint | Requests | Failures | Fail % | P50 | P95 | P99 |
|----------|----------|----------|--------|-----|-----|-----|
| GET / | 671 | 75 (11.18%) | 11.2% | 240ms | 530ms | 1,100ms |
| GET /leaderboard | 351 | 1 (0.28%) | 0.3% | 310ms | 560ms | 860ms |
| GET /library | 370 | 0 (0.00%) | 0.0% | 130ms | 300ms | 450ms |
| GET /quiz | 230 | 0 (0.00%) | 0.0% | 200ms | 400ms | 660ms |
| GET /login | 115 | 2 (1.74%) | 1.7% | 98ms | 310ms | 450ms |
| GET /register | 118 | 0 (0.00%) | 0.0% | 99ms | 310ms | 730ms |
| GET /scammer/report | 222 | 0 (0.00%) | 0.0% | 120ms | 370ms | 610ms |
| GET /api/v1/stats | 110 | 2 (1.82%) | 1.8% | 95ms | 150ms | 290ms |
| GET /api/v1/check | 107 | 1 (0.93%) | 0.9% | 92ms | 150ms | 220ms |

**Stage 1 Verdict:** ✅ PASS — Error rate 3.37% < 5% threshold. All latencies within criteria.

---

## Stage 2: Stress — 200 CCU, 5 minutes

| Metric | Value |
|--------|-------|
| Total requests | 15,845 |
| Failures | 3,089 (19.5%) |
| Throughput | 52.9 req/s |
| P50 response | 140ms |
| P95 response | 500ms |
| P99 response | 1,000ms |
| Error types | 100% HTTP 429 |
| 5xx errors | **0** |

### Per-Endpoint Breakdown (Stage 2)

| Endpoint | Requests | Failures | Fail % | P50 | P95 | P99 |
|----------|----------|----------|--------|-----|-----|-----|
| GET / | 4,620 | 1,896 (41.04%) | 41.0% | 240ms | 550ms | 1,100ms |
| GET /leaderboard | 2,423 | 272 (11.23%) | 11.2% | 310ms | 570ms | 1,000ms |
| GET /library | 2,448 | 292 (11.93%) | 11.9% | 130ms | 310ms | 450ms |
| GET /quiz | 1,562 | 151 (9.67%) | 9.7% | 200ms | 420ms | 880ms |
| GET /login | 781 | 62 (7.94%) | 7.9% | 97ms | 310ms | 750ms |
| GET /register | 814 | 0 (0.00%) | 0.0% | 96ms | 320ms | 800ms |
| GET /scammer/report | 1,506 | 0 (0.00%) | 0.0% | 120ms | 370ms | 810ms |
| GET /api/v1/stats | 751 | 86 (11.45%) | 11.5% | 96ms | 160ms | 320ms |
| GET /api/v1/check | 740 | 328 (44.32%) | 44.3% | 91ms | 170ms | 330ms |

**Stage 2 Verdict:** ⚠️ DEGRADED — Error rate 19.5% > 5% threshold. However, all errors are 429 rate-limiter rejections. Server itself is healthy.

---

## Error Analysis

### Error Breakdown (Stage 2 — all errors)

| Error Type | Count | % of Total Errors |
|------------|-------|-------------------|
| 429 Too Many Requests (GET /) | 1,896 | 61.4% |
| 429 Rate limited (GET /api/v1/check) | 328 | 10.6% |
| 429 Library returned 429 | 292 | 9.5% |
| 429 Too Many Requests (GET /leaderboard) | 272 | 8.8% |
| 429 Too Many Requests (GET /quiz) | 151 | 4.9% |
| 429 Too Many Requests (GET /api/v1/stats) | 86 | 2.8% |
| 429 Too Many Requests (GET /login) | 62 | 2.0% |
| **5xx Server Errors** | **0** | **0%** |

**Key Finding:** The rate limiter (Flask-Limiter, 200 req/min global per IP) is doing exactly what it's supposed to do. The application never crashed, timed out, or returned server errors even under 4x the target Beta 1 load.

---

## Latency Analysis

### Response Time Percentiles (Stage 2)

| Percentile | GET / | /leaderboard | /library | /quiz | /login | /register | /scammer/report | /api/stats | /api/check |
|------------|-------|--------------|----------|-------|--------|-----------|-----------------|------------|------------|
| P50 | 240ms | 310ms | 130ms | 200ms | 97ms | 96ms | 120ms | 96ms | 91ms |
| P75 | 300ms | 360ms | 140ms | 220ms | 120ms | 120ms | 140ms | 100ms | 100ms |
| P95 | 550ms | 570ms | 310ms | 420ms | 310ms | 320ms | 370ms | 160ms | 170ms |
| P99 | 1,100ms | 1,000ms | 450ms | 880ms | 750ms | 800ms | 810ms | 320ms | 330ms |

**All read endpoints meet success criteria:**

- ✅ P50 < 500ms (highest: /leaderboard at 310ms)
- ✅ P95 < 2s (highest: /leaderboard at 570ms)

---

## Capacity Analysis

| CCU Level | Error Rate | Throughput | Status |
|-----------|-----------|------------|--------|
| 50 | 3.37% | 13.4 req/s | ✅ Healthy |
| 200 | 19.5% | 52.9 req/s | ⚠️ Rate-limited (no server errors) |

### Estimated Stable CCU Threshold

Based on the data, the system is **stable at 50 CCU** with all metrics green. Extrapolating from error rate growth:

- **50 CCU:** ~3.4% error rate → PASS
- **~70 CCU:** ~5% error rate (estimated threshold)
- **200 CCU:** ~19.5% error rate → Rate-limited but server healthy

The **real bottleneck is Flask-Limiter's 200 req/min global limit per IP**, not server capacity. Since all 200 simulated users share one IP (the load test machine), the rate limiter treats them as a single user. In production, 200 real users would have 200 different IPs, each getting their own 200 req/min budget.

### True Production Capacity (Adjusted)

In real-world Beta 1:

- Each user has their own IP → own rate limit budget (200 req/min each)
- Average user generates ~0.3 req/s (with 2-5s think time) = 18 req/min
- Rate limit headroom per user: 200/18 = 11x margin
- **Server handled 52.9 req/s at 200 CCU with zero 5xx** → app/DB capacity is not the bottleneck
- **Estimated true CCU capacity: 200+ users (from different IPs)**

---

## Recommendations

### For Beta 1 Launch (50 CCU target)

1. **No changes needed** — system handles 50 CCU with 3.37% error rate
2. Rate limiter provides automatic DDoS protection

### For Scaling Beyond 50 CCU

1. Consider per-user rate limiting (session-based) instead of per-IP
2. Add `pool_size` / `max_overflow` to SQLAlchemy config for NeonDB
3. Monitor cold start frequency on Vercel dashboard
4. Consider Vercel Pro tier for higher concurrency limits

### Not Recommended

- Removing or significantly relaxing rate limits — they're protecting the system
- Adding caching before understanding actual user patterns from Beta 1 telemetry

---

## Artifacts

| File | Description |
|------|-------------|
| `tests/stress/locustfile.py` | Load test definition |
| `tests/stress/report_stage1.html` | Stage 1 HTML report (50 CCU) |
| `tests/stress/report_stage2.html` | Stage 2 HTML report (200 CCU) |
