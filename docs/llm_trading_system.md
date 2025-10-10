
# Building an LLM-Powered Algorithmic Trading System for MetaTrader

The most effective path to forex trading success combines MetaTrader's robust execution capabilities with Large Language Models' analytical power through radical decomposition—breaking every trading decision into atomic, AI-answerable questions. This approach transforms uncertain market analysis into **definitive, high-certainty micro-decisions** that aggregate into superior trading signals.

## Core philosophy: certainty through decomposition

Traditional trading systems fail because they ask AI to make complex, context-dependent decisions that inevitably produce hedged responses. **The breakthrough**: decompose every analysis into specific binary questions or categorical choices that an LLM can answer with 70%+ confidence. Instead of "Should I trade EUR/USD?", ask 100+ micro-questions: "Is RSI above 70?" "Did MACD cross signal line in last 3 periods?" "Is Fed policy stance hawkish based on latest statement?" Each answer is definitive. The ensemble becomes powerful.

Research demonstrates that hierarchical systems separating strategic decisions (LLM-driven) from tactical execution (algorithm-driven) consistently outperform monolithic approaches. MIT's Hierarchical Reinforced Trader achieved a **Sharpe ratio of 2.74** versus 2.27 for the S&P 500 in bullish markets, and remained positive (0.41) when the index collapsed to -0.83 in bearish 2022. The secret: strategic stock selection handled separately from execution optimization, each specialized and optimized independently.

## 30 questions LLMs can answer with high certainty

These questions leverage established economic principles, definitional knowledge, and historical patterns—domains where LLMs demonstrate 80%+ accuracy without speculation.

### Central bank policy interpretation (6 questions)

**Q1:** Based on the latest Federal Reserve statement, does the language indicate a hawkish or dovish monetary policy stance?
- High certainty because: Hawkish/dovish terminology has established indicators in central banking language

**Q2:** When a central bank raises interest rates, does this typically strengthen or weaken the domestic currency?
- High certainty because: Fundamental economic principle—higher rates attract capital flows

**Q3:** If the ECB statement emphasizes "inflation risks" and "data-dependent tightening," is this more hawkish or dovish?
- High certainty because: Specific terminology has documented meanings in monetary policy

**Q4:** What is the Federal Reserve's dual mandate, and which economic indicators do they prioritize for each mandate?
- High certainty because: Officially documented mandate (maximum employment, price stability)

**Q5:** When a central bank engages in quantitative easing (QE), does this typically increase or decrease money supply?
- High certainty because: Defined monetary policy mechanism

**Q6:** If Bank of England minutes show a 7-2 vote split favoring rate holds (with 2 voting for hikes), is this more hawkish or dovish than a unanimous vote?
- High certainty because: Voting patterns reveal policy direction and disagreement levels

### Economic data interpretation (7 questions)

**Q7:** If US CPI comes in higher than expected, does this typically increase or decrease the probability of a Federal Reserve rate hike?
- High certainty because: Direct relationship between inflation and monetary policy response

**Q8:** When Non-Farm Payrolls significantly exceeds expectations, does USD typically strengthen or weaken immediately following release?
- High certainty because: Established historical pattern and economic logic

**Q9:** Does a PMI reading above 50 indicate economic expansion or contraction?
- High certainty because: Definitional—50 is the neutral threshold by design

**Q10:** If a country's GDP growth is negative for two consecutive quarters, what is this condition called?
- High certainty because: Standard economic definition of recession

**Q11:** When retail sales data exceeds expectations, does this suggest stronger or weaker consumer demand?
- High certainty because: Direct measure of consumer spending

**Q12:** Does a trade surplus (exports > imports) typically support or weaken a country's currency?
- High certainty because: Fundamental relationship—surplus creates demand for domestic currency

**Q13:** If unemployment rate falls below the natural rate of unemployment, does this typically create upward or downward pressure on inflation?
- High certainty because: Established Phillips Curve relationship

### Currency correlations and relationships (6 questions)

**Q14:** Do EUR/USD and USD/CHF typically show positive or negative correlation?
- High certainty because: Historical data shows strong negative correlation (USD is counter currency in both)

**Q15:** Are AUD and NZD generally considered risk-on or risk-off currencies?
- High certainty because: Established classification as commodity currencies with risk-on characteristics

**Q16:** Do JPY and CHF strengthen or weaken during periods of market stress and risk-off sentiment?
- High certainty because: Documented safe-haven status for both currencies

**Q17:** Is AUD/USD positively or negatively correlated with commodity prices (especially metals)?
- High certainty because: Australia's export-dependent economy creates positive correlation

**Q18:** Do GBP/USD and EUR/USD typically move in the same direction or opposite directions?
- High certainty because: Strong positive correlation due to geographical proximity

**Q19:** When USD strengthens broadly, does the US Dollar Index (DXY) rise or fall?
- High certainty because: DXY measures USD strength—direct relationship

### Risk-on/risk-off dynamics (5 questions)

**Q20:** During risk-on periods, do investors typically prefer high-yielding currencies like AUD/NZD or safe-haven currencies like JPY/CHF?
- High certainty because: Definitional characteristic of risk appetite

**Q21:** Does gold typically strengthen or weaken during risk-off market conditions?
- High certainty because: Established safe-haven status

**Q22:** When equity markets rally strongly, is this considered a risk-on or risk-off environment?
- High certainty because: Definitional—equity rallies indicate risk appetite

**Q23:** If the VIX (volatility index) spikes significantly, does this indicate risk-on or risk-off sentiment?
- High certainty because: VIX is the "fear gauge"—rising VIX equals risk-off

**Q24:** During geopolitical crises, do emerging market currencies typically strengthen or weaken against major currencies?
- High certainty because: Historical pattern of capital flight to safety

### Interest rate differentials (3 questions)

**Q25:** If Country A has 5% interest rate and Country B has 1% interest rate, which currency would a carry trader typically borrow and which would they buy?
- High certainty because: Fundamental carry trade strategy—borrow low, lend high

**Q26:** When interest rate differentials between two countries widen in favor of one currency, does that currency typically strengthen or weaken?
- High certainty because: Capital flows to higher yields

**Q27:** If the Federal Reserve is hiking rates while Bank of Japan maintains near-zero rates, does this widening differential typically strengthen or weaken USD/JPY?
- High certainty because: Direct application of interest rate differential principle

### Market mechanisms (3 questions)

**Q28:** Does higher inflation typically strengthen or weaken a currency's purchasing power?
- High certainty because: Fundamental economic definition—inflation erodes purchasing power

**Q29:** When economic data is released "better than expected," does the related currency typically strengthen or weaken in immediate reaction?
- High certainty because: Market mechanism—positive surprises typically boost currency

**Q30:** If a country's central bank unexpectedly cuts interest rates, is the immediate market reaction typically currency appreciation or depreciation?
- High certainty because: Rate cuts signal easing, reducing yield advantage

## 30 technical indicators decomposed for AI analysis

Each indicator breaks into 8-10 specific, independently answerable questions. This transforms subjective technical analysis into objective pattern recognition.

### Momentum indicators

**1. Relative Strength Index (RSI)**  
Decomposition questions: Is RSI above 70 (overbought)? Below 30 (oversold)? Is RSI trending upward over last 3 periods? Is RSI diverging from price (price makes new high, RSI doesn't)? Did RSI cross above 50 in last 5 periods? Has RSI been above 70 for more than 5 consecutive periods? What's the RSI value change from 5 periods ago? Is RSI between 40-60 (neutral zone)?

**2. MACD (Moving Average Convergence Divergence)**  
Decomposition questions: Is MACD line above signal line (bullish)? Below (bearish)? Did MACD cross above signal in last 3 periods? Is histogram positive? Is histogram increasing? Has histogram been above zero for 5+ consecutive periods? Is MACD diverging from price? What's the angle/slope of MACD over last 5 periods? Is MACD above/below zero line? Is histogram widening or narrowing?

**3. Stochastic Oscillator**  
Decomposition questions: Is Stochastic above 80 (overbought)? Below 20 (oversold)? Did %K cross above %D line? Did %K cross below %D? Is %K trending upward? How many periods has Stochastic been in overbought zone? Is there bullish divergence (price lower low, Stochastic higher low)? Is %K within 40-60 range (neutral)? What's the distance between %K and %D?

**4. Williams %R**  
Decomposition questions: Is Williams %R above -20 (overbought)? Below -80 (oversold)? Did Williams cross above -50 (bullish momentum shift)? Below -50 (bearish)? Is Williams trending upward over last 3 periods? Has it been above -20 for 5+ periods? Is it diverging from price? Did it fail to reach -20 on recent rally (weakening momentum)?

**5. Commodity Channel Index (CCI)**  
Decomposition questions: Is CCI above +100 (overbought/strong uptrend)? Below -100 (oversold/strong downtrend)? Did CCI cross above zero? Below zero? Is CCI between -100 and +100 (normal range)? What's the CCI trend over last 5 periods? Is CCI above +200 (extreme overbought)? Is CCI diverging from price? How long has CCI been above +100?

**6. Rate of Change (ROC)**  
Decomposition questions: Is ROC above zero (positive momentum)? Below zero (negative momentum)? Did ROC cross above zero line? Is ROC value increasing? Is ROC above +10%? Below -10%? What's the ROC trend over last 3 periods? Is current ROC higher than 10 periods ago?

**7. Average Directional Index (ADX)**  
Decomposition questions: Is ADX above 25 (strong trend present)? Below 20 (weak trend/ranging)? Is ADX trending upward (trend strengthening)? Downward (weakening)? Is +DI above -DI (uptrend direction)? Is -DI above +DI (downtrend)? Did +DI cross above -DI recently? Is ADX above 40 (very strong trend)? Is ADX rising while above 25?

**8. Money Flow Index (MFI)**  
Decomposition questions: Is MFI above 80 (overbought)? Below 20 (oversold)? Is MFI trending upward? Did MFI cross above 50? Is there bearish divergence (price high, MFI lower high)? Is MFI in 40-60 neutral zone? Has MFI been declining for 5+ periods? What's the MFI momentum over last 3 periods?

### Volatility indicators

**9. Bollinger Bands**  
Decomposition questions: Is price touching upper band (potential overbought)? Touching lower band (potential oversold)? Is price above middle band (uptrend bias)? Below middle band (downtrend bias)? Are bands widening (increasing volatility)? Narrowing (decreasing volatility)? What's the distance between upper and lower bands? Did price break above upper band? Is price within 10% of upper band?

**10. Average True Range (ATR)**  
Decomposition questions: Is ATR increasing (rising volatility)? Decreasing (falling volatility)? Is current ATR above 20-period average? Is ATR at a 50-period high? At a 50-period low? What's the ATR change percentage from 10 periods ago? Is ATR above 1.5x its 50-period average (high volatility)? Has ATR been rising for 5+ consecutive periods?

**11. Keltner Channels**  
Decomposition questions: Is price above upper Keltner band (strong bullish pressure)? Below lower band (strong bearish pressure)? Is price above middle line? Are channels widening (increasing volatility)? Narrowing? Did price break out above upper channel? Is price consistently staying above middle line? What's the channel width relative to 20-period average?

**12. Donchian Channels**  
Decomposition questions: Did price break above upper Donchian band (bullish breakout)? Below lower band (bearish breakout)? Is price in upper half of channel? Lower half? Is price at the upper band? At the lower band? How wide is the channel relative to ATR? Has channel width been expanding?

**13. Chaikin Volatility**  
Decomposition questions: Is Chaikin Volatility increasing? Is it above zero (volatility expanding)? Below zero (contracting)? Did volatility cross above zero line? Is volatility at 50-period high? What's the rate of volatility change? Has volatility been increasing for 5+ periods?

### Trend-following indicators

**14. Simple Moving Average (SMA)**  
Decomposition questions: Is price above SMA (bullish)? Below SMA (bearish)? Did price cross above SMA in last 3 periods? Below? Is SMA sloping upward? Downward? What's the distance between price and SMA (percentage)? Is fast SMA (20) above slow SMA (50) (golden cross potential)? Are multiple SMAs aligned in order (bullish stack)?

**15. Exponential Moving Average (EMA)**  
Decomposition questions: Is price above EMA? Below? Did price cross above EMA recently? Is EMA trending upward? Is fast EMA (12) above slow EMA (26)? Did EMAs cross (bullish/bearish crossover)? What's the angle of EMA slope? How far is price from EMA (in ATR units)? Are multiple EMAs aligned in bullish order?

**16. Ichimoku Cloud**  
Decomposition questions: Is price above the cloud (bullish trend)? Below cloud (bearish)? Inside cloud (neutral/consolidation)? Is Tenkan-sen above Kijun-sen (bullish signal)? Did Tenkan-sen cross above Kijun-sen recently? Is cloud green (Senkou Span A > Span B, bullish cloud)? Red (bearish cloud)? Is Chikou Span above price from 26 periods ago? Is price approaching cloud edge (support/resistance test)? Is cloud thick or thin (strong/weak support)?

**17. Parabolic SAR**  
Decomposition questions: Are SAR dots below price (uptrend)? Above price (downtrend)? Did SAR flip from below to above price (trend reversal signal)? How many periods has SAR been below price? What's the distance from price to SAR (in ATR units)? Is SAR accelerating (dots spacing increasing)? Did price touch SAR dot?

**18. Supertrend**  
Decomposition questions: Is Supertrend indicator green (uptrend)? Red (downtrend)? Did Supertrend flip from red to green? Is price above Supertrend line? How many periods has trend been active? What's the distance from price to Supertrend line? Did Supertrend just give a buy signal?

**19. Moving Average Envelopes**  
Decomposition questions: Is price touching upper envelope? Lower envelope? Is price above center MA? Did price break above upper envelope? Is price reverting to center MA? Are envelopes widening? Is price in upper half of envelope?

**20. Zero Lag EMA (ZLEMA)**  
Decomposition questions: Is price above ZLEMA? Below? Did price cross above ZLEMA? Is ZLEMA trending upward? Is ZLEMA steeper than regular EMA? What's the divergence between ZLEMA and price?

### Volume-based indicators

**21. On-Balance Volume (OBV)**  
Decomposition questions: Is OBV rising (accumulation/buying pressure)? Falling (distribution/selling pressure)? Is OBV making higher highs with price? Is OBV diverging from price? Did OBV break above resistance level? Is OBV above its 50-period moving average? What's the OBV trend over last 10 periods? Is OBV confirming price breakout?

**22. Accumulation/Distribution (A/D)**  
Decomposition questions: Is A/D line rising (accumulation)? Falling (distribution)? Is A/D diverging from price? Did A/D break above its trend line? Is A/D making new highs with price? Is A/D above its moving average? What's the slope of A/D over last 5 periods?

**23. Volume Weighted Average Price (VWAP)**  
Decomposition questions: Is price above VWAP (above fair value)? Below VWAP (below fair value)? Did price cross above VWAP? How far is price from VWAP (percentage)? Is price consistently staying above VWAP? Did price bounce off VWAP? Is VWAP trending upward?

**24. Chaikin Money Flow (CMF)**  
Decomposition questions: Is CMF above zero (buying pressure)? Below zero (selling pressure)? Is CMF above 0.25 (strong buying)? Below -0.25 (strong selling)? Did CMF cross above zero line? Is CMF trending upward? Is CMF diverging from price? What's the CMF momentum over last 5 periods?

### Support/resistance indicators

**25. Pivot Points (Standard)**  
Decomposition questions: Is price above Pivot Point (bullish bias)? Below (bearish bias)? Did price reach R1 level? Did price bounce off S1 level? Is price between P and R1? Did price break above R2? Is price testing S1 support? How many resistance levels above current price? Did price fail to break R1 (rejection)?

**26. Fibonacci Retracement**  
Decomposition questions: Is price at 61.8% retracement level? Did price bounce off 38.2% level? Is price between 50% and 61.8% levels? Did price break below 78.6% level (trend failure)? Is price holding above 23.6% level? Which Fibonacci level is price closest to? Did price respect 50% retracement as support? Is price retracing from recent high/low?

**27. Fibonacci Pivot Points**  
Decomposition questions: Is price above Fibonacci Pivot Point? Did price reach R1 (38.2% level)? Did price reach R2 (61.8% level)? Is price testing S1 Fibonacci support? Did price break through R1? Is price between Pivot and R1? How many Fib resistance levels above price?

**28. Support/Resistance Zones**  
Decomposition questions: Is price at identified support zone? At resistance zone? Did price break above resistance? Did price bounce off support? Is price approaching resistance zone? How far is price from nearest support (ATR units)? Did price form higher low at support? Is resistance becoming support?

### Specialized indicators

**29. Awesome Oscillator**  
Decomposition questions: Is Awesome Oscillator above zero line? Below zero line? Did AO cross above zero (bullish signal)? Is AO histogram turning green (momentum shift)? Is AO making higher highs? Did AO form twin peaks pattern? Is AO in saucer pattern (three consecutive bars pattern)? Is AO increasing in value?

**30. Ease of Movement (EOM)**  
Decomposition questions: Is EOM above zero line? Below zero line? Did EOM cross above zero (bullish)? Below zero (bearish)? Is EOM value increasing? Is EOM at extreme high level? At extreme low level? What's the EOM trend over last 5 periods?
## 20 monthly economic indicators that move forex markets

These indicators provide the fundamental backbone for LLM analysis, each releasing on predictable schedules and creating measurable market reactions.

**1. Non-Farm Payrolls (NFP)** – First Friday monthly (US). Measures net job creation excluding farm/government sectors. Fed's dual mandate makes employment data critical for rate decisions. Strong NFP strengthens USD across all pairs (EUR/USD, GBP/USD, USD/JPY, AUD/USD).

**2. Consumer Price Index (CPI)** – Mid-month (multiple countries). Primary inflation measure. Central banks target 2% inflation. Higher CPI signals potential rate hikes, strengthening currency. Most impactful for USD, EUR, GBP, CAD, AUD pairs.

**3. Interest Rate Decisions** – 6-8 times yearly per central bank. Direct monetary policy control. Higher rates attract foreign capital and strengthen currency. Most market-moving event. Affects all pairs involving that central bank's currency.

**4. Gross Domestic Product (GDP)** – Quarterly with monthly/preliminary releases. Measures total economic output. Two consecutive negative quarters equals recession. Strong GDP strengthens major pairs (EUR/USD, GBP/USD, USD/JPY).

**5. Purchasing Managers' Index (PMI) – Manufacturing** – First business day monthly. Leading indicator of manufacturing health. Above 50 equals expansion; below 50 equals contraction. Impacts USD (ISM), EUR, GBP, JPY, CNY pairs.

**6. Purchasing Managers' Index (PMI) – Services** – First business day monthly. Measures service sector (60-70% of developed economies). More impactful than manufacturing for service-based economies. Key for USD, EUR, GBP pairs.

**7. Retail Sales** – Mid-month. Direct measure of consumer spending (60-70% of GDP). Leading indicator of economic health. Strong sales strengthen USD, EUR, GBP, CAD, AUD pairs.

**8. Unemployment Rate** – Monthly (typically with NFP for US). Key labor market health indicator. Below natural rate signals inflation pressure. Rising unemployment weakens currency; falling strengthens.

**9. Producer Price Index (PPI)** – Day before/after CPI. Measures wholesale price changes. Leading indicator for consumer inflation as producer costs pass to consumers. Primarily impacts USD, EUR pairs.

**10. Trade Balance** – Monthly. Difference between exports and imports. Trade surplus creates demand for domestic currency; deficit weakens it. Critical for export-heavy nations (AUD, NZD, CAD, CNY).

**11. Industrial Production** – Mid-month. Measures manufacturing, mining, utilities output. Indicates industrial health and capacity utilization. Most impactful for EUR (especially Germany), JPY, CNY pairs.

**12. Housing Starts / Building Permits** – Mid-month (primarily US). Leading indicator of economic activity. Housing sector drives significant employment and consumption. Key for USD/CAD, AUD/USD (housing-sensitive economies).

**13. Consumer Confidence Index** – End of month. Leading indicator of consumer spending. High confidence predicts increased spending and economic growth. Impacts USD, EUR pairs.

**14. Business Confidence / Sentiment Surveys** – Monthly (IFO Germany, Tankan Japan). Leading indicator of business investment and hiring. Predicts PMI and employment data. Specific to country: EUR (IFO), JPY (Tankan).

**15. Personal Consumption Expenditure (PCE)** – Last week of month (US). Fed's preferred inflation measure. Broader basket than CPI with consumer substitution adjustment. Critical for all USD pairs.

**16. Average Hourly Earnings** – Monthly (with NFP). Wage growth indicator directly tied to inflation. Rising wages increase spending and inflation pressure, potentially triggering rate hikes. Impacts all USD pairs.

**17. Durable Goods Orders** – Last week of month (US). Measures orders for long-lasting manufactured goods. Leading indicator of manufacturing activity and business investment. Affects USD pairs.

**18. Central Bank Meeting Minutes** – 2-3 weeks after rate decision. Reveals detailed discussion and voting patterns. Shows whether officials are hawkish (favor tightening) or dovish (favor easing). Impacts currency of releasing central bank.

**19. Factory Orders / Manufacturing Orders** – Monthly. Broad measure of demand for manufactured goods. Indicates future production levels and economic momentum. Affects USD, EUR, JPY pairs.

**20. Employment Cost Index (ECI)** – Quarterly with monthly variations. Comprehensive measure of labor costs including wages and benefits. Critical for Fed's inflation assessment. Impacts USD pairs.

## STL decomposition and 20 AI-answerable trend tasks

STL (Seasonal and Trend decomposition using Loess) transforms price data into three analyzable components: trend (long-term direction), seasonal (recurring patterns), and residual (noise). This robust, non-parametric method handles any periodicity, adapts to changing patterns, and resists outliers—perfect for volatile forex markets.

### STL technical mechanics

The algorithm uses **LOESS (Locally Estimated Scatterplot Smoothing)** through nested loops. The inner loop alternates between seasonal smoothing (detrending data, then smoothing each seasonal subseries) and trend smoothing (removing seasonal component, applying LOESS to extract trend). The outer loop adds robustness by assigning lower weights to observations with large residuals, ensuring occasional market shocks don't distort core components.

Key parameters: **period** (observations per seasonal cycle—252 for daily data with yearly seasonality), **seasonal window** (controls how quickly seasonal component can change, typically ≥7), **trend window** (usually ~1.5 × period/(1-1.5/seasonal)), and **robust** (enable outlier resistance).

### Trading applications for STL

**Trend following**: Use trend component for directional bias—buy when trend.diff() > 0, sell when negative. **Mean reversion**: Trade when residuals deviate significantly (z-score > 2 indicates overbought, < -2 oversold). **Seasonal trading**: Identify favorable seasonal periods by grouping seasonal component by month, trading in months with strong positive seasonal values. **Volatility timing**: Use residual variance for position sizing—divide base size by rolling volatility for risk parity. **Multi-component strategy**: Combine signals—require positive trend, favorable seasonal (above 70th percentile), and low residual (below 1 standard deviation) for entry.

For forex specifically, use period=24 for daily cycles in hourly data, period=5 for weekly cycles in daily data, period=21 for monthly cycles, period=252 for yearly cycles. Always set robust=True for forex markets due to frequent central bank interventions and flash crashes.

### 20 independent AI tasks for trend analysis

These tasks transform complex time series analysis into parallelizable, specific questions that AI agents can answer independently:

**Trend component analysis (Tasks 1-7)**

**Task 1**: Is the trend component in the last 20 periods showing a positive slope? (Output: Boolean Yes/No)

**Task 2**: Calculate the percentage change in the trend component over the last 50 periods. (Output: Numerical percentage)

**Task 3**: Has the trend component changed direction (local max/min) in the last 10 periods? (Output: Boolean + direction, e.g., "Yes, peak at period 5")

**Task 4**: What is the average rate of change of the trend component over the last 100 periods? (Output: Numerical slope value)

**Task 5**: Is the current trend component value above its 200-period moving average? (Output: Boolean)

**Task 6**: Classify the trend strength: weak (<1%), moderate (1-3%), or strong (>3%) based on recent slope. (Output: Category)

**Task 7**: Identify the longest consecutive period of positive/negative trend change in the data. (Output: Number of periods + direction)

**Seasonal component analysis (Tasks 8-12)**

**Task 8**: Has the amplitude of the seasonal component increased in the last 3 cycles compared to the previous 3? (Output: Boolean + percentage change)

**Task 9**: What is the average value of the seasonal component during period 1-5 of each cycle (e.g., week 1 of each month)? (Output: Numerical average)

**Task 10**: Is the current seasonal component value in the top 25% of all historical seasonal values? (Output: Boolean + percentile rank)

**Task 11**: Calculate the consistency ratio: correlation between current cycle's seasonal pattern and average seasonal pattern. (Output: Correlation coefficient 0-1)

**Task 12**: Detect anomalous seasonal behavior—are there cycles where seasonal component deviates >2 std from mean seasonal pattern? (Output: List of cycle numbers with anomalies)

**Residual component analysis (Tasks 13-16)**

**Task 13**: Is the variance of the residual component in the last 50 periods significantly higher than the previous 50? (Output: Boolean + F-statistic/p-value)

**Task 14**: Identify the 5 largest residual spikes (absolute value) in the entire series. (Output: List of periods and residual values)

**Task 15**: Calculate the autocorrelation of residuals at lag 1, 5, and 10. (Output: Three correlation coefficients)

**Task 16**: What percentage of residuals fall outside ±2 standard deviations? (Output: Percentage—normal distribution ~5%)

**Component interaction analysis (Tasks 17-20)**

**Task 17**: Is the seasonal component amplitude positively correlated with trend component level? (Output: Correlation coefficient + interpretation)

**Task 18**: Calculate the signal-to-noise ratio: variance(trend+seasonal) / variance(residual). (Output: Numerical ratio)

**Task 19**: What percentage of total variance is explained by: (a) trend, (b) seasonal, (c) residual? (Output: Three percentages summing to 100%)

**Task 20**: Compare current period's trend+seasonal composite to its 20-period moving average—is it overextended? (Output: Boolean + z-score)

### Alternative decomposition methods

**Empirical Mode Decomposition (EMD)** excels for high-frequency trading, extracting multi-scale oscillations through adaptive "sifting" that identifies Intrinsic Mode Functions (IMFs) without predefined basis functions. Each IMF represents different frequency/time scales. Use **EEMD (Ensemble EMD)** with added white noise for stability. Best for market regime detection where different IMFs capture different cycle frequencies.

**Wavelet Decomposition** provides excellent time-frequency localization through recursive filtering. High-pass filters extract detail coefficients (high frequency), low-pass filters extract approximation coefficients (low frequency). **Daubechies (db4, db8)** wavelets work well for financial data. Use **MODWT (Maximal Overlap DWT)** for shift-invariance. Ideal for market microstructure noise removal and multi-scale correlation analysis.
## Ensemble methods: combining 100+ signals into unified decisions

Research consistently shows ensemble approaches dramatically reduce variance while maintaining performance. The ACM ICAIF FinRL Contest demonstrated that ensemble standard deviation reached approximately **50% of individual agents**, while AlgoML's ensemble achieved 9.97% net profit with only -0.7% drawdown versus -3.4% for the best individual model—a 5x improvement in risk control.

### Voting systems for signal aggregation

**Majority voting** (simplest): Count signals for BUY/SELL/HOLD, execute the action receiving most votes. Effective when indicators have similar reliability. **Weighted voting**: Assign weights based on historical performance metrics (Sharpe ratio, win rate, profit factor). Recalculate weights periodically using rolling windows to adapt to regime changes. **Threshold voting**: Require supermajority (e.g., 60% agreement) for action; otherwise HOLD. Reduces false signals but may miss opportunities.

**Rank-based voting** (Borda count): Each indicator ranks assets 1-N, aggregate rankings to determine final order. Robust to outlier signals. **Confidence-weighted voting**: Indicators provide signal plus confidence score (0-100%); weight each vote by confidence. Enables nuanced aggregation where strong signals outweigh weak ones.

### Advanced ensemble architectures

**Stacking (meta-learning)**: Use first-level models (technical indicators, economic signals) to generate predictions. Feed predictions into second-level meta-model (neural network, gradient boosting) that learns optimal combination. Train meta-model on out-of-sample data to prevent overfitting. Achieves 15-25% performance improvement over simple voting in research studies.

**Dynamic agent selection**: Rather than combining all signals always, select subset based on current market regime. Use **Thompson Sampling** for exploration-exploitation balance—each indicator has beta-distributed success probability, sample from distributions to select active indicators. MSR-TSE using this approach achieved **49.7x profits versus buy-and-hold** with 8.85x Sortino ratio improvement.

**Hierarchical ensemble**: Strategic layer (LLM) interprets market conditions and selects appropriate tactical agents for current regime. MIT's Hierarchical Reinforced Trader uses **Proximal Policy Optimization (PPO)** for high-level stock selection (buy/sell/hold decisions) and **Deep Deterministic Policy Gradient (DDPG)** for optimal execution. Sharpe ratio reached 2.74 in bullish markets (vs 2.27 for S&P 500) and remained positive at 0.41 when market collapsed to -0.83 in bearish periods.

### Signal scaling and normalization

Before aggregation, normalize signals to common scale. Convert all indicators to **z-scores**: (value - mean) / std_dev. This equalizes influence regardless of original indicator range. Alternatively, map to **[0,1] range**: (value - min) / (max - min). For binary signals, ensure consistent encoding (1 = bullish, -1 = bearish, 0 = neutral).

Handle missing signals gracefully: ignore missing values in voting (reduce denominator), or forward-fill last valid signal, or use neutral signal (0). Never skip aggregation due to missing data.

### Practical implementation for 100+ indicators

Organize indicators into categories: **momentum** (RSI, MACD, Stochastic), **trend** (moving averages, Ichimoku, Parabolic SAR), **volatility** (Bollinger Bands, ATR, Keltner Channels), **volume** (OBV, MFI, VWAP), **fundamental** (LLM-analyzed economic data), **sentiment** (LLM-processed news), **time series** (STL components).

Assign category weights based on current market regime: trending markets weight trend indicators higher; ranging markets weight oscillators and support/resistance. Use **regime detection** via market state classifier (ADX for trend strength, ATR for volatility level).

For 100 binary signals, simple majority requires 51 votes. For weighted voting with normalized weights summing to 1.0, threshold at 0.6 for strong signals. Track individual indicator performance metrics over rolling 30/60/90-day windows; drop persistently underperforming indicators below Sharpe 0.5.

## Prompt engineering for definitive LLM financial answers

LLMs naturally hedge responses to be "helpful, harmless, and honest"—but trading requires decisive action. Research shows properly engineered prompts reduce hedging by **20%** and improve financial task accuracy by **20-30%**.

### Core principles that eliminate hedging

**Hyper-specificity defeats hedging**. Instead of "What do you think about Tesla stock?" use: "You are a momentum trader. Tesla is at $242. My criteria: Only buy if 50-day MA > 200-day MA AND RSI between 40-60 AND weekly volume >20M shares. Current data: 50-day MA $238, 200-day MA $225, RSI 52, weekly volume 25M. DECISION: [BUY or NO BUY]. If BUY, specify: Entry $X, Stop $Y, Target $Z."

**Constraint-based prompting** forces operation within defined boundaries. Use output format constraints ("Respond with only YES or NO"), length constraints ("Limit response to exactly 3 sentences"), decision constraints ("Choose one option from: [A, B, C]"), and confidence thresholds ("Only recommend if confidence >75%").

**Binary/categorical outputs** prevent hedging. Instead of open-ended questions, force selection: "Based on technical indicators [data], OUTPUT ONE EXACT RESPONSE: A) STRONG BUY - Enter full position now, B) WEAK BUY - Enter 25% position, C) HOLD - No action, D) WEAK SELL - Reduce 25%, E) STRONG SELL - Exit entire position. SELECTED OPTION: [Letter only]. JUSTIFICATION: [Maximum 40 words]."

### Claude API-specific optimization

**XML tags** (Claude's native format): Use `<role>`, `<task>`, `<data>`, `<constraints>`, `<output_format>` tags to structure prompts. Example: `<role>You are a CFO with 20 years experience</role> <task>Analyze quarterly statement and provide definitive assessment</task> <constraints>Provide exactly ONE recommendation: INVEST, DIVEST, or HOLD. Include confidence 0-100%. List exactly 3 key factors. No hedging language like "might", "could", "possibly"</constraints>`.

**Prefill Claude's response** to enforce format and reduce chattiness. In messages array, add assistant message with partial response: `{"role": "assistant", "content": "DECISION: "}`. This forces Claude to immediately provide the decision without preamble.

**System prompts** establish decisive persona: "You are a risk management specialist at a Fortune 500 bank. Your job is to make definitive credit decisions based on quantitative criteria. You never hedge. You always provide: 1) Clear YES/NO decision, 2) Numerical risk score (0-100), 3) Specific data points supporting decision. You do NOT use: 'it depends', 'consider', 'might', 'could be', 'possibly'."

**Temperature settings**: Use temperature=0.0 for maximum determinism in financial calculations and compliance tasks. Use temperature=0.3 for balanced analysis with minimal creativity in market analysis. Avoid higher temperatures—they introduce too much randomness.

### Production-ready prompt templates

**Trading signal template:**
```
<role>You are a quantitative trading algorithm making automated decisions</role>

<market_data>
Symbol: {{TICKER}}
Price: ${{PRICE}}
RSI_14: {{RSI}}
MACD: {{MACD}}
Volume vs 20-day avg: {{VOLUME_RATIO}}
50-day MA: ${{MA_50}}
200-day MA: ${{MA_200}}
</market_data>

<decision_logic>
IF price > 200-day MA AND RSI < 70 AND MACD bullish → BUY signal
IF price < 200-day MA AND RSI > 30 AND MACD bearish → SELL signal  
IF RSI > 70 OR RSI < 30 → HOLD (overbought/oversold)
ELSE → NO_TRADE
</decision_logic>

<required_output>
SIGNAL: [BUY/SELL/HOLD/NO_TRADE]
POSITION_SIZE: [% of portfolio, 0-10%]
ENTRY: $[specific price or "N/A"]
STOP: $[specific price or "N/A"]
TARGET: $[specific price or "N/A"]
</required_output>
```

**Economic analysis template:**
```
<role>You are a senior equity analyst at Goldman Sachs</role>

<data>
{{EARNINGS_REPORT}}
</data>

<analysis_framework>
Evaluate against:
1. EPS beat/miss vs consensus
2. Revenue growth vs guidance
3. Forward guidance vs street expectations
4. Margin trends (expand/contract)
5. Management tone on call
</analysis_framework>

<required_output>
RECOMMENDATION: [BUY/HOLD/SELL]
TARGET_PRICE: $[specific number]
PRICE_CHANGE_EXPECTED: [+/- X%]
TIMEFRAME: [X months]
CONFIDENCE: [0-100%]
CATALYST: [single most important factor]
RISK: [single biggest downside risk]
</required_output>

<constraints>
- No hedging language
- One clear recommendation only
- Specific price target required
- Confidence must be ≥60% or state INSUFFICIENT_DATA
</constraints>
```

**Risk assessment template:**
```
You are a Chief Risk Officer assessing portfolio position for regulatory compliance.

<position_details>
{{POSITION_DATA}}
</position_details>

<risk_thresholds>
- Value at Risk (VaR) limit: $5M
- Concentration limit: 10% of portfolio
- Liquidity requirement: Exit within 2 days
- Leverage limit: 2:1
</risk_thresholds>

Output in this exact format:
COMPLIANCE_STATUS: [PASS or FAIL]
VIOLATIONS: [list specific threshold breaches, or "NONE"]
ACTION_REQUIRED: [specific action or "NONE"]
URGENCY: [IMMEDIATE/24-HOURS/MONITOR]

If status is FAIL, specify exactly what to do to come into compliance.
```

### Few-shot examples establish decisiveness

Provide 3-5 examples showing exact decisiveness you want:

```
<example1>
COMPANY: TechCorp Q3 2023
DATA: Revenue $50M (+15% YoY), Net Margin 22%, Cash $30M
RATING: STRONG BUY
CONFIDENCE: 85%
REASON: Revenue growth exceeds sector average (10%) with improving margins
</example1>

<example2>
COMPANY: RetailCo Q2 2023
DATA: Revenue $80M (-5% YoY), Net Margin 8%, Cash $5M
RATING: SELL
CONFIDENCE: 78%
REASON: Declining revenue and thin cash position indicate liquidity risk
</example2>

Now analyze this company using same format:
[Insert new company data]
```
## MetaTrader integration architecture

MetaTrader provides robust execution infrastructure with multiple integration paths. The optimal approach depends on latency requirements, trading frequency, and system complexity.

### WebRequest method (recommended for LLM integration)

**Native MQL integration** using built-in WebRequest function for REST API calls. Supports GET, POST, PUT, DELETE. Requires URL whitelisting in Tools → Options → Expert Advisors → Add allowed URLs.

**Claude API integration** example in MQL5:
```mql5
string url = "https://api.anthropic.com/v1/messages";
string headers = "Content-Type: application/json\r\n"
                 "x-api-key: YOUR_KEY\r\n"
                 "anthropic-version: 2023-06-01\r\n";
string json = "{\"model\":\"claude-3-5-sonnet-20241022\",\"max_tokens\":1024,\"messages\":[{\"role\":\"user\",\"content\":\"Analyze EURUSD\"}]}";

char post[], result[];
StringToCharArray(json, post, 0, StringLen(json), CP_UTF8);
ArrayResize(post, ArraySize(post) - 1); // Remove null terminator

int res = WebRequest("POST", url, headers, 30000, post, result, headers);
```

**Rate limiting** critical for production. Implement token bucket algorithm:
```mql5
class TokenBucket {
private:
    int capacity, tokens, refillRate;
    datetime lastRefill;
public:
    TokenBucket(int cap, int rate) {
        capacity = cap; refillRate = rate;
        tokens = cap; lastRefill = TimeCurrent();
    }
    bool TryConsume(int count = 1) {
        Refill();
        if(tokens >= count) {
            tokens -= count;
            return true;
        }
        return false;
    }
    void Refill() {
        int elapsed = (int)(TimeCurrent() - lastRefill);
        if(elapsed > 0) {
            tokens = MathMin(capacity, tokens + (elapsed * refillRate));
            lastRefill = TimeCurrent();
        }
    }
};
```

**Error handling** with exponential backoff:
```mql5
int CallAPIWithRetry(string url, int maxRetries = 3) {
    char post[], result[];
    for(int attempt = 0; attempt < maxRetries; attempt++) {
        int res = WebRequest("GET", url, NULL, NULL, 5000, post, 0, result, headers);
        if(res >= 0) return res;
        
        int error = GetLastError();
        if(error == 4060) break; // Don't retry whitelist errors
        Sleep(1000 * MathPow(2, attempt)); // Exponential backoff
    }
    return -1;
}
```

### ZeroMQ for high-performance integration

**Sub-10ms latency** bidirectional communication ideal for Python/R/Java ML model integration. Use **dwx-zeromq-connector** (https://github.com/darwinex/dwx-zeromq-connector) for production-ready implementation.

**Architecture**: MQL Expert Advisor acts as ZeroMQ server, Python script as client. Python performs LLM analysis and complex calculations, sends trading signals to EA, receives execution confirmations.

**Use cases**: High-frequency strategies, complex ML models, real-time backtesting, multi-asset correlation analysis requiring sophisticated computation.

### Complete Expert Advisor structure

```mql5
#property strict

input double LotSize = 0.1;
input string API_URL = "https://api.example.com/signals";
input string API_KEY = "";
input int API_Interval = 300; // 5 minutes

RateLimiter limiter(60, 60); // 60 requests per 60 seconds

int OnInit() {
    EventSetTimer(API_Interval);
    return(INIT_SUCCEEDED);
}

void OnTimer() {
    if(limiter.CanMakeRequest()) {
        string signal = CallAPI();
        ParseAndExecute(signal);
        limiter.RecordRequest();
    }
}

string CallAPI() {
    // Collect market data
    string marketData = StringFormat(
        "{\"symbol\":\"%s\",\"price\":%.5f,\"rsi\":%.2f,\"macd\":%.5f}",
        _Symbol, Close[0], iRSI(_Symbol, 0, 14, PRICE_CLOSE, 0),
        iMACD(_Symbol, 0, 12, 26, 9, PRICE_CLOSE, MODE_MAIN, 0)
    );
    
    // Send to LLM for analysis
    string response = WebRequestAPI(API_URL, marketData);
    return response;
}

void ParseAndExecute(string response) {
    // Parse JSON response
    // Example: {"action":"BUY","confidence":0.85,"stop_loss":1.0850,"take_profit":1.0950}
    
    if(ParseAction(response) == "BUY" && ParseConfidence(response) > 0.7) {
        double stop = ParseStopLoss(response);
        double target = ParseTakeProfit(response);
        OrderSend(_Symbol, OP_BUY, LotSize, Ask, 3, stop, target);
    }
}
```

### Security best practices

**API key management**: Never hardcode keys. Use input variables or encrypted file storage. Implement key rotation procedures.

**Circuit breaker pattern** prevents runaway costs:
```mql5
class CircuitBreaker {
    int failures, threshold;
    datetime cooldownUntil;
public:
    bool IsOpen() {
        if(TimeCurrent() < cooldownUntil) return true;
        return false;
    }
    void RecordFailure() {
        failures++;
        if(failures >= threshold) {
            cooldownUntil = TimeCurrent() + 300; // 5 min cooldown
        }
    }
};
```

**Validation layers**: Validate all API responses before execution. Check for required fields, reasonable values, proper authentication. Implement position limits and maximum loss thresholds independent of LLM signals.

## Implementation roadmap: production system in 10 weeks

**Phase 1: Foundation (Weeks 1-2)** – Setup MT5 environment, configure WebRequest whitelist, test basic GET/POST requests, implement JSON parsing library (JAson.mqh), secure API key storage, establish logging infrastructure.

**Phase 2: Core Integration (Weeks 3-4)** – Build signal reception module, create trade execution logic with order management, implement position tracking and management, develop comprehensive logging system, add error handling and retry logic.

**Phase 3: Advanced Features (Weeks 5-6)** – Add rate limiting (token bucket), implement circuit breaker pattern, build risk management layer (position limits, max drawdown, exposure limits), create real-time monitoring dashboard, develop alert system for anomalies.

**Phase 4: AI Integration (Weeks 7-8)** – Design 30 technical indicator decomposition questions, create 30 LLM economic analysis questions, implement prompt templates for Claude API, build response parsing and validation, add STL time series decomposition module, develop ensemble voting system for 100+ signals.

**Phase 5: Production Deployment (Weeks 9-10)** – Comprehensive backtesting with event-driven timing, paper trading with live data feeds, security audit (API keys, rate limits, validation), performance optimization (reduce API calls, cache responses), gradual capital allocation starting at 1% of account, continuous monitoring with automated alerts, establish retraining procedures for model drift.

## Proven success patterns from quantitative firms

**JPMorgan Chase portfolio decomposition** achieved **80% problem size reduction** with 10x faster time-to-solution by applying Random Matrix Theory to separate signal from noise in correlation matrices, then using spectral clustering to group assets by community structure. Independent subproblem optimization followed by aggregation maintained solution quality within 5% of global optimum while enabling quantum computing compatibility.

**Citadel's organizational decomposition**: Researchers specialize deeply in specific problems (narrow expertise), collaborate across disciplines for integration (broad perspective), deploy quickly when edge identified (speed to market). Both systematic and discretionary strategies coexist. Culture emphasizes intellectual curiosity, competitive drive, and leveraging data in all forms.

**AlgoML ensemble system** combined DQN, A2C, PPO (reinforcement learning), CNN, CNN-BiLSTM, BiLSTM (deep learning), and GA-optimized Pullback strategy through majority voting. Result: 9.97% net profit with only -0.7% drawdown versus best individual model's -3.4% drawdown—a **5x improvement in risk control**.

**FinRL ensemble strategy** used rolling window selection based on Sharpe ratio to dynamically choose between PPO, A2C, DDPG agents every 3 months. Outperformed individual algorithms and min-variance portfolio across 2016-2020 including 2020 crash, demonstrating adaptability to regime changes through periodic model selection.

## Competition-winning divide-and-conquer strategies

**ACM ICAIF FinRL Contest 2023/2024** winners used ensemble methods (PPO, SAC, DDPG, Double DQN, Dueling DQN) with majority voting that reduced standard deviation to **~50% of individual agents**. GPU-accelerated massively parallel simulations enabled efficient rolling window training for non-stationarity.

**RSI2 ensemble strategy** applied RSI2 to 4 different ETFs, then traded SPY only when ≥2 strategies signaled active. This ensemble of signals outperformed individual strategies with higher Sharpe ratio and smoother equity curve while avoiding exposure to individual ETF idiosyncrasies. Practical benefit: smaller accounts capture multi-strategy information through single instrument.

**Hierarchical Pair Trading System** used two-level architecture—GAT (Graph Attention Networks) for pair selection in upper layer modeling complex asset relationships, A2C (Actor-Critic) for execution in lower layer. Novel closed-loop design: DRL trader pre-trained on traditional pairs, trader performance generates supervisory labels to train GAT selector, minimizing human intervention.

## Final synthesis: building your LLM trading system

The convergence of research points to a clear architecture: **hierarchical decomposition** where LLMs handle strategic reasoning (market regime, fundamental analysis, sentiment) while specialized algorithms handle tactical execution (entry/exit timing, position sizing, risk management). Each level optimizes independently, connected through feedback loops.

**Start with modular foundation**: Separate data pipeline, strategy logic, risk management, execution, and monitoring into distinct components with clear APIs. Use event-driven backtesting from day one to ensure realistic timing. Implement comprehensive logging and version control.

**Decompose relentlessly**: Break every decision into atomic questions answerable with 70%+ confidence. Design 30 economic interpretation questions, 30 technical indicator decompositions, 20 time series analysis tasks. Each component provides a binary vote or numerical score, nothing ambiguous.

**Ensemble everything**: Combine multiple technical indicators (momentum, trend, volatility, volume), fundamental signals (LLM-analyzed economic data), sentiment indicators (LLM-processed news), and time series components (STL trend/seasonal/residual). Use weighted voting with performance-based weight updates every 30 days. Require 60% supermajority for strong signals.

**Prompt engineering discipline**: Use XML tags for structure, prefill responses to enforce format, set temperature=0.0 for determinism, provide 3-5 few-shot examples showing decisiveness, explicitly prohibit hedging language, force binary/categorical outputs, require confidence scores with minimum thresholds.

**MetaTrader integration robustness**: Implement token bucket rate limiting (60 requests/minute), exponential backoff retry logic, circuit breaker pattern (5-minute cooldown after 3 failures), comprehensive validation (check all fields, reasonable values, authentication), position limits independent of LLM signals.

The research is unambiguous: **decomposition beats monoliths**, **ensembles beat individuals**, **hierarchies beat flat systems**, and **specificity beats generality**. Your LLM trading system succeeds not by asking AI to predict the future, but by asking it to answer 100+ specific, high-certainty micro-questions whose aggregate reveals trading edge.

Start small—implement one currency pair, 10 indicators, basic LLM sentiment analysis. Validate thoroughly with walk-forward testing across multiple market regimes. Scale gradually as performance validates approach. The divide-and-conquer philosophy isn't just architectural elegance—it's empirically proven to reduce variance, improve risk-adjusted returns, and create robust systems that survive regime changes.

Your competitive advantage emerges from making each task so specific, so bounded, so measurable that uncertainty vanishes. Where others ask "What will EUR/USD do?", you ask 100 questions like "Is the trend component above its 200-period MA?", "Did CPI exceed expectations?", "Is risk sentiment positive based on VIX?", "Are 3 of 5 momentum indicators bullish?" The aggregate of certainties defeats the uncertainty of complexity.
