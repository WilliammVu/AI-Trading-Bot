# William Vu - ZKV Finance Group
# AI Trading Bot - Documentation

# This file explains how the human sentiment analysis Python library works (AI-Trading-Bot/src/human_sentiment_analysis.py)

# Overview
#   - This library offers tools to analyze the overall sentiment of a particular stock.
#   - It is designed such that you can repeatedly analyze stocks

# ***Python Tutorial***

# Make sure your Python file is in the same directory as the HSA module
from human_sentiment_analysis import SentimentAnalysis

# How SentimentAnalysis works: 
#   - Uses EventRegistry API to find relevant & recent articles about Tesla
#   - Uses OpenAI API to analyze the overall sentiment about Tesla stock based on those articles

# The SentimentAnalysis class contains all methods from this library
HSA1 = SentimentAnalysis(openai_key = '...', newsapi_key = '...')
# This way of initializing the object defaults the number of articles to 20 (which is what we recommend)

# You can also initialize the object to 
HSA2 = SentimentAnalysis(openai_key = '...', newsapi_key = '...', num_of_articles = 100)
# Note that it takes ~2 minutes to analyze with 20 articles, so it is not recommended to have a large number of articles

# You can change the num_of_articles at any time, but note that num_of_articles is always divisble by 5
# So if you change num_of_articles to 13, it will autocorrect to 10 the next time you analyze
HSA1.num_of_articles = 15

analysis_dict = HSA1.analyze('Tesla')
# SentimentAnalysis.analyze() returns a [str,str] dictionary
# analysis_dict key-value pairs:
# - analysis_dict['analysis'] returns a paragraph of the analysis
# - analysis_dict['sentiment'] returns 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'
# - analysis_dict['rating'] returns 'BUY', 'SELL', or 'HOLD'
