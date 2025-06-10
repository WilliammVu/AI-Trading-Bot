# William Vu - ZKV Financial Group
# GNU AFFERO GENERAL PUBLIC LICENSE
# 2025

# AI Trading Bot: Human Sentiment Analysis Function

# Objective:
# Analyze the sentiment surrounding a particular stock
# of the user's choosing

openai_key   = 'undisclosed'
deepseek_key = 'undisclosed'
newsAPI_key  = 'undisclosed'

from openai import OpenAI
import eventregistry as NewsAPI
import json

# Find articles and social media posts

class Data:

    def __init__(self, stock: str, num_of_articles: int = 20):
        # the current stock of interest
        self.stock = stock
        # article data to be passed to OpenAI
        self.articles:list[str] = []
        # number of articles to be extracte from NewsAPI, 20 by default
        self.num_of_articles = num_of_articles
        
    def _get_sources(self):
        er = NewsAPI.EventRegistry(newsAPI_key, allowUseOfArchive = False)

        q = NewsAPI.QueryArticlesIter(
            keywords = self.stock,
            sourceLocationUri = NewsAPI.QueryItems.OR([
                "http://en.wikipedia.org/wiki/United_Kingdom",
                "http://en.wikipedia.org/wiki/United_States",
                "http://en.wikipedia.org/wiki/Canada"]),
            ignoreSourceGroupUri="paywall/paywalled_sources",
            dataType= ["news", "pr"]
        )

        # 20 query results
        for article in q.execQuery(er, sortBy="date", sortByAsc=False, maxItems=self.num_of_articles):
            self.articles.append(article['body'])

    def _condense_text(self):
        # We use Deepseek as a cheap option
        # to shorten the articles and posts into 2-3 sentence summaries
        client = OpenAI(api_key = deepseek_key, base_url = 'https://api.deepseek.com')

        for i in range(len(self.articles)):
            response = client.chat.completions.create(
                        model    = 'deepseek-chat',
                        messages =
                        [
                            {'role': 'system', 'content': 'You are a helpful assistant that summarizes articles in 2-3 sentences.'},
                            {"role": 'user', 'content': f'Summarize this article in 2-3 sentences, and do not output anything besides the summary:\n\n{self.articles[i]}'}
                        ]
                      )
            self.articles[i] = response.choices[0].message.content

    def _analyze(self) -> str:
        prompt = f'The following is a collection of {self.num_of_articles} recent articles regarding {self.stock}.'
        prompt += '\nBased on the articles, output the following valid json with fields: analysis, sentiment, rating.'
        prompt += '\nThe analysis json field should be a one paragraph summary of the key ideas of the articles.'
        prompt += '\nThe sentiment json field should strictly be "POSITIVE", "NEGATIVE", or "NEUTRAL".'
        prompt += '\nThe rating json field should stricly be "BUY", "HOLD", or "SELL".\n\n'
        prompt += 'IMPORTANT: Output a valid json string ONLY\n\n'
        i = 1
        for article in self.articles:
            prompt += f'ARTICLE {i}:\n\n'
            prompt += article
            prompt += '\n\n'
            i += 1

        client = OpenAI(api_key = openai_key)

        analysis = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                "content": "You are a helpful and decisive financial market analyst."},
                {"role": "user", "content": prompt}
            ]
        ).choices[0].message.content

        return analysis
    
    def analyze(self) -> dict[str,str]:
        # This is the only publicly used function
        self._get_sources()
        self._condense_text()
        return self._analyze()


if __name__ == '__main__':
    stock = input('Enter the stock for human sentiment analysis: ')

    d1 = Data(stock)
    analysis = d1.analyze()
    analysis_dict = json.loads(analysis)

    print(f'Analysis:\n\n{analysis_dict["analysis"]}\n\n')
    print(f'Sentiment:\n\n{analysis_dict["sentiment"]}\n\n')
    print(f'Rating:\n\n{analysis_dict["rating"]}')
