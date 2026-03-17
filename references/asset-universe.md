# Asset Universe

## Scope Filtering

The user's `asset_scope` in `user-profile.json` determines which tickers are available for selection:

- `etf_only`: Only rows marked with scope `etf_only` (ETFs only)
- `etf_and_stocks`: Rows marked `etf_only` + `etf_and_stocks` (ETFs + major individual stocks)
- `broad`: All rows (ETFs + stocks + alternatives + individual bonds)

## US Equity

### ETFs (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| VOO | Vanguard S&P 500 ETF | US Large Cap Index | Core US equity exposure |
| SPY | SPDR S&P 500 ETF | US Large Cap Index | Most liquid S&P 500 ETF |
| QQQ | Invesco QQQ Trust | US Tech/Growth | Nasdaq-100 exposure |
| VTI | Vanguard Total Stock Market | US Total Market | Broadest US equity |
| IWM | iShares Russell 2000 | US Small Cap | Small-cap exposure |
| VIG | Vanguard Dividend Appreciation | US Dividend Growth | Quality dividend growers |
| SCHD | Schwab US Dividend Equity | US High Dividend | High yield dividend |
| XLK | Technology Select Sector SPDR | US Sector - Tech | Technology sector |
| XLF | Financial Select Sector SPDR | US Sector - Financials | Financial sector |
| XLE | Energy Select Sector SPDR | US Sector - Energy | Energy sector |
| XLV | Health Care Select Sector SPDR | US Sector - Healthcare | Healthcare sector |
| XLI | Industrial Select Sector SPDR | US Sector - Industrials | Industrial sector |

### Individual Stocks (scope: etf_and_stocks)

| Ticker | Name | Sector | Notes |
|--------|------|--------|-------|
| AAPL | Apple Inc. | Technology | Mega cap, consumer tech |
| MSFT | Microsoft Corp. | Technology | Mega cap, enterprise/cloud |
| GOOGL | Alphabet Inc. | Technology | Mega cap, advertising/cloud |
| AMZN | Amazon.com Inc. | Consumer/Tech | Mega cap, e-commerce/cloud |
| NVDA | NVIDIA Corp. | Technology | AI/semiconductor leader |
| META | Meta Platforms Inc. | Technology | Social media/metaverse |
| TSLA | Tesla Inc. | Consumer/Auto | EV/energy leader |
| BRK.B | Berkshire Hathaway B | Financials | Diversified conglomerate |
| JPM | JPMorgan Chase | Financials | Largest US bank |
| JNJ | Johnson & Johnson | Healthcare | Diversified healthcare |
| V | Visa Inc. | Financials | Payment network |
| PG | Procter & Gamble | Consumer Staples | Defensive consumer |

## KR Equity

### ETFs (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| KODEX 200 | KODEX 200 ETF | KR Large Cap Index | KOSPI 200 tracking |
| KODEX 코스닥150 | KODEX KOSDAQ 150 | KR Growth | KOSDAQ 150 tracking |
| TIGER 미국S&P500 | TIGER US S&P 500 | US Equity (KRW) | KRW-denominated US equity |
| KODEX 삼성그룹 | KODEX Samsung Group | KR Conglomerate | Samsung group exposure |
| TIGER 반도체 | TIGER Semiconductor | KR Sector - Semi | Korean semiconductor sector |
| KODEX 배당가치 | KODEX Dividend Value | KR Dividend | Korean high dividend |
| KODEX 2차전지산업 | KODEX Secondary Battery | KR Sector - Battery | Battery/EV supply chain |

### Individual Stocks (scope: etf_and_stocks)

| Ticker | Name | Sector | Notes |
|--------|------|--------|-------|
| 005930 | Samsung Electronics | Technology/Semi | Korea's largest company |
| 000660 | SK Hynix | Technology/Semi | Memory semiconductor |
| 035420 | NAVER Corp. | Internet/Platform | Korea's largest internet co |
| 035720 | Kakao Corp. | Internet/Platform | Messaging/fintech platform |
| 005380 | Hyundai Motor | Auto | Major Korean automaker |
| 373220 | LG Energy Solution | Battery | EV battery manufacturer |
| 068270 | Celltrion | Bio/Pharma | Biosimilar leader |
| 005490 | POSCO Holdings | Materials/Steel | Steel conglomerate |

## Bonds

### ETFs (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| AGG | iShares Core US Aggregate Bond | US Aggregate | Core US bond exposure |
| BND | Vanguard Total Bond Market | US Total Bond | Broad US bond market |
| TLT | iShares 20+ Year Treasury | US Long-Term Treasury | Duration/rate sensitivity |
| SHY | iShares 1-3 Year Treasury | US Short-Term Treasury | Low duration, defensive |
| IEF | iShares 7-10 Year Treasury | US Mid-Term Treasury | Intermediate duration |
| LQD | iShares Investment Grade Corp | US IG Corporate | Investment grade corporate |
| HYG | iShares High Yield Corporate | US HY Corporate | High yield (junk) bonds |
| TIP | iShares TIPS Bond | US Inflation-Protected | Inflation hedge |
| KODEX 국고채10년 | KODEX KR Treasury 10Y | KR Government Bond | Korean 10-year treasury |
| TIGER 단기채권 | TIGER Short-Term Bond | KR Short-Term Bond | Korean short-term bond |

## Alternatives (scope: broad)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| GLD | SPDR Gold Shares | Gold | Gold bullion exposure |
| IAU | iShares Gold Trust | Gold | Lower-cost gold ETF |
| SLV | iShares Silver Trust | Silver | Silver bullion exposure |
| VNQ | Vanguard Real Estate | US REITs | Real estate exposure |
| DBC | Invesco DB Commodity | Commodities | Broad commodity basket |
| PDBC | Invesco Optimum Yield Diversified | Commodities | Optimized commodity |
| KODEX 골드선물(H) | KODEX Gold Futures (H) | Gold (KRW) | KRW-denominated gold |

## Cash Equivalents (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| SHV | iShares Short Treasury Bond | US Ultra Short | Near-cash, minimal risk |
| BIL | SPDR Bloomberg 1-3M T-Bill | US T-Bill | Treasury bill proxy |
| SGOV | iShares 0-3 Month Treasury | US T-Bill | Ultra-short treasury |
| CMA 머니마켓 | CMA Money Market | KR Money Market | Korean money market |

## Selection Rules

1. Select 2–4 tickers per asset class
2. Prefer ETFs over individual stocks for diversification
3. For `etf_only` scope: use ETFs exclusively
4. For `etf_and_stocks`: mix ETFs and individual stocks based on sector tilt
5. For `broad`: include alternatives (gold, REITs, commodities) when environment supports it
6. Korean tickers used when user's `market_preference` includes KR or is "mixed"
7. Every selected holding must have a `rationale` tied to environment assessment
8. Every holding carries a `source_tag` from data collection
