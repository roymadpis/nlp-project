# nlp-project
### Roy Madpis & Michael Kobaivanov
In this project we use the Brexit as a case study and use data related to it to perform several NLP tasks.

### Introduction:
Brexit was the withdrawal of the United Kingdom from the European Union on 31 January 2020. The UK is the only sovereign country to have left the EU. 

The Brexit issue occupied the british people from 1975, where the first referendum on leaving the European Union was conducted, this issue came back in 2016 where another referendum on leaving the European Union was conducted again. There is huge difference between those 2 referendum as the second one was conducted in the social media era where there are numerous of influencers, as known as "Key Opinion Leaders" (KOL), who are usually at the forefront of public opinion and followed by a massive number of users and influenced the public and convince it to vote for leaving/staying in the Eu.
It is quite known that some influencers, who want to be popular, "change their mind" and as they understand the mainstreem, and are in favour of the most popular agenda, this is known as populism. We wish to investigate if such a phenomena happened among the main Key Opinion Leaders in the Brexit issue.

The Brexit is a very interesting issue both because of its precedential characteristic and because of its huge impact.
Many studies have been done to investigate the Brexit, its origin, reasoning, impact, etc.
We will focus on several issues regarding Brexit and use NLP techniques for this research.

In order to do that we will do the following:

0. Step_0 Retrieve tweets for brexit.ipynb
This notebook contains code to:
a. retrive tweets containing the word: brexit in 2014 | 2015 | 2016 .. | 2021 (only english tweets)
The data is stored in csv files and can be located in folder: KOL tweets (and also in the folder Roy_tweets_brexit)

b. retive tweets by given tweet-ids (we have data on about 5M tweets that are relevant to brexit with sentiment analysis label [Positive / Negative / Neutral] on each tweet).

+ The table with the tweet-ids and the sentiment (from the 5M tweets) is located in: data_folder/tweets_4_5M/all_tweetids_and_sentiment.csv

+ The exported tweets data are stored in:  tweets_by_tweet_ids/brexit_tweet_ids.csv


###########################################################
1. Step_1_Read_KOL_tweets.ipynb
This notebook contains code that export tweets of a list of Key Opinion Leaders in a specified time-frame.
The csv files of each KOL is located in the folder: KOL tweets

###########################################################
2. Step_2_filter_KOL_tweets.ipynb
This notebook contains code that reads all the csv files that are stored in the folder: KOL tweets (this folder includes all the tweets of the Key Opinion Leaders as well as all the tweets we exported in step 0 [the tweets from the different years - 2014 till 2021 that contains the word "brexit"]), and the code combines all those tweets into one big data frame. It performs some manipulatios on it.
Finally it saves this big dataframe in the following location:
data_folder/tweets_table_all.csv

###########################################################
3. Step_3_Sentiment_Analysis.ipynb
In this notebook we import a sentiment analysis model from hugginface. this model was trained on ~124M tweets from Jan 2018 to Dec 2021. It is able to get a tweet as input and provide its predicted sentiment (0: Negative, 1:Neutral, 2:Positive).
We take this model and **retrain it**, how?? using the data from step 0: We take the tweets with the sentiment labels (as we explained before, we have data on ~4.5M tweets with sentiment labels, we have only the tweet ids and the sentiment so in order to use that data we need to export the text of the tweet from twitter using the given tweet id), we don't export all of them from twitter, in fact we have export 300K tweets. We use those tweets with labels of sentiment to fine-tune the model we imported from hugginface.

Then, after fine-tuning the sentiment model we save it in the location: Brexit_sentiment_model

We use this model in step 4 to provide sentiment labels

###########################################################
4. Step_4_Sentiment_labels.ipynb
In this notebook we:

a. read the data_folder/tweets_table_all.csv - this is a table with ~1M tweets, containing tweets of KOL ad tweets of brexit from 2014-2021. It is a table **without sentiment**

b. Import the fine-tuned sentiment model - from the location: Brexit_sentiment_model

c. We use the sentiment model to give sentiment-prediction-labels to the ~1M tweets (from part a.)
We save the labeled data frame in the following location:  data_folder/tweets_table_all_with_sentimet.csv 
We will use that table + the 300K tweets with labels in step 5

###########################################################
5. Step_5_visualizing_Word2Vec and Sentiment Analysis
In this notebook we use all the data we collected so far to collect insights regarding the Brexit issue.
1. Word2Vec model:
a. We split the ~1.3M tweets data (data_folder/tweets_table_all.csv) by the year the tweet was published, train a Word2Vec model for each year alone (thus have word2vec model that was trained on tweets from 2014 / model that was trained on tweets from 2015, etc) we also have one Word2Vec model that was trained on all the data.
b. Then we find the K most simiilar words to the referenced word: brexit (using the Word2Vec model) [This is performed for each year alone]
c. We apply TSNE on the vecotrs of the k most simmilar words
d. we visualize - lets see :
    + How the different most closed words to "Brexit" changed throught the years

2. Doc2Vec model
a. We trained Doc2Vec model and generate tags. The tags are the conversation ids, author ids and the tweet create date. We also tried the same model but using for tags only the year of the tweet.
b. We apply TSNE on the vecotrs of the k most simmilar words to the referenced word ("brexit")
c. we visualize - the 30 most similar words to "brexit" using all the years data

We can note that the performance of the Doc2Vec model is less impressive compared to the perfomrance of the original Word2Vec model

3. Using Sentiment Analysis - EDA
We would like to use the Predicted sentiment label (that we got using step 4) in order to drive some insights regarding: The Key Opinion leaders sentiment in each year, the changes in their sentiment, the overall sentiment and its change throught the years.


+ data_folder/tweets_table_all.csv - this is a table with ~1M tweets, containing tweets of KOL ad tweets of brexit from 2014-2021. It is a table **without sentiment**

+ data_folder/tweets_table_all_with_sentimet.csv -  this is a table with ~1M tweets, containing tweets of KOL ad tweets of brexit from 2014-2021. It is a table **With sentiment Prediction from the fine-tuned ugginface model**





## More Attached files:

#### Python file: Brexit_Package.py
This python file contains the Package we have built in order to deal with reading data from twitter, this package enables:

+ Given a list of tweet ids - retrieve the tweets + information on them and their authors
+ Given a list of Twitter users + timeframe - retrieve all the tweets they wrote in the given time-frame
+ Given a list of conversation ids retrieve data on all the people who like it
+ Given a list of conversation ids retrieve data on all its retweets
+ Given a list of conversation ids retrieve data on all its Quotes
+ Given a list of conversation ids retrieve data on all its comments
+ Given a tweet-id - get the URL of the tweet - so you can view it on Twitter
+ given a query - retrive all the tweets that correspond to that query
+ Filter function - given a directory with CSV files (containing tweets) filter on multiple criteria we define (and can be altered using the function’s parameters) 



### creating virtul environment for the project
pip3 install virtualenv
virtualenv nlp-brexit-env
source nlp-brexit-env/bin/activate
pip3 install -r requirements.txt
 
