# William Vu - ZKV Finance Group
# AI Trading Bot - Documentation

# This file explains how the human sentiment analysis Python library works (AI-Trading-Bot/src/human_sentiment_analysis.py)

from human_sentiment_analysis import SentimentAnalysis

data = SentimentAnalysis(openai_key = openai_key, newsapi_key = newsAPI_key)

analysis_dict = data.analyze('Tesla')

print('ANALYSIS:\n', analysis_dict['analysis'], '\n')

print('SENTIMENT:\n',analysis_dict['sentiment'], '\n')

print('RATING:\n',analysis_dict['rating'], '\n')


# OUTPUT:

"""
Getting keywords for article search...
Finished getting keywords (2.90 s)
Getting sources...
Finished getting sources (2.18 s)
Condensing sources...
This process may take a while
Finished condensing sources (87.75 s)
Analyzing sources...
Finished analyzing sources (3.79 s)


Sentiment Analysis Completed.
"""
