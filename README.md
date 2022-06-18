# nlp-project

In this project you can find the following things:

0. Step_0 Retrieve tweets for brexit.ipynb
This notebook contains code to:
a. retrive tweets containing the word: brexit in 2014 | 2015 | 2016 .. | 2021 (only english tweets)
The data is stored in csv files and can be located in folder: KOL tweets (and also in the folder Roy_tweets_brexit)

b. retive tweets by given tweet-ids (we have data on about 5M tweets that are relevant to brexit with sentiment analysis label [Positive / Negative / Neutral] on each tweet).

+ The table with the tweet-ids and the sentiment (from the 5M tweets) is located in: data_folder/tweets_4_5M/all_tweetids_and_sentiment.csv

+ The exported tweets data are stored in:  tweets_by_tweet_ids/brexit_tweet_ids.csv


###########################################################
1.Step_1_Read_KOL_tweets.ipynb
This notebook contains code that export tweets of a list of Key Opinion Leaders in a specified time-frame.
The csv files of each KOL is located in the folder: KOL tweets

###########################################################
2. Step_2_filter_KOL_tweets.ipynb
This notebook contains code that reads all the csv files that are stored in the folder: KOL tweets (this folder includes all the tweets of the Key Opinion Leaders as well as all the tweets we exported in step 0 [the tweets from the different years - 2014 till 2021 that contains the word "brexit"]), and the code combines all those tweets into one big data frame. It performs some manipulatios on it.
Finally it saves this big dataframe in the following location:
data_folder/tweets_table_all.csv


### creating virtul environment for the project
pip3 install virtualenv
virtualenv nlp-brexit-env
source nlp-brexit-env/bin/activate
pip3 install -r requirements.txt
 
