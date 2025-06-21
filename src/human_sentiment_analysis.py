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
import time

# Find articles and social media posts

class Data:

    def __init__(self, *, stock_name: str, num_of_articles: int = 20):
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
        prompt = f"""The following is a collection of {self.num_of_articles} recent articles regarding {self.stock}.
        Based on the articles, output the following valid JSON with fields: analysis, sentiment, rating.
        The analysis JSON field should be a one-paragraph summary of the key ideas of the articles.
        The sentiment JSON field should strictly be "POSITIVE", "NEGATIVE", or "NEUTRAL".
        The rating JSON field should strictly be "BUY", "HOLD", or "SELL".

        IMPORTANT: Output a valid JSON string ONLY
        """

        for i in range(len(self.articles)):
            prompt += f'ARTICLE {i+1}:\n\n'
            prompt += self.articles[i]
            prompt += '\n\n'

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

        print('Getting sources...')
        start = time.time()
        self._get_sources()
        end = time.time()
        print(f'Finished getting sources ({end - start:.2f} s)')

        print('Condensing sources...')
        print('This process may take a couple minutes')
        start = time.time()
        self._condense_text()
        end = time.time()
        print(f'Finished condensing sources ({end - start:.2f} s)')

        print('Analyzing sources...')
        start = time.time()
        analysis = self._analyze()
        end = time.time()
        print(f'Finished analyzing sources ({end - start:.2f} s)\n\n')

        analysis_dict = json.loads(analysis)
        return analysis_dict


if __name__ == '__main__':
    print('to exit instead, enter \'exit\'')
    stock = input('Enter the stock for human sentiment analysis: ')
    if(stock != 'exit'):
        d1 = Data(stock_name = stock)
        analysis_dict = d1.analyze()

        print(f'Analysis:\n\n{analysis_dict["analysis"]}\n\n')
        print(f'Sentiment:\n\n{analysis_dict["sentiment"]}\n\n')
        print(f'Rating:\n\n{analysis_dict["rating"]}')
    print('\n\nFinished!')
