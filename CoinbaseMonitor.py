from twitterscraper import *
import datetime as dt 
import pandas as pd 
begin_date = dt.date(2021,4,6)
end_date = dt.date(2021,4,9)
print(begin_date)
lang = 'english'
user = '@CoinbasePro'
tweets = query_tweets_from_user(user='@CoinbasePro')
df = pd.DataFrame(t.__dict___ for t in tweets)
print(df)

