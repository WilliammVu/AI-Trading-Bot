# William Vu - ZKV Financial Group
# GNU AFFERO GENERAL PUBLIC LICENSE
# 2025

# AI Trading Bot: Candidate Selector module

# Objective:
# Out of a list of major tickers, choose 10 that 
# might be worth analyzing based on very basic indicators

import yfinance
import pandas as pd
import datetime

class Data:
    def __init__(self):
        # Parallel arrays
        self.tickers = []

        self.market_caps = []
        self.cum_dividend_payouts = []
        self.shares_outstanding = []
        self.volumes = []

        self.scores = []

class CandidateSelector:
    def __init__(self, num_of_stocks = None):
        # Total number of stock candidates to be returned
        self.num_of_stocks = num_of_stocks

        self.data = Data()

        self._initialize_tickers()
        self._setup_data()

    def get_candidates(self, num_of_stocks = 10):
        n = len(self.data.tickers)
        self.num_of_stocks = num_of_stocks
        if num_of_stocks > n:
            num_of_stocks = n

        self._calculate_scores()

        score_to_tickers = {}
        for i in range(n):
            if self.data.scores[i] not in score_to_tickers:
                score_to_tickers[self.data.scores[i]] = []
            score_to_tickers[self.data.scores[i]].append(self.data.tickers[i])
        
        ans = []
        cnt = 0
        cont = True
        for score in sorted(score_to_tickers.keys()):
            tickers = score_to_tickers[score]
            for ticker in tickers:
                ans.append(ticker)
                cnt += 1
                if cnt == self.num_of_stocks:
                    cont = False
                    break
            if not cont:
                break
        return ans

    def _initialize_tickers(self):
        self.data.tickers = [
        # Mega‑caps / FAANG+
        "NVDA",  #NVIDIA
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "GOOGL", # Alphabet Class A
        "AMZN",  # Amazon
        "META",  # Meta Platforms 
        "TSLA",  # Tesla
        "PLTR",  # Palantir

        # Diversified financials & conglomerates
        "JPM",   # JPMorgan Chase
        "V",     # Visa
        "MA",    # Mastercard
        "BAC",   # Bank of America
        "WFC",   # Wells Fargo

        # Health care & pharma
        "JNJ",   # Johnson & Johnson
        "LLY",   # Eli Lilly
        "UNH",   # UnitedHealth Group
        "PFE",   # Pfizer
        "MRK",   # Merck
        "ABBV",  # AbbVie
        "ABT",   # Abbott Laboratories

        # Consumer staples & discretionary
        "COST",  # Costco
        "WMT",   # Walmart
        "KO",    # Coca‑Cola
        "PEP",   # PepsiCo
        "MCD",   # McDonald's
        "DIS",   # Disney
        "NFLX",  # Netflix
        "HD",    # Home Depot
        "NKE",   # Nike

        # Energy & materials
        "CVX",   # Chevron

        # Industrials & transport
        "UPS",   # UPS
        "HON",   # Honeywell

        # Tech & semiconductors
        "IBM",   # IBM
        "RIVN",  # Rivian
        "INTC",  # Intel
        "AMD",   # AMD
        "CSCO",  # Cisco
        "ORCL",  # Oracle
        "CRM",   # Salesforce
        "ADBE",  # Adobe
        "TXN",   # Texas Instruments
        "AVGO",  # Broadcom
        "QCOM",  # Qualcomm
        "DHR",   # Danaher
        "MDT",   # Medtronic

        # Communication services
        "VZ",    # Verizon
        "T",     # AT&T
        "CMCSA" # Comcast
        ]

    def _setup_data(self):
        for ticker_str in self.data.tickers:
            ticker = yfinance.Ticker(ticker_str)

            # Fill self.data.market_caps
            try:
                info = ticker.info
                market_cap = info.get('marketCap', 0)
                self.data.market_caps.append(market_cap)
            except Exception as e:
                print(f'Failed getting market cap for {ticker_str}: {e}')
                self.data.market_caps.append(0)

            # Fill self.data.shares_outstanding
            try:
                shares = info.get('sharesOutstanding', 0)
                self.data.shares_outstanding.append(shares)
            except Exception as e:
                print(f'Failed getting shares outstanding for {ticker_str}: {e}')
                self.data.shares_outstanding.append(0)

            # Fill self.data.cum_dividend_payouts
            try:
                divs_series = ticker.dividends
                
                if not divs_series.empty:
                    cutoff = pd.Timestamp.now(tz='America/New_York') - pd.Timedelta(days=365)
                    recent_divs = divs_series[divs_series.index > cutoff]
                    
                    if not recent_divs.empty and shares > 0:
                        annual_div_per_share = recent_divs.sum()
                        total_payout = annual_div_per_share * shares
                        self.data.cum_dividend_payouts.append(total_payout)
                    else:
                        self.data.cum_dividend_payouts.append(0)
                else:
                    self.data.cum_dividend_payouts.append(0)
                    
            except Exception as e:
                print(f'Failed getting dividend data for {ticker_str}: {e}')
                self.data.cum_dividend_payouts.append(0)

            # Fill self.data.volumes
            try:
                hist = ticker.history(period='7d')
                
                if not hist.empty and 'Volume' in hist.columns:
                    total_volume = hist['Volume'].sum()
                    self.data.volumes.append(int(total_volume))
                else:
                    self.data.volumes.append(0)
                    
            except Exception as e:
                print(f'Failed getting volume data for {ticker_str}: {e}')
                self.data.volumes.append(0)

            import time
            time.sleep(0.1)

    def _calculate_scores(self):
        n = len(self.data.tickers)
        self.data.scores = [0] * n

        temp = self._rank_elements(self.data.market_caps)
        for j in range(n):
            self.data.scores[j] += temp[j]

        temp = self._rank_elements(self.data.cum_dividend_payouts)
        for j in range(n):
            self.data.scores[j] += temp[j]
            
        temp = self._rank_elements(self.data.volumes)
        for j in range(n):
            self.data.scores[j] += temp[j]
        
    def _rank_elements(self, array):
        # O(N log(N))
        hash_set = set(array)
        rev = sorted(hash_set, reverse = True)
        ranking_map = {}
        for i in range(len(rev)):
            ranking_map[rev[i]] = i+1
        ans = []
        for x in array:
            ans.append(ranking_map[x])
        return ans

    def debug_data(self):
        """Helper method to see the collected data"""
        for i, ticker in enumerate(self.data.tickers):
            print(f"{ticker}: MC={self.data.market_caps[i]:,}, "
                  f"Div=${self.data.cum_dividend_payouts[i]:,.0f}, "
                  f"Vol={self.data.volumes[i]:,}, "
                  f"Shares={self.data.shares_outstanding[i]:,}")

if __name__ == "__main__":
    selector = CandidateSelector()
    candidates = selector.get_candidates(10)
    print("Top 10 candidates:", candidates)
