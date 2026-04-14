# Phase 14: Stress Test & Beta Sign-off — Context

**Created:** 2026-04-14
**Mode:** Auto (recommended defaults)

## Phase Goal (from ROADMAP)

Team biết chính xác ngưỡng CCU tối đa của hệ thống và có bằng chứng hệ thống sẵn sàng cho Beta 1 Hà Nội.

## Decisions

### 1. Load Testing Tool

**Decision:** Locust (Python-native, matches stack)
**Rationale:** Project is Python/Flask. Locust integrates naturally, supports distributed mode, and produces HTML reports. Already recommended in STACK.md.

### 2. Test Target

**Decision:** Test against production Vercel URL (`https://mindguard-five.vercel.app`)
**Rationale:** Beta 1 will run on Vercel serverless. Testing locally would not reflect real serverless cold starts, NeonDB latency from sin1 region, or Vercel's concurrency model. Must test the real production path.

### 3. Load Profile & CCU Targets

**Decision:** Ramp from 0 → 100 CCU over 5 minutes, hold for 3 minutes, then ramp to 200 CCU.
**Rationale:** Vercel hobby tier has concurrency limits. 10M potential users in Hà Nội ≠ 10M CCU — realistic Beta 1 traffic is 50-200 CCU. Start conservative, find the actual breaking point.

**Ramp pattern:**

- Stage 1: 0 → 50 users over 2 min (baseline)
- Stage 2: 50 → 100 users over 3 min (moderate)
- Stage 3: Hold 100 users for 3 min (sustained load)
- Stage 4: 100 → 200 users over 2 min (stress)

### 4. User Behavior Mix (Task Weights)

**Decision:** Weighted scenario reflecting real Beta 1 usage:

| Task | Weight | Endpoint(s) | Rationale |
|------|--------|-------------|-----------|
| Browse homepage | 30% | GET / | Highest traffic page |
| View leaderboard | 10% | GET /leaderboard | Popular public page |
| Quiz flow | 20% | GET /quiz → GET /quiz/step/0 → POST /quiz/step/0 | Core feature |
| Report scammer | 10% | GET /scammer/report → POST /scammer/report | Core feature |
| Chatbot (send) | 15% | POST /chatbot/send | Most expensive endpoint (AI call) |
| Library browse | 10% | GET /library | Read-heavy |
| Public API check | 5% | GET /api/v1/check?q=test | API integration |

### 5. Success Criteria Thresholds

**Decision:**

- **P50 latency:** < 500ms for read endpoints, < 2s for AI endpoints
- **P95 latency:** < 2s for read endpoints, < 8s for AI endpoints (Vercel timeout)
- **Error rate threshold:** 5% (above this = system degraded)
- **Minimum stable CCU for Beta:** 50 (conservative for controlled Beta)

### 6. Authentication Handling in Tests

**Decision:** Mix of authenticated and unauthenticated flows.

- Homepage, leaderboard, library, public API → no auth needed
- Quiz, chatbot, report → create test account on setup, use session cookie
- Admin routes → excluded from stress test (not user-facing)

### 7. Rate Limiting Awareness

**Decision:** Respect rate limits in test design — don't flood endpoints beyond their configured limits per-IP. Use realistic think times (1-5s between requests). The goal is to test system capacity under realistic load, not to test rate limiter bypass.

**Current limits to respect:**

- Chatbot endpoints: 10-20/min per user
- Auth endpoints: 5-10/min per user
- Public API: 30-60/min per user
- Global: 200/min per IP

### 8. Report Output

**Decision:** Generate:

1. Locust HTML report (auto-generated)
2. Markdown summary in `.planning/phases/14-stress-test-beta-signoff/` with CCU threshold, P50/P95, failure points
3. Beta sign-off checklist (17 requirements verification)

## Code Context

### Infrastructure

- **Vercel:** Single region `sin1`, Python runtime, 120s timeout, 1024MB memory
- **Database:** NeonDB PostgreSQL via pooler endpoint (connection pool NOT configured in SQLAlchemy — uses defaults)
- **Rate limiter:** Flask-Limiter with `get_remote_address`, 200/min global default

### Key Risks

- NeonDB connection exhaustion — no pool_size configured, serverless cold starts create new connections
- Vercel cold start latency may spike P95 on first requests
- AI chatbot calls to OpenRouter are the slowest endpoint (potential 8s timeout)
- Rate limiter may reject load test requests if think time too low

## Deferred Ideas

(None — this is the final phase)

## Next Step

→ Plan Phase 14 (`/gsd-plan-phase 14`)
