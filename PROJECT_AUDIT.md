# Project Feature and Test Audit

**Audit date:** 2026-10-29  
**Scope:** Tracked backend, frontend, tests, README, and CI configuration in this repository. This is a static implementation review plus the test/build commands recorded below; it is not a production deployment or external-service verification.

## Executive summary

The project has a functioning foundation for market data, technical-feature generation, prediction signals, material-based analysis, authentication primitives, and a Next.js user interface. There are also service implementations and API routes for backtesting, portfolio analysis, risk, sentiment, trading, and social features.

However, feature presence is not consistent with feature completion. Several phase-based API routers return fixed demonstration values and are registered before the more substantive API routes with overlapping paths. This means some callers can receive mock results instead of the corresponding service-backed results. Parts of the frontend also use local mock data, and there are documented placeholders in news and asset-yield code. The current tests establish useful offline coverage for core calculations and security utilities, but do not validate most UI flows, persistence, real broker integrations, external data sources, or end-to-end feature behavior.

## Verified test and build results

| Check | Result | Notes |
|---|---:|---|
| Python tests, `py -3.12 -m pytest -q` | **82 passed, 4 skipped** | The four root-level live API/cache checks are now explicitly opt-in with `RUN_LIVE_API_TESTS=1`; the offline suite passed. |
| Frontend production build, `npm run build` | **Passed** | Next.js 16.4.3 TypeScript checking, compilation, static page generation, and build traces completed. |
| Frontend lint, `npm run lint` | **Passed with 43 warnings** | Fixed the prior 37 errors. The `react-hooks/set-state-in-effect` rule remains enabled as a warning because this Pages Router app uses effects for async loading and external updates; other warnings remain visible. |
| Frontend automated tests | **Not present** | `frontend/package.json` defines build/lint scripts but no test script; no frontend test files were found in the repository inventory. |

The four live API/cache checks are skipped by default and can be run with a started API using `RUN_LIVE_API_TESTS=1`. They were not verified against a running service in this audit. The CI workflow runs `pytest tests/`, installs the npm workspace, runs frontend lint, then builds the frontend; the live API/cache module is not part of the CI test command.

## Feature implementation inventory

Status definitions: **Implemented** means there is a concrete implementation in the reviewed source; **Partial** means core code exists but behavior is incomplete, mock-backed, weakly verified, or not fully integrated; **Gap** means the claimed behavior is absent or only a placeholder in the reviewed scope.

| Feature area | Status | Audit findings |
|---|---|---|
| Market data and asset catalog | Partial | Data-provider, quote, historical-price, asset-library, cache, and WebSocket code exists. Real-time results depend on external providers/configuration, and the standalone cache checks require a running service. |
| Core prediction signals | Implemented (limited verification) | Feature building, candlestick detection, model/walk-forward evaluation, signal composition, and API signal/quote routes have offline test coverage. No evidence here establishes predictive performance on live or held-out market data. |
| Material/text analysis | Implemented | Text analysis, URL/PDF/CSV handling, and combined material/automatic signal behavior have meaningful unit/API tests in `tests/test_smoke.py`. |
| Authentication and security utilities | Partial | Password hashing, JWT helpers, input sanitization, rate-limiter utilities, API keys, and session utilities are implemented and covered by tests. Some phase routers have duplicate/demo handlers for API paths; the registered route behavior needs focused tests before treating all documented authentication behavior as active. |
| Admin and account management | Partial | Admin modules and API handlers exist, but broad role/access and persistence behavior is not covered by end-to-end tests in the reviewed suite. |
| Backtesting and strategy analysis | Partial | A substantive backtesting service exists and has tests for strategies, metrics, Monte Carlo, walk-forward, and optimization. Separately, phase-router `/api/v2/backtest/*` handlers return fixed sample results and overlap service-backed API routes. |
| News and sentiment | Partial | Yahoo Finance news is implemented via `yfinance` with Google/Bloomberg RSS supplements, and the news/sentiment routes plus advanced-sentiment adapter have offline tests. Social posts and Fear & Greed components remain mock-based. |
| Risk management and portfolio analytics | Partial | Service/API code exists, but phase-based handlers return constant demo metrics and recommendations. Real-data correctness and portfolio persistence are not demonstrated by the tests. |
| Orders, paper trading, and broker integration | Partial / Gap | UI components and backend service/routes exist. Several phase-router order/broker handlers return canned responses; no broker sandbox or live integration tests were found. Treat order execution as demonstration behavior until a real adapter and guarded integration tests are established. |
| Social trading and community | Partial / Gap | Strategy/social APIs and UI components are present. `frontend/components/Community.jsx` uses local mock forums, discussions, and messages rather than a persistent community API. |
| Frontend pages and dashboard | Partial | Landing, login/signup, dashboard, assets, asset detail, and admin pages build successfully. The dashboard renders feature components, but compilation is not a substitute for browser-flow tests or API-backed UX validation. |
| Prediction history and accuracy | Partial | History/accuracy code exists, but some APIs expose simulated accuracy values and batch history returns only the latest stored prediction rather than a multi-period history. |
| Asset earnings/APY | Gap | `get_apy_for_asset` in `app/routes/assets_library.py` is explicitly a placeholder and returns `None`. |
| Mobile application | Gap | Listed as a future item in README; no mobile application is present in the tracked project inventory. |

## High-priority implementation gaps

1. **Resolve confirmed route overlaps, but do not assume they explain the asset 500s.** `app/api/__init__.py` includes phase routers before declaring direct API handlers, and some phase routes overlap with service-backed handlers. However, the phase asset-library router is prefixed `/api/v2/assets`; the `/api/assets/categories` and `/api/assets/live-prices` handlers are direct routes in `app/api/__init__.py`, so reordering that router does not explain those specific errors. Inspect the Railway traceback/config and exercise these direct handlers before changing their implementation.
2. **Replace remaining demonstration responses in phase endpoints.** News and v2 sentiment phase routes now call real services. Fixed sample backtest, execution, portfolio, ensemble prediction, social, and broker responses remain and should be wired or clearly marked unavailable; do not report success for simulated trades or broker connections.
3. **Complete remaining provider integrations or expose honest availability.** Yahoo news and CoinGecko quotes/history are implemented with offline provider tests and explicit source/error states. Social and Fear & Greed providers still need real integrations; distinguish “no data” from successful analysis of empty data.
4. **Persist features advertised as user/community workflows.** Replace the Community component’s local mock forums and messages with authenticated API-backed storage. Confirm portfolio, alerts, strategy sharing/following, broker accounts, and trading history persist across restarts and are scoped to the correct user.
5. **Add end-to-end tests for real feature boundaries.** Cover authentication and role checks, route precedence, market-data fallback/cache, portfolio/risk calculations, alert lifecycle, paper trading, and broker sandbox workflows. Add frontend tests for login/signup, dashboard data loading, and major feature components.
6. **Make quality checks reproducible.** Fix the ESLint config/dependency compatibility, add lint to CI, and separate offline tests from integration checks that require a running API/Redis service. Report test failures and service prerequisites clearly.
7. **Reconcile documentation and configuration.** Review the README’s endpoint/feature claims and setup guidance against actual wired behavior. In particular, document which integrations are mock/demo-only and avoid presenting demo credentials as safe production defaults.

## Follow-up validation and changes

- Marked the root-level live API/cache test module as opt-in. Run it with `RUN_LIVE_API_TESTS=1` only after starting the API and configuring its cache dependencies.
- Updated `eslint-config-next` to the Next.js 16 version range and refreshed both npm lockfiles. Resolved the reported ESLint errors by hoisting component helpers, correcting deferred callback references, escaping JSX text, and deriving portfolio symbols from props. ESLint now exits successfully with warnings; `react-hooks/set-state-in-effect` remains enabled as a warning because the Pages Router UI uses effects for async loading and external updates.
- Upgraded Next.js to the patched 16.4.3 release on branch `copilot/next-security-upgrade`; the production build passes. No changes were committed.
- Next.js 16.4.3 does not expose `experimental.agentUpgrade` in its installed configuration types or package sources, so that requested option was not added to `next.config.ts`.
- `npm audit --omit=dev` still reports one high-severity production transitive advisory in `follow-redirects` 1.16.0. This separate dependency issue was not changed as part of the Next.js upgrade.
- Confirmed both direct asset endpoints are defined in `app/api/__init__.py`; the `/api/v2/assets` router prefix does not collide with `/api/assets/*`.
- Updated the project test instructions to explain how to opt into the live API checks.
- Updated `.github/workflows/test.yml` to run frontend lint in CI before the production build.
- Did not alter Railway variables. Railway logs are outside the local repository, so the production 500 cause remains unverified.

## Coverage limits and caveats

- The test count is the result of the full discovered suite at audit time, not a coverage percentage. No coverage command was run.
- Tests use synthetic data and mocked providers in places; passing tests do not establish predictive accuracy or financial suitability.
- The 4 root-level live API/cache checks were skipped by default during the follow-up verification; they were not run against a started server.
- The static review does not certify secrets, deployment environment, live provider availability, brokerage permissions, or production runtime behavior.
- `docs/` exists but did not appear in the tracked-file inventory, so the audit does not rely on untracked documentation.

## Evidence reviewed

- `README.md` feature, endpoint, setup, and roadmap claims.
- `app/api/__init__.py`, `app/routes/`, `app/services/`, `app/core/`, and frontend pages/components.
- `tests/test_smoke.py`, `tests/test_security.py`, `tests/test_backtesting.py`, `tests/test_advanced_sentiment.py`, and `test_redis_cache.py`.
- `.github/workflows/test.yml`, `pyproject.toml`, `requirements.txt`, and frontend package/lint configuration.
