# William Vu - ZKV Financial Group
# GNU AFFERO GENERAL PUBLIC LICENSE
# 2025

# AI Trading Bot: Human Sentiment Analysis module

# Objective:
# Analyze the sentiment surrounding a particular stock
# of the user's choosing using EventRegistry and OpenAI.

from openai import OpenAI
import eventregistry as NewsAPI
import json, time, sys, datetime

# Subclass for SentimentAnalysis
class Article:

    def __init__(self, *, body, date):
        self.body = body
        self.date = date

class SentimentAnalysis:

    def __init__(self, *, num_of_articles:int = 20, openai_key, newsapi_key):
        # The current stock of interest
        self.stock_name:str = None

        #keywords regarding the stock used for searching articles
        self.keywords:list[str] = []

        # Article data to be passed to OpenAI
        self.articles:list[Article] = []

        # Number of articles to be extracted from NewsAPI, 20 by default
        self.num_of_articles:int = num_of_articles

        # API keys
        self.openai_key:str = openai_key
        self.newsapi_key:str = newsapi_key

    def analyze(self, stock_name) -> dict[str,str]:
        # Returns a [str,str] dict with the following keys:
        # 'analysis', 'sentiment', 'rating'
        # read self._analyze() for more info

        if type(stock_name) != str:
            sys.stderr.write('SentimentAnalysis.analyze(stock_name) Error: stock_name should be str')
            sys.exit(1)
        else:
            self.stock_name = stock_name
        
        # If n = self.num_of_articles, ensure n % 5 == 0 and n >= 5 and n <= 100

        n = self.num_of_articles

        while n % 5 != 0:
            n += 1
        if n > 100:
            n = 100
        elif n < 5:
            n = 5
        
        self.num_of_articles = n

        print('Getting keywords for article search...')
        start = time.time()
        self._get_keywords()
        end = time.time()
        print(f'Finished getting keywords ({end - start:.2f} s)')

        print('Getting sources...')
        start = time.time()
        self._get_sources()
        end = time.time()
        print(f'Finished getting sources ({end - start:.2f} s)')

        print('Condensing sources...')
        print('This process may take a while')
        start = time.time()
        self._condense_text()
        end = time.time()
        print(f'Finished condensing sources ({end - start:.2f} s)')

        print('Analyzing sources...')
        start = time.time()
        analysis = self._analyze()
        end = time.time()
        print(f'Finished analyzing sources ({end - start:.2f} s)')

        print('Sentiment Analysis Completed.\n')

        self._reset()

        analysis_dict = json.loads(analysis)
        return analysis_dict

    def _get_keywords(self):
        # Use OpenAI to get keywords that will be used in _get_sources

        try:
            client = OpenAI(api_key = self.openai_key)

            prompt = f"""You will receive a <ticker symbol>. 
            You must convert that <ticker symbol> into a valid json string with the following fields: name, long_name, ticker_symbol.

            The following are examples to guide your operations:
            Ex. 1: <ticker symbol> = Tesla -> name:Tesla, long_name: Tesla Inc, ticker_symbol:TSLA
            Ex. 2: <ticker symbol> = TSLA -> name:Tesla, long_name: Tesla Inc, ticker_symbol:TSLA
            Ex. 3: <ticker symbol> = NVIDIA -> name:NVIDIA, long_name:NVIDIA Corp, ticker_symbol:NVDA

            If you do not know the answer to any of these fields, leave them as NONE. for example: long_name:NONE

            The <ticker symbol> is: {self.stock_name}. Please output valid JSON based on the above directions.

            """

            keywords_json_str = client.chat.completions.create(
                    model="gpt-4.1",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                ).choices[0].message.content
            
            keywords_dict = json.loads(keywords_json_str)

            if keywords_dict['name'] != 'NONE':
                self.keywords.append(keywords_dict['name'])
            else:
                print('name not found')
            if keywords_dict['long_name'] != 'NONE':
                self.keywords.append(keywords_dict['long_name'])
            else:
                print('long name not found')
            if keywords_dict['ticker_symbol'] != 'NONE':
                self.keywords.append(keywords_dict['ticker_symbol'])
            else:
                print('ticker symbol not found')
            
            if len(self.keywords) == 0:
                print(f'Unable to find keywords. Will use {self.stock_name} for searches instead')
                self.keywords.append(self.stock_name)

        except Exception as e:
            print(f'SentimentAnalysis._get_keywords() OpenAI API call failed. \'{self.stock_name}\' used as only keyword')

    def _get_sources(self):
        # If n == self.num_of_articles, 
        # this function adds n stringified articles to self.articles

        er = NewsAPI.EventRegistry(self.newsapi_key, allowUseOfArchive = False)

        q = NewsAPI.QueryArticlesIter(
            keywords = NewsAPI.QueryItems.OR(self.keywords),
            sourceGroupUri = er.getSourceGroupUri('business top 100'),
            lang = 'eng'
        )

        # 20 query results
        for article in q.execQuery(er, sortBy='rel', sortByAsc=False, maxItems=self.num_of_articles):
            a = Article(body = article['body'], date = article['date'])
            self.articles.append(a)   

    def _condense_text(self):
        # Function: summarize each article in self.articles

        # Shorten the articles into 3 sentence summaries
        client = OpenAI(api_key = self.openai_key)

        instructions = f"""The following is a collection of 5 articles regarding {self.stock_name}.
        Summarize each article in about 3 sentences.
        You should output a valid JSON string with the fields: one, two, three, four, five.
        The one JSON field should be the ~3 sentence summary of the first article.
        The two JSON field should be the ~3 sentence summary of the second article.
        The three JSON field should be the ~3 sentence summary of the third article.
        The four JSON field should be the ~3 sentence summary of the fourth article.
        The five JSON field should be the ~3 sentence summary of the fifth article.

        DO NOT OUTPUT ANYTHING BESIDES THE VALID JSON STRING

        """
        start = time.time()

        for i in range(self.num_of_articles // 5):
            #if this process took too long, exit
            end = time.time()
            if end - start > 3600.0:
                sys.stderr.write('Could not condense articles. Terminating processes')
                sys.exit(1)

            prompt = instructions

            for j in range(5):
                prompt += f'\nARTICLE {j}:\n\n'
                prompt += self.articles[(i * 5) + j].body

            summaries = client.chat.completions.create(
                model="gpt-4.1",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system",
                    "content": "You are acting as a tool that summarizes articles in ~3 sentences"},
                    {"role": "user", "content": prompt}
                ]
            ).choices[0].message.content

            summaries_dict = json.loads(summaries)
            self.articles[(i * 5) + 0].body = summaries_dict['one']
            self.articles[(i * 5) + 1].body = summaries_dict['two']
            self.articles[(i * 5) + 2].body = summaries_dict['three']
            self.articles[(i * 5) + 3].body = summaries_dict['four']
            self.articles[(i * 5) + 4].body = summaries_dict['five']

    def _analyze(self) -> str:
        prompt = f"""The following is a collection of {self.num_of_articles} summaries of recent articles regarding {self.stock_name}.
        Note that some of the articles might be irrelevant to {self.stock_name}.
        Note that today's date is {datetime.date.today()}, so articles closest to this date are the most important to consider.
        Based on the articles, output the following valid JSON with fields: analysis, sentiment, rating.
        The analysis JSON field should be a one-paragraph summary of the key ideas of all the articles.
        The sentiment JSON field should strictly be "POSITIVE", "NEGATIVE", or "NEUTRAL".
        The rating JSON field should strictly be "BUY", "HOLD", or "SELL".

        Important Notes: 
        Output a valid JSON string ONLY
        You are analyzing every single article at once and producing one analysis, sentiment, rating JSON object

        """

        for i in range(len(self.articles)):
            prompt += f'ARTICLE {i+1} ({self.articles[i].date}):\n\n'
            prompt += self.articles[i].body
            prompt += '\n\n'

        client = OpenAI(api_key = self.openai_key)

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
    
    def _reset(self):
        stock_name = None
        self.keywords = []
        self.articles = []
    
    # Getters
    
    def get_num_of_articles(self):
        return self.num_of_articles
    
    def get_openai_key(self):
        return self.openai_key
    
    def get_newsapi_key(self):
        return self.newsapi_key
    
    # Setters

    def set_num_of_articles(self, num:int):
        if type(num) != int:
            print('Error: SentimentAnalysis.set_num_of_articles() requires int. Ignoring call')
        else:
            self.num_of_articles = num
    
    def set_openai_key(self, key:str):
        if type(key) != str:
            print('Error: SentimentAnalysis.set_openai_key() requires str. Ignoring call')
        else:
            self.openai_key = key

    def set_newsapi_key(self, key:str):
        if type(key) != str:
            print('Error: SentimentAnalysis.set_newsapi_key() requires str. Ignoring call')
        else:
            self.newsapi_key = key


if __name__ == '__main__':
    pass
