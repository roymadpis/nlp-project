


import requests
import os
import json
import pandas as pd
import numpy as np
import csv , datetime, unicodedata, time, tweeterid #dateutil.parserm,
import gensim
import openpyxl
import json

from os import path
from datetime import datetime
from collections import Counter
from inputimeout import inputimeout, TimeoutOccurred

class TwitterCrawler():
    """Summary of class here.

    You must define a TwitterCrawler instance to start crawling Twitter Data.
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, bearer_token: str):
        """Inits SampleClass with the academic bearer_token."""
        self.bearer_token = bearer_token
        os.environ['TOKEN'] = self.bearer_token
        self.headers = {"Authorization": "Bearer {}".format(self.bearer_token)}

    def auth():
     return os.getenv('TOKEN')

    # def create_headers(self):
    #     """ Creates a header for the Twitter API request,
    #      based on the Bearer Token

    #     Parameters
    #     ----------
    #     sound : str, optional
    #         The sound the animal makes (default is None)

    #     Raises
    #     ------
    #     NotImplementedError
    #         If no sound is set for the animal or passed in as a
    #         parameter.
    #     """

    #     headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
    #     return headers

    def __connect_to_endpoint(self, url: str, params: dict, next_token: str  = None,
     sleep_time:int = 3, num_of_trails = 10, verbose:bool = False, is_retweet = False):
        """
        ### connect_to_endpoint
        This Function enables concatinating the twitter endpoint url with the search parameters and search for the relevant information

        ### Arguemnts:
            - url: One of twitter endpoints URL
            - params: dict with the query params. The acceptable params can be found in twitter developer documentation
            - next_token: the token is a distinct hash key that categorizes search pages in twitter. In some of the endpoints calls, you get a token indicating the place you "stopped" in. If you wish to get data from that stopped point you can use that given token.
            - sleep_time: int, by default  = 3 seconds. If the function got an error from twitter, it sometimes because you tried retirve data too quickly (multiple calls whithin less than 1 second), so the function can activate the sleep command for a few seconds and right after that try calling twitter again.
            - num_of_trails: int, by default  = 10 tries. If the function got an error from twitter it will try waiting K seconds (K = sleep_time = 3) and it will do this N times (N = num_of_trails)
            - vebose: bool, by default  = False. If True then the function will print the status code it gets and will print when it goes sleeping
            - is_retweet: bool, by default  = False. For some of the endpoints there is a new name for "next_token" - "pagination_token". Example for this cases is the End point for retweets or quotes. So for all the endpoints that uses the "pagination_token", we need to pass the connect_to_endpoint function "True" in this arguement.
        """
        if is_retweet:
            params['pagination_token'] = next_token
        else:
            params['next_token'] = next_token   #params object received from create_url function

        for i in range(num_of_trails):

            if i > num_of_trails//2:
                print(f"Failed to connect {i} times, going to sleep for 15 minutes..")
                time.sleep(15*60) # sleep for 15 minutes

            response = requests.request("GET", url, headers = self.headers, params = params)
            if verbose: print(f"Trail #{i} Response Code: " + str(response.status_code))

            if response.status_code == 200: return response.json()

            if response.status_code == 429:
                if verbose: print(f"Try sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)

        raise Exception(response.status_code, response.text)

    # def __connect_to_endpoint(self, url: str, params: dict, next_token = None, verbose = True):
    #     """ Connect to Twitter API via a endpoint

    #     Parameters
    #     ----------
    #     sound : str, optional
    #         The sound the animal makes (default is None)

    #     Raises
    #     ------
    #     NotImplementedError
    #         If no sound is set for the animal or passed in as a
    #         parameter.
    #     """
    #     params['next_token'] = next_token   #params object received from create_url function
    #     response = requests.request("GET", url, headers = self.headers, params = params)
    #     if verbose == True:
    #         print("Endpoint Response Code: " + str(response.status_code))

    #     if response.status_code == 429:
    #         print(response.text)
    #         print("try sleeping for 2 seconds")
    #         time.sleep(2)
    #         return response.status_code

    #     if response.status_code != 200:
    #         raise Exception(response.status_code, response.text)
    #     return response.json()

    def get_url_by_tweet_id(tweet_id: str):
        """ Given tweet id - get the twitter url

        ### Parameters
        ------
        + tweet_id : str

        """
        return "https://twitter.com/anyuser/status/" + str(tweet_id)

    def search_by_tweet_id(self, tweet_id: str):
        """ ## search tweet by tweet-id

        + link to twitter-developer page regarding this capability:
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id

        ### App rate limit:
        900 requests per 15-minute window per each authenticated user


        ### Parameters
        ----------
        - tweet_id : str --> The twitter Id of the tweet you wish to get

        ### Classic Use cases
        When you have a twet id and you want to get all the available data on this tweet - the text, data about the author, tweet metrics, etc.
        """

        search_url = "https://api.twitter.com/2/tweets/:id"
        search_url = search_url.replace(":id", tweet_id)
        #change params based on the endpoint you are using
        query_params = {
                        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                        'next_token': {}}
        json_response = self.__connect_to_endpoint(url = search_url, params = query_params)
        return json_response

    def search_recent_by_keyword(self, keyword: str, start_date, end_date, max_results = 10):
        """ ## search tweets by query

This function enalbes look for tweets by providing start + end date and building a query.\n
You can see the full documentation on how to build a query (what to pass in the `keywork` argument) in the following link:\n
https://developer.twitter.com/en/docs/twitter-api/tweets/counts/integrate/build-a-query

+ link to twitter-developer page regarding this capability:\n
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

### App rate limit:
- App rate limit (OAuth 2.0 App Access Token): 300 requests per 15-minute window shared among all users of your app
- App rate limit (OAuth 2.0 App Access Token): 1 request per second shared among all users of your app

Parameters
----------
keyword : str
start_date = The start date is the date that from it the function will look and rerieve tweets.\nNote that the format of the start time should be: "2015-12-7T00:00:00Z"
end_date = The end date is the date that till it the function will look and rerieve tweets.\nNote that the format of the end time should be: "2021-12-7T00:00:00Z"

max_results = The max number of tweets to retrieve in a given call. Must be an integer between 10 to 500.

        """
        search_url = "https://api.twitter.com/2/tweets/search/all"
        #handling case where the user entered a max_result that is not between 10 and 500
        if max_results > 500:
            max_results = 500
            print('max_results can not be greater than 500, changed to 500')
        if max_results < 10:
            max_results = 10
            print('max_results can not be smaller than 10, changed to 10')

        #change params based on the endpoint you are using
        query_params = {'query': keyword,
                        'start_time': start_date,
                        'end_time': end_date,
                        'max_results': max_results,
                        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                        'next_token': {}}

        json_response = self.__connect_to_endpoint(url= search_url, params = query_params)
        return json_response

###self.__connect_to_endpoint2(self, search_url, query_params, next_token = next_token, verbose = False)

#################################################################################################################
    def __return_tweets_of_key_opinion_leader(self, query="", user_name=None,
                                        start_time = "2015-12-7T00:00:00Z",
                                        end_time = "2021-12-26T00:00:00Z",
                                        max_results = 10, evaluate_last_token = False,
                                        limit_amount_of_returned_tweets = 10000000,
                                       verbose_10 = False, dir_name = "key_opinion_leaders_tweets_tables_beta"):

        search_url = "https://api.twitter.com/2/tweets/search/all" #endpoint use to collect data from
        
        #handling case where the user entered a max_result that is not between 10 and 500
        if max_results > 500:
            max_results = 500
            print('max_results can not be greater than 500, changed to 500')
        if max_results < 10:
            max_results = 10
            print('max_results can not be smaller than 10, changed to 10')
        #creating a directory tat will contain the csv file + the log directory of the Key Opinion Leader
        import os.path
        try:
            os.mkdir(dir_name)
            print("creating directory", dir_name, "to insert all the tables of all the key opinion leaders")
        except:
            print("The dir", dir_name ,"already exist")

        if user_name is not None:
            query = str(query) + " from:" + str(user_name)
            try: #displaying with print the start and end time + the user name that the function will try to retirve tweets
                display_start_time = datetime.strptime(start_time.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")
                display_end_time = datetime.strptime(end_time.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")
            except:
                display_start_time = start_time
                display_end_time = end_time
            print("Bringing all the tweets of the user:", user_name, "from:", display_start_time, "to", display_end_time)
            print()

        ##### Creating the log directory (that will contain 3 files: The token file, the retriving tweets streem and the full json file)
        import os.path
        dir_log_name = os.path.join(dir_name, "log_key_opinion_leaders")
        
        # Try creating the directory for the logs, if the path exist don't create a new one. Print in either case What happened
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the key opinion leaders")
        except:
            print("The dir", dir_log_name ,"already exist")
        ######################## creating a path for the specific user that we wish to retirve his tweets
        path_for_log_dir_of_certain_user = os.path.join(dir_log_name, user_name)
        
        # Try creating the directory for the specific user, if the path exist don't create a new one. Print in either case What happened
        try:
            os.mkdir(path_for_log_dir_of_certain_user)
            print("creating directory", path_for_log_dir_of_certain_user,"in the dir",dir_log_name, "to insert all the logs of the key opinion leader", user_name)
        except:
            print("The dir", path_for_log_dir_of_certain_user ,"already exist")
        ### creating the log-text-file of the "retriving_tweets_streem" This log file will contain a time-stamp
        # of the time you activated the function, and in each call to twitter API it will write in that log-file
        # the number of tweets that the function retirved in that call + the totla number of tweets retrived so far.
        # With this text file you can follow up in any time the function runs what is the status of the call - 
        # you can see how many tweets have been collected on a specifc user and know that the function works fine.
        path_for_dir_retriving_tweets_streem = os.path.join(path_for_log_dir_of_certain_user, 'retriving_tweets_streem.txt')
        with open(path_for_dir_retriving_tweets_streem, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')

        # Opening the Tokens text-file (if not exist)
        ########### If the token file exist already, then take the last token available, else start from token 1  ############
        tokens_location = os.path.join(dir_log_name, user_name, "tokens.txt")

        if (evaluate_last_token == True and os.path.isfile(tokens_location) == True):
            a_file = open(tokens_location, "r")
            lines = a_file.readlines()
            last_lines = lines[-2]
            next_token = last_lines[0:-1]
            a_file.close()
        else:
            next_token = None

        ################ Add a time stamp ########################################
        path_for_dir_tokens = os.path.join(path_for_log_dir_of_certain_user, 'tokens.txt')
        with open(path_for_dir_tokens, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time+ '\n\n')

        ############################################# The main for loop #############################################

        continue_searching = True #logical variable that controls the for loop, as long as it is True, the function will keep trying to retrive tweets
        json_response_list = [] #list containing all the json responses the function got. In each loop we are
        #saving that list in the log-json file (so if there was a problem in a certain loop, we would have all the jsons till that problematic loop)
        next_tokens = [] #list containing all the tokens
        num_of_returned_tweets = 0 # counter of returned tweets
        counter_loops = 0 #counter of the loops - the number of calls to twitter API

        while continue_searching == True and num_of_returned_tweets < limit_amount_of_returned_tweets:
            counter_loops +=1
            if counter_loops > 1:
                next_token = json_response["meta"]["next_token"]
                query_params["next_token"] = next_token
                if verbose_10:
                    print("token to insert:",next_token)
            #if the returned amount of tweets is getting close to the limit number, we need to alter the max_result,
            #so we won't get tweets beyond what we asked
            if (limit_amount_of_returned_tweets - num_of_returned_tweets) < max_results:
                max_results = limit_amount_of_returned_tweets - num_of_returned_tweets
                if max_results < 10:
                    max_results = 10
            else :
                max_results = max_results

            #change params based on the endpoint you are using
            query_params = {'query': query,
                        'start_time': start_time,
                        'end_time': end_time,
                        'max_results': max_results,
                        'expansions': 'author_id,in_reply_to_user_id,geo.place_id,entities.mentions.username,referenced_tweets.id',
                        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                        'next_token': {next_token}}

            json_response = self.__connect_to_endpoint(url = search_url,params= query_params, next_token = next_token)

            json_response_list.append(json_response) #the first json_response itme
            num_of_returned_tweets += json_response["meta"]["result_count"]

            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                b = pd.json_normalize(json_response["includes"], ["users"]).add_prefix("users.")

                a.conversation_id = a.conversation_id.astype("string")
                a.id = a.id.astype("string")
                a["id_new"] = "id: " + a["id"].astype("string")
                a["conv_id_new"] = "conv_id: " + a["conversation_id"].astype("string")
                a["author_id_new"] = "author_id: " + a["author_id"].astype("string")

            #c = pd.json_normalize(json_response["includes"]["places"]).add_prefix("places.")
                df_tweets_i = pd.merge(a, b, left_on="author_id", right_on="users.id")
                list_of_cols_to_add = ['author_id', "author_id_new", 'conversation_id', "conv_id_new",
                                        "id", "id_new",'created_at','entities.mentions',
                            'public_metrics.like_count', 'public_metrics.quote_count',
                        'public_metrics.reply_count', 'public_metrics.retweet_count','referenced_tweets', 'text',
                            'users.created_at', 'users.description','users.id', 'users.name',
                        'users.public_metrics.followers_count', 'users.public_metrics.following_count',
                        'users.public_metrics.listed_count', 'users.public_metrics.tweet_count',
                        'users.username', 'users.verified']

                list_cols_to_drop = [x for x in df_tweets_i.columns if x not in list_of_cols_to_add]

                ##droping labels (columns) we don't need
                df_tweets_i = df_tweets_i.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                #sort columns by alphabetic order
                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)
            
                #This will be the csv file name that will contain all the tweets of the specific user:
                name = user_name + ".csv"
                path_for_table = os.path.join(dir_name, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)
            except:
                print("no data / include in the json")
            
            ### save all thr json responses in json file:
            path_for_dir_all_json_responses = os.path.join(path_for_log_dir_of_certain_user, 'all_json_responses.json')
            with open(path_for_dir_all_json_responses, 'w') as outfile:
                json.dump(json_response_list, outfile)
            
            ### Writing in the retrieving tweets log file the number of retrieved tweets + status - is the function finished running or keep retrieving more tweets?
            with open(path_for_dir_retriving_tweets_streem, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(json_response["meta"]["result_count"]) + " tweets, and there are more tweets of that user to get, I am bringing more tweets!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_tweets)
                f.write(print_total+ '\n\n')

            if "next_token" in json_response["meta"]:
                if (verbose_10 == True and counter_loops % 20 == 1):
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                #elif verbose_10 == False:
                    #print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                next_token = json_response["meta"]["next_token"]
                query_params["next_token"] = next_token
                next_tokens.append(next_token)
                #ids_token_print = "next token = " + next_token + "newest id: " + json_response["meta"]["newest_id"] + " | oldest id: " + json_response["meta"]["oldest_id"]
                ids_token_print = next_token
                with open(path_for_dir_tokens, 'a') as f:
                    f.write(ids_token_print + '\n\n')
            else:
                print("no more tweets from this user")
                continue_searching = False
                print("Total amount of collected tweets = ", num_of_returned_tweets)

            if num_of_returned_tweets >=limit_amount_of_returned_tweets:
                print("oooops, There may be more tweets to return, but you asked to limit the amount of returned tweets")
                print("infact you got", num_of_returned_tweets, "returned tweets and limited the function to get", limit_amount_of_returned_tweets, "tweets")

        #In what case we suspect that there may be more tweets that we didn't get? -->
        #When the number of tweets we asked to get is equal to the number of tweets we got back

        return json_response_list, num_of_returned_tweets, next_tokens

 #The following cose check wheter the user_name is a list, if not it turnes it into a list


    def return_tweets_of_key_opinion_leaders(self, query="",dir_name="tweets", user_names =None, \
        start_time = "2015-12-7T00:00:00Z", end_time = "2021-12-26T00:00:00Z",
        max_results = 10, evaluate_last_token = False, \
            limit_amount_of_returned_tweets = 10000000, verbose_10 = False):
        """ ## Return Tweets of Key Opinion leaders

This function enalbes getting all the tweets written by a list of twitter accounts in a certain time-frame.\n

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

### App rate limit:
        - App rate limit (OAuth 2.0 App Access Token): 300 requests per 15-minute window shared among all users of your app
        - App rate limit (OAuth 2.0 App Access Token): 1 request per second shared among all users of your app
        
Parameters
- query : str --> You can see the full documentation on how to build a query (what to pass in the `query` argument) in the following link:\n
https://developer.twitter.com/en/docs/twitter-api/tweets/counts/integrate/build-a-query
        
- dir_name: by defualy "tweets" --> the dir name to put all the data from the function

- start_date = The start date is the date that from it the function will look and rerieve tweets.\n
Note that the format of the start time should be: "2015-12-7T00:00:00Z" (this is the default)

- end_date = The end date is the date that till it the function will look and rerieve tweets.\n
Note that the format of the end time should be: "2021-12-26T00:00:00Z" (this is the default)

- max_results = The max number of tweets to retrieve in a given call. Must be an integer between 10 to 500.
- evaluate_last_token - by default = False--> If you have already retrive data on the given tweeter acconts and you wish to continue retriving from the place you stopped, pass "True" to this arguemnt.

- limit_amount_of_returned_tweets - by default = 10000000 --> Lets say a given account had 5000 tweets in the given timeframe (from the given start to the given end date), and you wish to get only the first 2000, then pass to this arguemnt 2000. It will automatically stop the function when it reaches the `limit_amount_of_returned_tweets` you provided

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    
        """

        #handling case where the user entered a max_result that is not between 10 and 100
        if max_results > 500:
            max_results = 500
            print('max_results can not be greater than 500, changed to 500')
        if max_results < 10:
            max_results = 10
            print('max_results can not be smaller than 10, changed to 10')

        if type(user_names) != list:
            user_names = [user_names]

        #users_json_response_lists = []
        names_evaluated = []
        names_didnt_evaluated = []
        next_tokens_users= [] #this will include a list where eachelement is a list containing all the tokens off the specific user
        for name in user_names:
            print("Bringing tweets of", name)
            query = ""
            user_name = name
            try:

                json_response_list, num_of_returned_tweets,next_tokens = self.__return_tweets_of_key_opinion_leader(query=query, user_name=user_name,
                                                        start_time = start_time, evaluate_last_token = evaluate_last_token,
                                                        end_time = end_time,
                                                        max_results = max_results, dir_name=dir_name,
                                                        limit_amount_of_returned_tweets = limit_amount_of_returned_tweets,
                                                                                                            verbose_10 = verbose_10)
                print(num_of_returned_tweets)
                if num_of_returned_tweets > 0:
                    names_evaluated.append(name)
                    next_tokens_users.append(next_tokens)


                else:
                    names_didnt_evaluated.append(name)
                    print("The user:", name, "had", num_of_returned_tweets, "tweets!!")

                print("---------------------------------------------------------------")
            except:
                print("There was a problem with the key opinion leader:", name)
                names_didnt_evaluated.append(name)
                print("*************************************************************************************")



############################################ roy: Dont know what is this ######################################################################
    def create_url_tweet_ids(self, search_url, tweet_ids_list, verbose = False):

        #search_url = "https://api.twitter.com/2/tweets/search/recent" #Change to the endpoint you want to collect data from
        search_url = search_url.replace("X", ','.join(tweet_ids_list))
        if verbose: print(search_url)
        #change params based on the endpoint you are using
        query_params = {
                        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                        'next_token': {}}
        return (search_url, query_params)


##################################################roy: dont know what this is: ################################################################
    def get_tweets_by_tweet_ids(self , tweet_ids, #TypeError: 'type' object is not subscriptable
     json_tweets_output_folder : str,
     tweets_per_api_request : int = 100,
     api_error_sleep_secs : int = 15*60,
     verbose = False ):
        
        json_response_list = []
        os.makedirs(json_tweets_output_folder, exist_ok = True)

        count_proccesed_tweets_file = os.path.join(json_tweets_output_folder, 'count_proccesed_tweets.txt')
        count_requests_sent_file = os.path.join(json_tweets_output_folder,'count_requests_sent.txt')
        json_output_file_basename = os.path.join(json_tweets_output_folder,'twitter_data_')

        if not os.path.exists(count_requests_sent_file):
            with open(count_requests_sent_file,'w') as f:
                f.write('%d' % 0)

        if not os.path.exists(count_proccesed_tweets_file):
            with open(count_proccesed_tweets_file,'w') as f:
                f.write('%d' % 0)

        count_proccesed_tweets = int( open(count_proccesed_tweets_file,'r').read())

        count_requests_sent = int( open(count_requests_sent_file,'r').read())

        while(count_proccesed_tweets < len(tweet_ids)):

            if verbose:
                print(f'~~~~~ Already sent {count_requests_sent} requests')
                print(f'~~~~~ Already proccesed {count_proccesed_tweets} tweets')
                print(f'~~~~~ Currently proccessing {tweets_per_api_request} tweets')


            ## FIXME - last batch size cant be more than what's left
            if len(tweet_ids)>1:
                tweet_ids_batch = tweet_ids[count_proccesed_tweets:(count_proccesed_tweets+ tweets_per_api_request )// (len(tweet_ids)-1)]
            else:
                tweet_ids_batch = tweet_ids
            
            #tweet_ids_batch = tweet_ids[count_proccesed_tweets:(count_proccesed_tweets+ tweets_per_api_request )// (len(tweet_ids)-1)]
            search_url, query_params = self.create_url_tweet_ids("https://api.twitter.com/2/tweets/?ids=X" , tweet_ids_batch)
            # headers = create_headers(os.environ['TOKEN'])

            try:
                json_response = self.__connect_to_endpoint( url = search_url, params= query_params)
                json_response_list.append(json_response)
            except Exception as e:
                print(f'Twitter API error: {e} \n Sleeping 15 min from {datetime.datetime.now()}')
                time.sleep(api_error_sleep_secs)

                
            count_proccesed_tweets += tweets_per_api_request
            count_requests_sent += 1


            with open(f'{json_output_file_basename}{count_requests_sent}.json', "w") as twitter_data_file:
                json.dump(json_response, twitter_data_file, indent=4, sort_keys=True)

            with open(count_proccesed_tweets_file, "w") as f:
                f.write('%d' % count_proccesed_tweets)

            with open(count_requests_sent_file, "w") as f:
                f.write('%d' % count_requests_sent)
                
        return(json_response_list)
            # if verbose: print(f'~~~~~ Batch done, moving forward (sleep 2 min for debug)')
            # time.sleep(5)


########################## Function to get all the retweets given a tweet id / conversation id #############################################################
    def __return_retweets_of_tweet_id_SMALL(self, tweet_id=None,
                                        max_results = 10, evaluate_last_token = False,
                                        limit_amount_of_returned_retweets = 10000000,
                                    verbose = False, dir_tree_name = "conversation_trees"):

        search_url = "https://api.twitter.com/2/tweets/:id/retweeted_by" #endpoint use to collect data from
        search_url = search_url.replace(":id", tweet_id)

        import os.path
        #making a dir for the tree - this file will contain a unique file for each conversation id
        #dir_tree_name = "conversation_trees"
        try:
            os.mkdir(dir_tree_name)
            print("creating tree directory", dir_tree_name, "to store all the trees")
        except:
            print("The dir", dir_tree_name ,"already exist")

        # Making directory (inside the tree dir) to store, for each tweet-id all its retweets (in one csv file)
        name_for_tweet_id = "conv_tree_for_" + str(tweet_id)
        dir_name_for_tweet_id = os.path.join(dir_tree_name, name_for_tweet_id)
        try:
            os.mkdir(dir_name_for_tweet_id)
            print("creating directory", dir_name_for_tweet_id, "to insert all the retweets of the given tweet-id")
        except:
            print("The dir", dir_name_for_tweet_id ,"already exist")

        ##### Creating The log directory (that will contain 3 files: The token file, the retriving tweets streem and the full json file)
        dir_log_name = os.path.join(dir_name_for_tweet_id, "log_retweets_for_tweet_id_" + tweet_id)
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the retweets for the tweet id - ", str(tweet_id))
        except:
            print("The dir", dir_log_name ,"already exist")

        ######################## creating a path for the specific tweet-id that we wish to retirve its retweets
        path_for_dir_retriving_retweets_stream = os.path.join(dir_log_name, 'retriving_retweets_streem.txt')

        with open(path_for_dir_retriving_retweets_stream, 'a') as f:
            from datetime import datetime
            time_now = datetime.now()
            current_time = time_now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')

        ########### If the token file exist already, then take the last token available, else start from token 1  ############
        tokens_location = os.path.join(dir_log_name, "tokens.txt")

        if (evaluate_last_token == True and os.path.isfile(tokens_location) == True):
            a_file = open(tokens_location, "r")
            lines = a_file.readlines()
            last_lines = lines[-2]
            #next_token = last_lines[0:-1]
            #a_file.close()
            if "Current" in last_lines:
                from file_read_backwards import FileReadBackwards

                with FileReadBackwards(tokens_location, encoding="utf-8") as frb:
                    for l in frb:
                        if "Current" in l:
                            continue
                        elif any(c.isalpha() for c in l):
                            next_token = l
                            break
        else:
            next_token = None
        ################ Add a time stamp ########################################
        with open(tokens_location, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time+ '\n\n')

        ##########################################################################################

        continue_searching = True #logical variable that controls the for loop, as long as it is True, the function will keep trying to retrive tweets
        json_response_list = [] #list containing all the json responses the function got. In each loop we are
        #saving that list in the log-json file (so if there was a problem in a certain loop, we would have all the jsons till that problematic loop)
        next_tokens = [] #list containing all the tokens
        num_of_returned_retweets = 0 # counter of returned retweets
        counter_loops = 0 #counter of the loops - the number of calls to twitter API

        while continue_searching == True and num_of_returned_retweets < limit_amount_of_returned_retweets:
            counter_loops +=1
            if counter_loops > 1:
                next_token = json_response["meta"]["next_token"]
                query_params["pagination_token"] = next_token
                print("token to insert:",next_token)
            #if the returned amount of retweets is getting close to the limit number, we need to alter the max_result,
            #so we won't get retweets beyond what we asked
            #if (limit_amount_of_returned_retweets - num_of_returned_retweets) < max_results:
            max_results = min(limit_amount_of_returned_retweets - num_of_returned_retweets, max_results)

        #change params based on the endpoint you are using
            query_params = {
                            'expansions': 'pinned_tweet_id',
                            'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                            'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                            #'place.fields': 'contained_within, country, country_code, full_name, geo, id, name, place_type',
                            'max_results': max_results,
                            'pagination_token': next_token}

            json_response = self.__connect_to_endpoint(url = search_url, params= query_params, next_token = next_token, is_retweet = True)

            # #check if the tweeet_id is valid = if we can find its retweets:
            # if "data" not in json_response:
            #     tweet_ids_not_found.append(json_response["errors"][0]["resource_id"])
            #     print("prob")

            json_response_list.append(json_response) #the first json_response itme
            num_of_returned_retweets += json_response["meta"]["result_count"]

            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                a["id_new"] = "id: " + a["id"].astype("string")
                list_of_cols_to_add = ["id","id_new", "verified", "username", "name", "created_at", "public_metrics.followers_count",
                                    "public_metrics.following_count", "public_metrics.tweet_count",
                                    "public_metrics.listed_count", "pinned_tweet_id"]
                list_cols_to_drop = [x for x in a.columns if x not in list_of_cols_to_add]

                ##droping labels we don't need
                df_tweets_i = a.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                #sort columns by alphabetic order
                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)

                name = tweet_id + "_retweets" + ".csv"
                path_for_table = os.path.join(dir_name_for_tweet_id, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)
            except:
                print("no data / include in the json")

            path_for_dir_all_json_responses = os.path.join(dir_log_name, 'all_json_responses.json')
            with open(path_for_dir_all_json_responses, 'w') as outfile:
                json.dump(json_response_list, outfile)

            with open(path_for_dir_retriving_retweets_stream, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(json_response["meta"]["result_count"]) + " tweets, and there are more tweets of that user to get, I am bringing more tweets!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_retweets)
                f.write(print_total+ '\n\n')

            if "next_token" in json_response["meta"]:
                if (verbose == True and counter_loops % 20 == 1):
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                elif verbose == False:
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                next_token = json_response["meta"]["next_token"]
                query_params["pagination_token"] = next_token
                next_tokens.append(next_token)
                #ids_token_print = "next token = " + next_token + "newest id: " + json_response["meta"]["newest_id"] + " | oldest id: " + json_response["meta"]["oldest_id"]
                ids_token_print = next_token
                with open(tokens_location, 'a') as f:
                    f.write(ids_token_print + '\n\n')
            else:
                print("no more tweets from this user")
                continue_searching = False
                print("Total amount of collected tweets = ", num_of_returned_retweets)

            if num_of_returned_retweets >=limit_amount_of_returned_retweets:
                print("oooops, There may be more tweets to return, but you asked to limit the amount of returned tweets")
                print("infact you got", num_of_returned_retweets, "returned tweets and limited the function to get", limit_amount_of_returned_retweets, "tweets")

        #In what case we suspect that there may be more tweets that we didn't get? -->
        #When the number of tweets we asked to get is equal to the number of tweets we got back

        ### save all thr json responses in json file:

        return json_response_list, num_of_returned_retweets, next_tokens

    def return_retweets_by_tweet_ids(self, tweet_ids,max_results = 10, evaluate_last_token = False,
                                        limit_amount_of_returned_retweets = 10000000,
                                    verbose = False, dir_tree_name = "conversation_trees"):
        """ ## Return Retweets of a given list of tweetIds / converstionIds 

This function enalbes getting all the retweets of a list of tweetids - return information on the people who retweeted a tweet.\n

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/get-tweets-id-retweeted_by

### App rate limit:
        - App rate limit (OAuth 2.0 App Access Token): 75 requests per 15-minute window shared among all users of your app
        - User rate limit (OAuth 2.0 user Access Token): 75 requests per 15-minute window per each authenticated user

### Parameters
- tweet_ids: list --> a list with all the tweet-ids you wish to get all of their retweets

- max_results = The max number of retweets to retrieve in a given call. Must be an integer between 1 to 100.

- evaluate_last_token - by default = False--> If you have already retrive retweets on the given tweet-id and you wish to continue retriving from the place you stopped, pass "True" to this arguemnt.

- limit_amount_of_returned_retweets - by default = 10000000 --> Lets say a given tweet had 5000 retweets,
and you wish to get only the first 2000 retweets, then pass to this arguemnt 2000.
It will automatically stop the function when it reaches the `limit_amount_of_returned_retweets` you provided

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    

- dir_tree_name: by default "conversation_trees" --> the dir name to put all the data from the function
        """                
        
        if max_results > 100:
            max_results = 100
            print('max_results can not be greater than 100, changed to 100')

        if type(tweet_ids) != list:
            tweet_ids = [tweet_ids]

        #users_json_response_lists = []
        tweet_ids_evaluated = []
        tweet_ids_didnt_evaluated = []
        next_tokens_users= [] #this will include a list where eachelement is a list containing all the tokens off the specific user
        for tweet_id in tweet_ids:
            print("Bringing retweets of", tweet_id)
            try:
                json_response_list, num_of_returned_retweets,next_tokens =\
                        self.__return_retweets_of_tweet_id_SMALL(tweet_id=tweet_id,
                            max_results = max_results, evaluate_last_token = evaluate_last_token,
                            limit_amount_of_returned_retweets = limit_amount_of_returned_retweets,
                            verbose = verbose, dir_tree_name = dir_tree_name)


                print(num_of_returned_retweets)
                if num_of_returned_retweets > 0:
                    tweet_ids_evaluated.append(tweet_id)
                    next_tokens_users.append(next_tokens)


                else:
                    tweet_ids_didnt_evaluated.append(tweet_id)
                    print("The tweet_id:", tweet_id, "had", num_of_returned_retweets, "tweets!!")

                print("---------------------------------------------------------------")
            except:
                print("There was a problem with the tweet id:", tweet_id)
                tweet_ids_didnt_evaluated.append(tweet_id)
                print("*************************************************************************************")


################################################## quotes ###############################################

    def __return_quotes_of_tweet_id_SMALL(self, tweet_id=None,
                                        max_results = 10, evaluate_last_token = False,
                                            limit_amount_of_returned_quotes = 10000000,
                                    verbose = False, dir_tree_name = "conversation_trees"):

        search_url = "https://api.twitter.com/2/tweets/:id/quote_tweets"
        search_url = search_url.replace(":id", tweet_id)

        import os.path
        #making a dir for the tree - this file will contain a unique file for each conversation id
        #dir_tree_name = "conversation_trees"
        try:
            os.mkdir(dir_tree_name)
            print("creating tree directory", dir_tree_name, "to store all the trees")
        except:
            print("The dir", dir_tree_name ,"already exist")

        #making dir (inside the tree dir) to store, for each tweet-id all its quotes
        name_for_tweet_id = "conv_tree_for_" + str(tweet_id)
        dir_name_for_tweet_id = os.path.join(dir_tree_name, name_for_tweet_id)
        try:
            os.mkdir(dir_name_for_tweet_id)
            print("creating directory", dir_name_for_tweet_id, "to insert all the quotes of the given tweet-id")
        except:
            print("The dir", dir_name_for_tweet_id ,"already exist")

        ##### the log dir
        dir_log_name = os.path.join(dir_name_for_tweet_id, "log_quotes_for_tweet_id_" + tweet_id)
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the quotes for the tweet id - ", str(tweet_id))
        except:
            print("The dir", dir_log_name ,"already exist")

        ########################
        path_for_dir_retriving_quotes_stream = os.path.join(dir_log_name, 'retriving_quotes_streem.txt')
        with open(path_for_dir_retriving_quotes_stream, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')

        ########### If the token file exist already, then take the last token available, else start from token 1  ############
        tokens_location = os.path.join(dir_log_name, "tokens.txt")

        if (evaluate_last_token == True and os.path.isfile(tokens_location) == True):
            a_file = open(tokens_location, "r")
            lines = a_file.readlines()
            last_lines = lines[-2]
            #next_token = last_lines[0:-1]
            #a_file.close()
            if "Current" in last_lines:
                from file_read_backwards import FileReadBackwards

                with FileReadBackwards(tokens_location, encoding="utf-8") as frb:
                    for l in frb:
                        if "Current" in l:
                            continue
                        elif any(c.isalpha() for c in l):
                            next_token = l
                            break
        else:
            next_token = None

        ################ Add a time stamp ########################################
        with open(tokens_location, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time+ '\n\n')

        ##########################################################################################

        continue_searching = True
        json_response_list = []
        next_tokens = []
        num_of_returned_quotes = 0
        counter_loops = 0

        while continue_searching == True and num_of_returned_quotes < limit_amount_of_returned_quotes:
            counter_loops +=1
            if counter_loops > 1:
                next_token = json_response["meta"]["next_token"]
                query_params["pagination_token"] = next_token
                print("token to insert:",next_token)
            #if the returned amount of quotes is getting close to the limit number, we need to alter the max_result,
            #so we won't get quotes beyond what we asked
            if (limit_amount_of_returned_quotes - num_of_returned_quotes) < max_results:
                max_results = limit_amount_of_returned_quotes - num_of_returned_quotes
            else :
                max_results = max_results

        #change params based on the endpoint you are using
            query_params = {'expansions': 'author_id,in_reply_to_user_id,geo.place_id,entities.mentions.username,referenced_tweets.id',
                            'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                            'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                            'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                            'max_results': max_results,
                            'pagination_token': {next_token}}

            json_response = self.__connect_to_endpoint(url = search_url, params= query_params, next_token = next_token, is_retweet = True)

            json_response_list.append(json_response) #the first json_response itme
            num_of_returned_quotes += json_response["meta"]["result_count"]

            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                a["id_new"] = "id: " + a["id"].astype("string")
                a["conversation_id_new"] = "conversation_id: " + a["conversation_id"].astype("string")
                a["author_id_new"] = "author_id: " + a["author_id"].astype("string")
                b = pd.json_normalize(json_response["includes"], ["users"]).add_prefix("users.")

                df_tweets_i = pd.merge(a, b, left_on="author_id", right_on="users.id")

                list_of_cols_to_add = ['id', "id_new", 'conversation_id', "conversation_id_new",
                                        'lang', 'author_id', "author_id_new" ,'referenced_tweets',
                                    'text', 'created_at', 'source', 'reply_settings',
                                    'public_metrics.retweet_count', 'public_metrics.reply_count',
                                    'public_metrics.like_count', 'public_metrics.quote_count',
                                    'in_reply_to_user_id', 'geo.place_id',
                                    'users.username', 'users.name', 'users.verified',
                                    'users.created_at', 'users.id', 'users.public_metrics.followers_count',
                                    'users.public_metrics.following_count',
                                    'users.public_metrics.tweet_count',
                                    'users.public_metrics.listed_count'] #'referenced_tweet_type', 'referenced_tweet_id'

                list_cols_to_drop = [x for x in a.columns if x not in list_of_cols_to_add]

                ##droping labels we don't need
                df_tweets_i = df_tweets_i.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                # #add 2 new columns for referenced tweets
                # referenced_tweet_type = []
                # referenced_tweet_id = []
                # for row in range(df_tweets_i.shape[0]):
                #     referenced_tweet_type.append(df_tweets_i.referenced_tweets[0][0]["type"])
                #     referenced_tweet_id.append(df_tweets_i.referenced_tweets[0][0]["id"])

                # df_tweets_i["referenced_tweets_type"] = np.asarray(referenced_tweet_type)
                # df_tweets_i["referenced_tweets_id"] = np.asarray(referenced_tweet_id)
                #sort columns by alphabetic order
                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)

                name = tweet_id + "_quotes" + ".csv"
                path_for_table = os.path.join(dir_name_for_tweet_id, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)
            except:
                print("no data / include in the json")

                ### save all thr json responses in json file:
                path_for_dir_all_json_responses = os.path.join(dir_log_name, 'all_json_responses.json')
                with open(path_for_dir_all_json_responses, 'w') as outfile:
                    json.dump(json_response_list, outfile)



            with open(path_for_dir_retriving_quotes_stream, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(json_response["meta"]["result_count"]) + " tweets, and there are more tweets of that user to get, I am bringing more tweets!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_quotes)
                f.write(print_total+ '\n\n')

            if "next_token" in json_response["meta"]:
                if (verbose == True and counter_loops % 20 == 1):
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                elif verbose == False:
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                next_token = json_response["meta"]["next_token"]
                query_params["pagination_token"] = next_token
                next_tokens.append(next_token)
                #ids_token_print = "next token = " + next_token + "newest id: " + json_response["meta"]["newest_id"] + " | oldest id: " + json_response["meta"]["oldest_id"]
                ids_token_print = next_token
                with open(tokens_location, 'a') as f:
                    f.write(ids_token_print + '\n\n')
            else:
                print("no more tweets from this user")
                continue_searching = False
                print("Total amount of collected tweets = ", num_of_returned_quotes)

            if num_of_returned_quotes >=limit_amount_of_returned_quotes:
                print("oooops, There may be more tweets to return, but you asked to limit the amount of returned tweets")
                print("infact you got", num_of_returned_quotes, "returned tweets and limited the function to get", limit_amount_of_returned_quotes, "tweets")

        #In what case we suspect that there may be more tweets that we didn't get? -->
        #When the number of tweets we asked to get is equal to the number of tweets we got back


        return json_response_list, num_of_returned_quotes, next_tokens,path_for_table


    def return_quotes_by_tweet_ids(self, tweet_ids, max_results = 10, evaluate_last_token = False,
                                            limit_amount_of_returned_quotes = 10000000,
                                        verbose = False, dir_tree_name = "conversation_trees"):

        """ ## Return Quotes of a given list of tweet Ids / converstion Ids 

This function enalbes getting all the quotes of a list of tweetids / conversation ids.\n

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/quote-tweets/api-reference/get-tweets-id-quote_tweets

### App rate limit:
        - App rate limit (OAuth 2.0 App Access Token): 75 requests per 15-minute window shared among all users of your app
        - User rate limit (OAuth 2.0 user Access Token): 75 requests per 15-minute window per each authenticated user

### Parameters
- tweet_ids: list --> a list with all the tweet-ids you wish to get all of their quotes

- max_results = The max number of retweets to retrieve in a given call. Must be an integer between 10 to 100.

- evaluate_last_token - by default = False--> If you have already retrive quotes on the given tweet-id and you wish to continue retriving from the place you stopped, pass "True" to this arguemnt.

- limit_amount_of_returned_quotes - by default = 10000000 --> Lets say a given tweet had 5000 quotes,
and you wish to get only the first 2000 quotes, then pass to this arguemnt 2000.
It will automatically stop the function when it reaches the `limit_amount_of_returned_quotes` you provided

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    

- dir_tree_name: by default "conversation_trees" --> the dir name to put all the data from the function
        """   

        if max_results > 100:
            max_results = 100
            print('max_results can not be greater than 100, changed to 100')
        if max_results < 10:
            max_results = 10
            print('max_results can not be smaller than 10, changed to 10')
        if type(tweet_ids) != list:
            tweet_ids = [tweet_ids]

        #users_json_response_lists = []
        tweet_ids_evaluated = []
        tweet_ids_didnt_evaluated = []
        next_tokens_users= [] #this will include a list where eachelement is a list containing all the tokens off the specific user
        path_for_table_dict = {}
        for tweet_id in tweet_ids:
            print("Bringing quotes of", tweet_id)
            try:
                json_response_list, num_of_returned_quotes,next_tokens, path_for_table =\
                    self.__return_quotes_of_tweet_id_SMALL(tweet_id=tweet_id,
                            max_results = max_results, evaluate_last_token = evaluate_last_token,
                            limit_amount_of_returned_quotes = limit_amount_of_returned_quotes,
                        verbose = verbose, dir_tree_name = dir_tree_name)

                path_for_table_dict[tweet_id] = path_for_table


                print(num_of_returned_quotes)
                if num_of_returned_quotes > 0:
                    tweet_ids_evaluated.append(tweet_id)
                    next_tokens_users.append(next_tokens)


                else:
                    tweet_ids_didnt_evaluated.append(tweet_id)
                    print("The tweet_id:", tweet_id, "had", num_of_returned_quotes, "quotes!!")

                print("---------------------------------------------------------------")
            except:
                print("There was a problem with the tweet id:", tweet_id)
                tweet_ids_didnt_evaluated.append(tweet_id)
                print("*************************************************************************************")

        return path_for_table_dict

################################################ likes ##################################################
    def __return_likes_of_tweet_id_SMALL(self, tweet_id=None,
                                        max_results = 10, evaluate_last_token = False,
                                            limit_amount_of_returned_likes = 10000000,
                                    verbose = False, dir_tree_name = "conversation_trees"):

        search_url = "https://api.twitter.com/2/tweets/:id/liking_users"
        search_url = search_url.replace(":id", tweet_id)

        import os.path
        #making a dir for the tree - this file will contain a unique file for each conversation id
        #dir_tree_name = "conversation_trees"
        try:
            os.mkdir(dir_tree_name)
            print("creating tree directory", dir_tree_name, "to store all the trees")
        except:
            print("The dir", dir_tree_name ,"already exist")

        #making dir (inside the tree dir) to store, for each tweet-id all its likes
        name_for_tweet_id = "conv_tree_for_" + str(tweet_id)
        dir_name_for_tweet_id = os.path.join(dir_tree_name, name_for_tweet_id)
        try:
            os.mkdir(dir_name_for_tweet_id)
            print("creating directory", dir_name_for_tweet_id, "to insert all the likes of the given tweet-id")
        except:
            print("The dir", dir_name_for_tweet_id ,"already exist")

        ##### the log dir
        dir_log_name = os.path.join(dir_name_for_tweet_id, "log_likes_for_tweet_id_" + tweet_id)
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the likes for the tweet id - ", str(tweet_id))
        except:
            print("The dir", dir_log_name ,"already exist")

        ########################
        path_for_dir_retriving_likes_stream = os.path.join(dir_log_name, 'retriving_likes_streem.txt')
        with open(path_for_dir_retriving_likes_stream, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')

        ########### If the token file exist already, then take the last token available, else start from token 1  ############
        tokens_location = os.path.join(dir_log_name, "tokens.txt")

        if (evaluate_last_token == True and os.path.isfile(tokens_location) == True):
            a_file = open(tokens_location, "r")
            lines = a_file.readlines()
            last_lines = lines[-2]
            #next_token = last_lines[0:-1]
            #a_file.close()
            if "Current" in last_lines:
                from file_read_backwards import FileReadBackwards

                with FileReadBackwards(tokens_location, encoding="utf-8") as frb:
                    for l in frb:
                        if "Current" in l:
                            continue
                        elif any(c.isalpha() for c in l):
                            next_token = l
                            break
        else:
            next_token = None

        ################ Add a time stamp ########################################
        with open(tokens_location, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time+ '\n\n')
        ######################################## The Main For Loop #############################################

        continue_searching = True
        json_response_list = []
        next_tokens = []
        num_of_returned_likes = 0
        counter_loops = 0

        while continue_searching == True and num_of_returned_likes < limit_amount_of_returned_likes:
            counter_loops +=1
            if counter_loops > 1:
                next_token = json_response["meta"]["next_token"]
                query_params["pagination_token"] = next_token
                print("token to insert:",next_token)
            #if the returned amount of quotes is getting close to the limit number, we need to alter the max_result,
            #so we won't get quotes beyond what we asked
            if (limit_amount_of_returned_likes - num_of_returned_likes) < max_results:
                max_results = limit_amount_of_returned_likes - num_of_returned_likes
            else :
                max_results = max_results

        #change params based on the endpoint you are using
            query_params = {'expansions': 'pinned_tweet_id',
                            'tweet.fields': "attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,non_public_metrics,public_metrics,organic_metrics,promoted_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld",
                            'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                            'max_results': max_results,
                            'pagination_token': {next_token}}

            json_response = self.__connect_to_endpoint(url = search_url, params= query_params, next_token = next_token, is_retweet = True)

            json_response_list.append(json_response) #the first json_response itme
            num_of_returned_likes += json_response["meta"]["result_count"]

            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                a["id_new"] = "id: " + a["id"].astype("string")
                #b = pd.json_normalize(json_response["includes"], ["users"]).add_prefix("users.")

                #df_tweets_i = pd.merge(a, b, left_on="author_id", right_on="users.id")

                list_of_cols_to_add = ['id', "id_new", 'verified', 'created_at', 'description', 'name', 'username',
       'public_metrics.followers_count', 'public_metrics.following_count',
       'public_metrics.tweet_count', 'public_metrics.listed_count'] #'referenced_tweet_type', 'referenced_tweet_id'

                list_cols_to_drop = [x for x in a.columns if x not in list_of_cols_to_add]

                ##droping labels we don't need
                df_tweets_i = a.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)

                name = tweet_id + "_likes" + ".csv"
                path_for_table = os.path.join(dir_name_for_tweet_id, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)
            except:
                print("no data / include in the json")

                ### save all thr json responses in json file:
                path_for_dir_all_json_responses = os.path.join(dir_log_name, 'all_json_responses.json')
                with open(path_for_dir_all_json_responses, 'w') as outfile:
                    json.dump(json_response_list, outfile)

            with open(path_for_dir_retriving_likes_stream, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(json_response["meta"]["result_count"]) + " tweets, and there are more tweets of that user to get, I am bringing more tweets!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_likes)
                f.write(print_total+ '\n\n')

            if "next_token" in json_response["meta"]:
                if (verbose == True and counter_loops % 20 == 1):
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                elif verbose == False:
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                next_token = json_response["meta"]["next_token"]
                query_params["pagination_token"] = next_token
                next_tokens.append(next_token)
                #ids_token_print = "next token = " + next_token + "newest id: " + json_response["meta"]["newest_id"] + " | oldest id: " + json_response["meta"]["oldest_id"]
                ids_token_print = next_token
                with open(tokens_location, 'a') as f:
                    f.write(ids_token_print + '\n\n')
            else:
                print("no more tweets from this user")
                continue_searching = False
                print("Total amount of collected tweets = ", num_of_returned_likes)

            if num_of_returned_likes >=limit_amount_of_returned_likes:
                print("oooops, There may be more likes to return, but you asked to limit the amount of returned likes")
                print("infact you got", num_of_returned_likes, "returned likes and limited the function to get", limit_amount_of_returned_likes, "tweets")

        return json_response_list, num_of_returned_likes, next_tokens, path_for_table


    def return_likes_by_tweet_ids(self, tweet_ids,max_results = 10, evaluate_last_token = False,
                                            limit_amount_of_returned_likes = 10000000,
                                        verbose = False, dir_tree_name = "conversation_trees"):
        """ ## Return users who liked given tweet Ids / converstion Ids 

This function enalbes getting, for a list of tweet ids / conversation ids, all the users who liked those tweets.\n

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-tweets-id-liking_users

### App rate limit:
        - App rate limit (OAuth 2.0 App Access Token): 75 requests per 15-minute window shared among all users of your app
        - User rate limit (OAuth 2.0 user Access Token): 75 requests per 15-minute window per each authenticated user

### Parameters
- tweet_ids: list --> a list with all the tweet-ids you wish to get all of their likes

- max_results = The max number of likes to retrieve in a given call. Must be an integer between 1 to 100.

- evaluate_last_token - by default = False--> If you have already retrive likes on the given tweet-id and you wish to continue retriving from the place you stopped, pass "True" to this arguemnt.

- limit_amount_of_returned_likes - by default = 10000000 --> Lets say a given tweet had 5000 likes,
and you wish to get only the first 2000 likes, then pass to this arguemnt 2000.
It will automatically stop the function when it reaches the `limit_amount_of_returned_likes` you provided

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    

- dir_tree_name: by default "conversation_trees" --> the dir name to put all the data from the function
        """   
        if max_results > 100:
            max_results = 100
            print('max_results can not be greater than 100, changed to 100')
        if max_results < 1:
            max_results = 1
            print('max_results can not be smaller than 1, changed to 1')
        if type(tweet_ids) != list:
            tweet_ids = [tweet_ids]

        #users_json_response_lists = []
        tweet_ids_evaluated = []
        tweet_ids_didnt_evaluated = []
        next_tokens_users= [] #this will include a list where eachelement is a list containing all the tokens off the specific user
        path_for_table_dict = {}
        for tweet_id in tweet_ids:
            print("Bringing likes of", tweet_id)
            try:
                json_response_list, num_of_returned_likes,next_tokens, path_for_table =\
                    self.__return_likes_of_tweet_id_SMALL(tweet_id=tweet_id,
                            max_results = max_results, evaluate_last_token = evaluate_last_token,
                            limit_amount_of_returned_likes = limit_amount_of_returned_likes,
                        verbose = verbose, dir_tree_name = dir_tree_name)

                path_for_table_dict[tweet_id] = path_for_table

                print(num_of_returned_likes)
                if num_of_returned_likes > 0:
                    tweet_ids_evaluated.append(tweet_id)
                    next_tokens_users.append(next_tokens)

                else:
                    tweet_ids_didnt_evaluated.append(tweet_id)
                    print("The tweet_id:", tweet_id, "had", num_of_returned_likes, "likes!!")

                print("---------------------------------------------------------------")
            except:
                print("There was a problem with the tweet id:", tweet_id)
                tweet_ids_didnt_evaluated.append(tweet_id)
                print("*************************************************************************************")

        return path_for_table_dict


########################################### replies: ############################################################
# Twitter's API doesn't allow you to get replies to a particular tweet. Strange
# but true. But you can use Twitter's Search API to search for tweets that are
# directed at a particular user, and then search through the results to see if
# any are replies to a given tweet. You probably are also interested in the
# replies to any replies as well, so the process is recursive. The big caveat
# here is that the search API only returns results for the last 7 days. So
# you'll want to run this sooner rather than later.
#### link: https://gist.github.com/edsu/54e6f7d63df3866a87a15aed17b51eaf

## To get the commetnts f a certain tweet you need to provide the conversation id
    def __return_replies_of_conv_id_SMALL(self, conversation_id="", query = "",
                                        start_time = "2015-12-7T00:00:00Z",
                                        end_time = "today",
                                        max_results = 10, evaluate_last_token = False,
                                        limit_amount_of_returned_comments = 10000000,
                                        verbose = False, dir_tree_name = "conversation_trees"):

        from datetime import date
        if end_time == "today":
            #if you wish to get all the comments that were written till this day:
            end_time = date.today().strftime("%Y-%m-%d")+"T00:00:00Z"

        tweet_id = conversation_id
        search_url = "https://api.twitter.com/2/tweets/search/all" #endpoint use to collect data from
        query = query + "conversation_id:"+ str(conversation_id)

        import os.path
        #making a dir for the tree - this file will contain a unique file for each conversation id
        #dir_tree_name = "conversation_trees"
        try:
            os.mkdir(dir_tree_name)
            print("creating tree directory", dir_tree_name, "to store all the trees")
        except:
            print("The dir", dir_tree_name ,"already exist")


        #making dir (inside the tree dir) to store, for each tweet-id all its quotes
        name_for_tweet_id = "conv_tree_for_" + str(tweet_id)
        dir_name_for_tweet_id = os.path.join(dir_tree_name, name_for_tweet_id)
        try:
            os.mkdir(dir_name_for_tweet_id)
            print("creating directory", dir_name_for_tweet_id, "to insert all the comments of the given conversation-id")
        except:
            print("The dir", dir_name_for_tweet_id ,"already exist")

        ##### the log dir
        dir_log_name = os.path.join(dir_name_for_tweet_id, "log_comments_for_conversation_id_" + tweet_id)
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the comments for the tweet id - ", str(tweet_id))
        except:
            print("The dir", dir_log_name ,"already exist")

        ########################

        path_for_dir_retriving_comments_stream = os.path.join(dir_log_name, 'retriving_comments_streem.txt')
        with open(path_for_dir_retriving_comments_stream, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')

        ########### If the token file exist already, then take the last token available, else start from token 1  ############
        tokens_location = os.path.join(dir_log_name, "tokens.txt")

        if (evaluate_last_token == True and os.path.isfile(tokens_location) == True):
            a_file = open(tokens_location, "r")
            lines = a_file.readlines()
            last_lines = lines[-2]
            #next_token = last_lines[0:-1]
            #a_file.close()
            if "Current" in last_lines:
                from file_read_backwards import FileReadBackwards

                with FileReadBackwards(tokens_location, encoding="utf-8") as frb:
                    for l in frb:
                        if "Current" in l:
                            continue
                        elif any(c.isalpha() for c in l):
                            next_token = l
                            break
        else:
            next_token = None

        ################ Add a time stamp ########################################
        with open(tokens_location, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time+ '\n\n')

        ##########################################################################################

        continue_searching = True
        json_response_list = []
        next_tokens = []
        num_of_returned_comments = 0
        counter_loops = 0

        while continue_searching == True and num_of_returned_comments < limit_amount_of_returned_comments:
            counter_loops +=1
            if counter_loops > 1:
                next_token = json_response["meta"]["next_token"]
                query_params["next_token"] = next_token
                if verbose: print("token to insert:",next_token)
            #if the returned amount of quotes is getting close to the limit number, we need to alter the max_result,
            #so we won't get quotes beyond what we asked
            if (limit_amount_of_returned_comments - num_of_returned_comments) < max_results:
                max_results = limit_amount_of_returned_comments - num_of_returned_comments
            else :
                max_results = max_results
        #change params based on the endpoint you are using
            query_params = {'query': query,
                                    'start_time': start_time,
                                    'end_time': end_time,
                                    'max_results': max_results,
                                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id,entities.mentions.username,referenced_tweets.id',
                                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                                    'next_token': {next_token}}

            json_response = self.__connect_to_endpoint(url = search_url, params= query_params, next_token = next_token, is_retweet = False)

            json_response_list.append(json_response) #the first json_response itme
            num_of_returned_comments += json_response["meta"]["result_count"]


            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                a["id_new"] = "id: " + a["id"].astype("string")
                a["conv_id_new"] = "coversation_id: " + a["conversation_id"].astype("string")
                a["author_id_new"] = "author_id: " + a["author_id"].astype("string")

                b = pd.json_normalize(json_response["includes"], ["users"]).add_prefix("users.")

                df_tweets_i = pd.merge(a, b, left_on="author_id", right_on="users.id")

                list_of_cols_to_add = ['id', "id_new", "conv_id_new", "author_id_new", 'text', 'conversation_id', 'in_reply_to_user_id','reply_settings', 'referenced_tweets', 'lang', 'created_at',
        'author_id', 'source', 'entities.mentions', 'public_metrics.retweet_count', 'public_metrics.reply_count',
        'public_metrics.like_count', 'public_metrics.quote_count', 'users.username', 'users.created_at', 'users.id', 'users.description',
            'users.verified', 'users.name', 'users.public_metrics.followers_count','users.public_metrics.following_count',
            'users.public_metrics.tweet_count','users.public_metrics.listed_count'] #'referenced_tweet_type', 'referenced_tweet_id'

                list_cols_to_drop = [x for x in a.columns if x not in list_of_cols_to_add]

                ##droping labels we don't need
                df_tweets_i = df_tweets_i.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)

                name = tweet_id + "_comments" + ".csv"
                path_for_table = os.path.join(dir_name_for_tweet_id, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)

            except:
                print("no data / include in the json")

                ### save all thr json responses in json file:
                path_for_dir_all_json_responses = os.path.join(dir_log_name, 'all_json_responses.json')
                with open(path_for_dir_all_json_responses, 'w') as outfile:
                    json.dump(json_response_list, outfile)



            with open(path_for_dir_retriving_comments_stream, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(json_response["meta"]["result_count"]) + " comments, and there are more comments of that conversation-id to get, I am bringing more comments!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_comments)
                f.write(print_total+ '\n\n')

            if "next_token" in json_response["meta"]:
                if (verbose == True and counter_loops % 20 == 1):
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "comments, and there are more comments of that conversation-id to get, I am bringing more comments!\n")
                elif verbose == False:
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "comments, and there are more comments of that conversation-id to get, I am bringing more comments!\n")
                next_token = json_response["meta"]["next_token"]
                query_params["next_token"] = next_token
                next_tokens.append(next_token)
                #ids_token_print = "next token = " + next_token + "newest id: " + json_response["meta"]["newest_id"] + " | oldest id: " + json_response["meta"]["oldest_id"]
                ids_token_print = next_token
                with open(tokens_location, 'a') as f:
                    f.write(ids_token_print + '\n\n')
            else:
                print("no more comments from this conversation id")
                continue_searching = False
                print("Total amount of collected comments = ", num_of_returned_comments)

            if num_of_returned_comments >=limit_amount_of_returned_comments:
                print("oooops, There may be more comments to return, but you asked to limit the amount of returned comments")
                print("infact you got", num_of_returned_comments, "returned comments and limited the function to get", limit_amount_of_returned_comments, "comments")

        return json_response_list, num_of_returned_comments, next_tokens, path_for_table

#max result in comment function: 10 - 500

    def return_comments_by_tweet_ids(self, conversation_ids = None, query = "",
                                start_time = "2015-12-7T00:00:00Z",
                                end_time = "today",
                                max_results = 10, evaluate_last_token = False,
                                limit_amount_of_returned_comments = 10000000,
                                verbose = False, dir_tree_name = "conversation_trees"):
        """ ## Return Replies for a given tweet Ids / converstion Ids 

This function enalbes getting all the replies (comments) of a list of tweet ids / conversation ids

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

### App rate limit:
    - App rate limit (OAuth 2.0 App Access Token): 300 requests per 15-minute window shared among all users of your app
    - App rate limit (OAuth 2.0 App Access Token): 1 request per second shared among all users of your app

### Parameters
- conversation_ids: list --> a list with all the tweet-ids you wish to get all of their replies

- query : str --> You can see the full documentation on how to build a query (what to pass in the `query` argument) in the following link:\n
https://developer.twitter.com/en/docs/twitter-api/tweets/counts/integrate/build-a-query


- start_time = The start time is the date-time that from it the function will look and rerieve replies to a certain tweet.\n
Note that the format of the start time should be: "2015-12-7T00:00:00Z" (this is the default)

- end_time = The end time is the date-time that till it the function will look and rerieve replies to a certain tweet.\n
Note that the format of the end time should be: "2021-12-26T00:00:00Z".
The defualt is "today", this automatically retrive all the comments written till this day

- max_results = The max number of likes to retrieve in a given call. Must be an integer between 1 to 100.

- evaluate_last_token - by default = False--> If you have already retrive likes on the given tweet-id and you wish to continue retriving from the place you stopped, pass "True" to this arguemnt.

- limit_amount_of_returned_likes - by default = 10000000 --> Lets say a given tweet had 5000 likes,
and you wish to get only the first 2000 likes, then pass to this arguemnt 2000.
It will automatically stop the function when it reaches the `limit_amount_of_returned_likes` you provided

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    

- dir_tree_name: by default "conversation_trees" --> the dir name to put all the data from the function
        """

        tweet_ids = conversation_ids
        if max_results > 500:
            max_results = 500
            print('max_results can not be greater than 100, changed to 100')
        if max_results < 10:
            max_results = 10
            print('max_results can not be smaller than 10, changed to 10')
        if type(tweet_ids) != list:
            tweet_ids = [tweet_ids]

        #users_json_response_lists = []
        tweet_ids_evaluated = []
        tweet_ids_didnt_evaluated = []
        next_tokens_users= [] #this will include a list where eachelement is a list containing all the tokens off the specific user
        path_for_table_dict = {}
        for tweet_id in tweet_ids:
            print("Bringing comments of", tweet_id)
            try:
                json_response_list, num_of_returned_comments,next_tokens, path_for_table =\
                    self.__return_replies_of_conv_id_SMALL(conversation_id=tweet_id,
                                                        query = query,
                                                        start_time = start_time, end_time = end_time,
                                                        max_results = max_results, evaluate_last_token = evaluate_last_token,
                                                        limit_amount_of_returned_comments = limit_amount_of_returned_comments,
                                                        verbose = verbose, dir_tree_name = dir_tree_name)

                path_for_table_dict[tweet_id] = path_for_table

                print(num_of_returned_comments)
                if num_of_returned_comments > 0:
                    tweet_ids_evaluated.append(tweet_id)
                    next_tokens_users.append(next_tokens)


                else:
                    tweet_ids_didnt_evaluated.append(tweet_id)
                    print("The conversation id:", tweet_id, "had", num_of_returned_comments, "comments!!")

                print("---------------------------------------------------------------")
            except:
                print("There was a problem with the conversation id:", tweet_id)
                tweet_ids_didnt_evaluated.append(tweet_id)
                print("*************************************************************************************")

        return path_for_table_dict


##################################################### Filter function ################################################
   

    def filter_tweets_Brexit(self, dir_with_all_tweets, score_for_KOP = 5, score_for_key_event = 5, score_for_key_words = 5,
                            key_words = ["brexit", "eu", "deal"], threshold_score = 10,
                            KOP_excel_name = "KOP brexit.xlsx",
                            key_events_excel_name = "Brexit_key_events.xlsx",
                            stop_words_to_add = ["https"], stop_words_file_name = "stopwords.txt",
                            verbose = True):
        """
    # Function filter tweets

    We read numerous amount of tweets, comments, retweets and quotes from twitter.
    Now we wish to create a function that, given a dataframe with  tweets / comments / quotes it will enable scoring them.
    The scoring will be based on the following parameters:

    1. The author - if he is one of the KOPs - K points
    2. The time - if it is in the day of key event - K points
    3. The text - if it contains key words - K points

    ### Notes:
    + Note that you can't mix tables with tweets / comments / quotes - this is because they have different amount of columns. You need to process the tweets, comments and quotes table separately

    + **The key-events table and the KOP table - MUST BE OF XLSX TYPE!!**

    ### The Filter function gets as input:

    + 1. **dir_with_all_tweets** - The location / name of dir (if the dir is in the same location of the jupyter file) of all the tweets table that we want to read into the function (this is important as all the csv tweet tables that will be located in this location will be read into the function).

    + 2. **score_for_KOP** = By default = 5. This argument controls the **weight** given to tweet with author id of **Key Opinion Leader**

    + 3. **score_for_key_event** = By default = 5. This argument controls the **weight** given to tweet that was published in **key event day**.

    + 4. **score_for_key_words** = By default = 5. This argument controls the **weight** given to **each** **key-word** that is located in the tweet.

    + 5. **key_words** = By default = ["brexit", "eu", "deal"]. This argument controls the **Key words** to search in each tweet that are related to the brexit. Tweets with high amount of those words are assumed to be important.

    + 6. **threshold_score** - By default = 10. This is a very important argument. It controls the minimum score that a tweet must get in order to be returned in the filtered tweets table. Any tweet with score under this value won't be included in the filtered table

    + 7. **KOP_excel_name** - The name of the excel file (**xlsx format**) that contains the Key Opinion Leaders

    + 8. **key_events_excel_name** - The name of the excel file (**xlsx format**) that contains the key events data

    + 9. **stop_words_to_add** = A list with all the additional words you wish the function to handle as stop words (those words will be removed from each list of tokens for each tweet).

    + 10. **stop_words_file_name** = The name of the text file that contains all the stopwords. Note that if it doesn't exist, the function will go to "https://gist.githubusercontent.com/sebleier/554280/raw/7e0e4a1ce04c2bb7bd41089c9821dbcf6d0c786c/NLTK's%2520list%2520of%2520english%2520stopwords" - to find the stopwords

    + 11. **verbose** = by default = True. If True than the function will print its progress (suggested!)

    ### The function returns:

    + **tweets_table_filtered** - The filtered tweets table is a table containing all the tweets that their score is higher than the `threshold_score`

    + **tweets_table** - The preprocessed tweets table with all the tweets - This table is identical to the `tweets_table_filtered` except that it also included tweets with score under the `threshold_score`

    + **csv_files_evaluated** = a list with all the **csv** files that the function read and add to the tweets table (the files are read from the location you provided in the argument: `dir_with_all_tweets`)
        """
        
        start_fun_time = time.time()
        ############# step 1 - Reading the tweets data #############
        if verbose: print("Step 1: Reading all the csv files")
        tweets_tables = []
        csv_files_evaluated = []
        for root,dirs,files in os.walk(dir_with_all_tweets):
            for file in files:
                if file.endswith(".csv"): #if the file is csv
                    csv_files_evaluated.append(file)
                    file_location = os.path.join(dir_with_all_tweets, file)
                    tweets_tables.append(pd.read_csv(file_location))

        tweets_table = pd.concat(tweets_tables)
        if verbose: print("There are: ", tweets_table.shape[0], "Tweets")
        ############# step 2 - Reading events data #############
        if verbose: print("Step 2: Reading The Events Excel File")
        dir_path_for_events_table = os.path.join(key_events_excel_name)
        events_table = pd.read_excel(dir_path_for_events_table)
        events_table = events_table.drop(labels = ["tweets", "Arguments", "Index"], axis = 1)
        #display(events_table.head())

        ############# step 3 - Reading KOP data #############
        if verbose: print("Step 3: Reading and preprocessing Key Opinion Leaders data")
        dir_path_for_KOP_table = os.path.join(KOP_excel_name)
        KOP_table = pd.read_excel(dir_path_for_KOP_table)
        try:
            KOP_table.rename(columns = {'Unnamed: 0':'KOP_num',
                                        "Born In":"Born_in",
                                        "Twitter acount name" : "twitter_user_name",}, inplace = True)
            #drop unnecessary columns
            KOP_table = KOP_table.drop(labels = ["Unnamed: 7", "Source"], axis = 1)
        except: print()

        #remove KOP without twitter account name
        KOP_table = KOP_table[KOP_table['twitter_user_name'].notna()]
        #remove the "@" at the begining of some user names
        KOP_table["clean_user_name"] = KOP_table["twitter_user_name"].apply(lambda x: x.replace("@", ""))

        def take_all_except_first_char(x):
            try:
                author_id = tweeterid.handle_to_id(x)
            except:
                author_id = "-"
            return author_id

        KOP_table["author_id"] = KOP_table["clean_user_name"].apply(take_all_except_first_char)

        ############# step 4-A - Stop-words #############
        if verbose: print("Step 4-A: Reading stop words data and adding your stop words")
        stopwords_file_name = os.path.join(stop_words_file_name)
        stopwords_url = "https://gist.githubusercontent.com/sebleier/554280/raw/7e0e4a1ce04c2bb7bd41089c9821dbcf6d0c786c/NLTK's%2520list%2520of%2520english%2520stopwords"

        if not os.path.isfile(stopwords_file_name):
            stopwords = requests.get(stopwords_url).text.split()
            with open(stopwords_file_name,'w+t', encoding='utf-8') as out_file:
                out_file.write(' '.join(stopwords))
        else:
            with open(stopwords_file_name,'rt', encoding='utf-8') as in_file:
                stopwords = in_file.readline().split()
        stopwords = set(stopwords)

        #### Adding stopWords
        for word_i in stop_words_to_add:
            stopwords.add(word_i)

        ############# step 4-B - contractions #############
        if verbose: print("\nStep 4-B: Preprocess the tweets table - the text column - using contractions | ")
        def clean_text(x):
            from gensim.utils import simple_preprocess
            import contractions
            x = contractions.fix(x)
            x = ' '.join(simple_preprocess(x))
            return x
        tweets_table['text'] = tweets_table['text'].apply(clean_text)

        ############# step 5 - Preprocess the tweets table for scoring #############
        if verbose: print("\nStep 5: Preprocess the tweets table for scoring:\nRemoving Stop words\
        | bigram, trigram, forthgram | merging the tweets table with the KOP and Events tables | ")

        start_time = time.time()
        #using gensim function to split the text into tokens
        tweets_table["text_tokens"] = tweets_table["text"].apply(gensim.utils.simple_preprocess,{"deacc":True, "min_len":2,"max_len":25})

        #remove stopwords:
        def remove_stopwords(tokens, stopwords):
            return [token for token in tokens if token not in stopwords]
        tweets_table['text_tokens'] = tweets_table['text_tokens'].apply(remove_stopwords, stopwords=stopwords)

        ################################## add bygrams to the tokens
        #print(f"connector words: {gensim.models.phrases.ENGLISH_CONNECTOR_WORDS}")
        ## train bygram model
        bigram = gensim.models.Phrases(tweets_table['text_tokens'], min_count=2, threshold=2, connector_words=gensim.models.phrases.ENGLISH_CONNECTOR_WORDS)
        bigram_model = gensim.models.phrases.Phraser(bigram)
        if verbose: print(f"found {len(bigram_model.phrasegrams)} bigrams")
        # bigram_model.phrasegrams #the bygrams the model found
        tweets_table['text_tokens'] = tweets_table['text_tokens'].apply(lambda x: bigram_model[x])
        ###### add trigram to the tokens
        trigram = gensim.models.Phrases(tweets_table['text_tokens'], min_count=2, threshold=1, connector_words=gensim.models.phrases.ENGLISH_CONNECTOR_WORDS)
        trigram_model = gensim.models.phrases.Phraser(trigram)
        if verbose: print(f"found {len(trigram_model.phrasegrams)} trigram")
        #trigram_model.phrasegrams #the trigram that the model found
        tweets_table['text_tokens'] = tweets_table['text_tokens'].apply(lambda x: trigram_model[x])
        ############################################################################
        ###### add forthgram to the tokens
        forthgram = gensim.models.Phrases(tweets_table['text_tokens'], min_count=2, threshold=6, connector_words=gensim.models.phrases.ENGLISH_CONNECTOR_WORDS)
        forthgram_model = gensim.models.phrases.Phraser(forthgram)
        if verbose: print(f"found {len(forthgram_model.phrasegrams)} forthgram")
        #forthgram_model.phrasegrams #the trigram that the model found
        tweets_table['text_tokens'] = tweets_table['text_tokens'].apply(lambda x: forthgram_model[x])
        ############################################################################
        ### add tweet date column
        def take_only_10_first_char(x):
            return(x[0:10])
        tweets_table["created_at_date"] = tweets_table["created_at"].apply(take_only_10_first_char)
        tweets_table["created_at_date"] = pd.to_datetime(tweets_table["created_at_date"])

        ### add column is_in_special_date that checks wheter the tweet was published in a special event day
        tweets_table['is_in_special_date'] = tweets_table['created_at_date'].apply(lambda x : pd.Series(x).isin(events_table["Date"]).any())

        ### Joining the event table so we can get additional information for the special events
        tweets_table = tweets_table.merge(events_table, left_on = "created_at_date", right_on = "Date", how = "left")
        tweets_table.rename(columns = {'Date':'Event_Date'}, inplace = True)
        tweets_table['Event_Date'] = tweets_table['Event_Date'].fillna("No-Event")

        ### Joining the KOP table so we can get additional information for the KOP
        tweets_table = tweets_table.merge(KOP_table, left_on = "author_id", right_on = "author_id", how = "left")
        try:
            tweets_table['KOP_num'] = tweets_table['KOP_num'].fillna("No-KOP")
            tweets_table['Index'] = tweets_table['Index'].fillna("No-KOP")
            tweets_table['Name'] = tweets_table['Name'].fillna("No-KOP")
            tweets_table['Born_in'] = tweets_table['Born_in'].fillna("No-KOP")
            tweets_table['Role'] = tweets_table['Role'].fillna("No-KOP")
            tweets_table['Place'] = tweets_table['Place'].fillna("No-KOP")
        except: print()

        if verbose: print("\nFinish preprocessing the tweets table, it took:", round(time.time() - start_time,3), "seconds")

        ############# step 6 - Scoring #############
        if verbose: print("Step 6: Scoring the Tweets")

        KOP_ids = list(set(KOP_table.author_id))

        ### the following scorer - count the number of times the key words apprear in a certain text. If a certain word (brexit)
        # appear more than once, it will be counted twice
        def scorer_keywords_brexit(tweet_tokens, key_words):
            #scoring the keywords:
            count_key_words = 0
            for word in key_words:
                count_key_words += tweet_tokens.count(word)
            return count_key_words
        ##########################################################################################################
        def scorer_KOP_brexit(author_id, KOP_ids):
            if author_id in KOP_ids:
                score = 1
            else:
                score = 0
            return score
        ##########################################################################################################
        ### adding year column
        #tweets_table["Year_tweet"] = pd.DatetimeIndex(tweets_table['created_at']).year
 
        ### scoring key-words
        tweets_table["score_key_words"] = tweets_table['text_tokens'].apply(scorer_keywords_brexit, key_words = key_words)

        #scoring KOP: if the author is KOP then the score in this column will be 1, else 0
        tweets_table["score_KOP"] = tweets_table['author_id'].apply(scorer_KOP_brexit, KOP_ids = KOP_ids)

        ### scoring events - column is_in_special_date

        #tweets_table["total_score"]: adding the weights of each scorer
        tweets_table["total_score"] = score_for_key_words*tweets_table['score_key_words'] + score_for_key_event*tweets_table["is_in_special_date"] + score_for_KOP*tweets_table["score_KOP"]

        #Geting a table with all the tweets that passed the score threshold
        tweets_table_filtered = tweets_table[tweets_table["total_score"]>=threshold_score].copy()
        #Sort the filtered table by score such that the tweets with the highest score will be first
        tweets_table_filtered.sort_values(by = "total_score", ascending=False, inplace=True)

        print("\nFinish!\nTotal time:", round(time.time() - start_fun_time,3),
            "Seconds (",round((time.time() - start_fun_time)/60,3), "Minutes)")
            
        bigrams_models = [bigram, trigram, forthgram]
        return (tweets_table_filtered, tweets_table, csv_files_evaluated, bigrams_models)


##########################################################################################################
#### return tweets given query


    def return_tweets_given_query(self, query="", user_name=None,
                                            start_time = "2015-12-7T00:00:00Z",
                                            end_time = "2021-12-26T00:00:00Z",
                                            max_results = 10, evaluate_last_token = False,
                                            limit_amount_of_returned_tweets = 10000000,
                                           verbose_10 = False, dir_name = "tweets_by_query", csv_table_name = "brexit"):
        """ ## Return Tweets of given query

This function enalbes getting all the tweets that follow the given query.\n

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

+ link to twitter-developer page regarding building a query:
https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query

### App rate limit:
        - App rate limit (OAuth 2.0 App Access Token): 300 requests per 15-minute window shared among all users of your app
        - App rate limit (OAuth 2.0 App Access Token): 1 request per second shared among all users of your app
        
Parameters
- query : str --> You can see the full documentation on how to build a query (what to pass in the `query` argument) in the following link:\n
https://developer.twitter.com/en/docs/twitter-api/tweets/counts/integrate/build-a-query
        
- dir_name: by defualy "tweets" --> the dir name to put all the data from the function

- start_date = The start date is the date that from it the function will look and rerieve tweets.\n
Note that the format of the start time should be: "2015-12-7T00:00:00Z" (this is the default)

- end_date = The end date is the date that till it the function will look and rerieve tweets.\n
Note that the format of the end time should be: "2021-12-26T00:00:00Z" (this is the default)

- max_results = The max number of tweets to retrieve in a given call. Must be an integer between 10 to 500.
- evaluate_last_token - by default = False--> If you have already retrive dataand you wish to continue retriving from the place you stopped, pass "True" to this arguemnt.

- limit_amount_of_returned_tweets - by default = 10000000 --> Lets say a given account had 5000 tweets in the given timeframe (from the given start to the given end date), and you wish to get only the first 2000, then pass to this arguemnt 2000. It will automatically stop the function when it reaches the `limit_amount_of_returned_tweets` you provided

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    

- csv_table_name - the csv name that you wish to give to the table that the function generates. Note that this name will also be the name of the log dir that will contain the tokens and the tweets-json file. This is important as if you wish to continue searching for more tweets of the same query, you need to provide the same csv table name and of course write "True" in the argument: evaluate_last_token
        """
        search_url = "https://api.twitter.com/2/tweets/search/all" #endpoint use to collect data from

        #handling case where the user entered a max_result that is not between 10 and 500
        if max_results > 500:
            max_results = 500
            print('max_results can not be greater than 500, changed to 500')
        if max_results < 10:
            max_results = 10
            print('max_results can not be smaller than 10, changed to 10')
        #creating a directory tat will contain the csv file + the log directory of the Key Opinion Leader
        import os.path
        try:
            os.mkdir(dir_name)
            print("creating directory", dir_name, "to insert the table with the tweets for the given query")
        except:
            print("The dir", dir_name ,"already exist")

        if user_name is not None:
            query = str(query) + " from:" + str(user_name)
            try: #displaying with print the start and end time + the user name that the function will try to retirve tweets
                display_start_time = datetime.strptime(start_time.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")
                display_end_time = datetime.strptime(end_time.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")
            except:
                display_start_time = start_time
                display_end_time = end_time
            print("Bringing all the tweets of the user:", user_name, "from:", display_start_time, "to", display_end_time)
            print()

            ##### Creating the log directory (that will contain 3 files: The token file, the retriving tweets streem and the full json file)
        import os.path
        dir_log_name = os.path.join(dir_name, "log_tweets")

        # Try creating the directory for the logs, if the path exist don't create a new one. Print in either case What happened
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the tweets")
        except:
            print("The dir", dir_log_name ,"already exist")
        ######################## creating a path for the specific user that we wish to retirve his tweets
        path_for_log_dir_of_certain_query = os.path.join(dir_log_name, csv_table_name)
        # Try creating the directory for the specific user, if the path exist don't create a new one. Print in either case What happened
        try:
            os.mkdir(path_for_log_dir_of_certain_query)
            print("creating directory", path_for_log_dir_of_certain_query,"in the dir",dir_log_name, "to insert all the logs of the QUERY", csv_table_name)
        except:
            print("The dir", path_for_log_dir_of_certain_query ,"already exist")
        ### creating the log-text-file of the "retriving_tweets_streem" This log file will contain a time-stamp
        # of the time you activated the function, and in each call to twitter API it will write in that log-file
        # the number of tweets that the function retirved in that call + the totla number of tweets retrived so far.
        # With this text file you can follow up in any time the function runs what is the status of the call - 
        # you can see how many tweets have been collected on a specifc user and know that the function works fine.
        path_for_dir_retriving_tweets_streem = os.path.join(path_for_log_dir_of_certain_query, 'retriving_tweets_streem.txt')
        with open(path_for_dir_retriving_tweets_streem, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')

        # Opening the Tokens text-file (if not exist)
        ########### If the token file exist already, then take the last token available, else start from token 1  ############
        tokens_location = os.path.join(dir_log_name,csv_table_name, "tokens.txt")

        if (evaluate_last_token == True and os.path.isfile(tokens_location) == True):
            a_file = open(tokens_location, "r")
            lines = a_file.readlines()
            last_lines = lines[-2]
            next_token = last_lines[0:-1]
            a_file.close()
        else:
            next_token = None

        ################ Add a time stamp ########################################
        path_for_dir_tokens = os.path.join(path_for_log_dir_of_certain_query, 'tokens.txt')
        with open(path_for_dir_tokens, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time+ '\n\n')

        ############################################# The main for loop #############################################

        continue_searching = True #logical variable that controls the for loop, as long as it is True, the function will keep trying to retrive tweets
        json_response_list = [] #list containing all the json responses the function got. In each loop we are
        #saving that list in the log-json file (so if there was a problem in a certain loop, we would have all the jsons till that problematic loop)
        next_tokens = [] #list containing all the tokens
        num_of_returned_tweets = 0 # counter of returned tweets
        counter_loops = 0 #counter of the loops - the number of calls to twitter API

        while continue_searching == True and num_of_returned_tweets < limit_amount_of_returned_tweets:
            counter_loops +=1
            if counter_loops > 1:
                next_token = json_response["meta"]["next_token"]
                query_params["next_token"] = next_token
                #if verbose_10:
                #    print("token to insert:",next_token)
            #if the returned amount of tweets is getting close to the limit number, we need to alter the max_result,
            #so we won't get tweets beyond what we asked
            if (limit_amount_of_returned_tweets - num_of_returned_tweets) < max_results:
                max_results = limit_amount_of_returned_tweets - num_of_returned_tweets
                if max_results < 10:
                    max_results = 10
            else :
                max_results = max_results

            #change params based on the endpoint you are using
            query_params = {'query': query,
                        'start_time': start_time,
                        'end_time': end_time,
                        'max_results': max_results,
                        'expansions': 'author_id,in_reply_to_user_id,geo.place_id,entities.mentions.username,referenced_tweets.id',
                        'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                        'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                        'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                        'next_token': {next_token}}

            json_response = self.__connect_to_endpoint(url = search_url,params= query_params, next_token = next_token)

            json_response_list.append(json_response) #the first json_response itme
            num_of_returned_tweets += json_response["meta"]["result_count"]

            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                b = pd.json_normalize(json_response["includes"], ["users"]).add_prefix("users.")

                a.conversation_id = a.conversation_id.astype("string")
                a.id = a.id.astype("string")
                a["id_new"] = "id: " + a["id"].astype("string")
                a["conv_id_new"] = "conv_id: " + a["conversation_id"].astype("string")
                a["author_id_new"] = "author_id: " + a["author_id"].astype("string")

            #c = pd.json_normalize(json_response["includes"]["places"]).add_prefix("places.")
                df_tweets_i = pd.merge(a, b, left_on="author_id", right_on="users.id")
                list_of_cols_to_add = ['author_id', "author_id_new", 'conversation_id', "conv_id_new",
                                        "id", "id_new",'created_at','entities.mentions',
                            'public_metrics.like_count', 'public_metrics.quote_count',
                        'public_metrics.reply_count', 'public_metrics.retweet_count','referenced_tweets', 'text',
                            'users.created_at', 'users.description','users.id', 'users.name',
                        'users.public_metrics.followers_count', 'users.public_metrics.following_count',
                        'users.public_metrics.listed_count', 'users.public_metrics.tweet_count',
                        'users.username', 'users.verified']

                list_cols_to_drop = [x for x in df_tweets_i.columns if x not in list_of_cols_to_add]

                ##droping labels (columns) we don't need
                df_tweets_i = df_tweets_i.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                #sort columns by alphabetic order
                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)

                #This will be the csv file name that will contain all the tweets of the specific user:
                name =  csv_table_name + ".csv"
                path_for_table = os.path.join(dir_name, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)
            except:
                print("no data / include in the json")

            ### save all the json responses in json file:
            path_for_dir_all_json_responses = os.path.join(path_for_log_dir_of_certain_query, 'all_json_responses.json')
            with open(path_for_dir_all_json_responses, 'w') as outfile:
                json.dump(json_response_list, outfile)

            ### Writing in the retrieving tweets log file the number of retrieved tweets + status - is the function finished running or keep retrieving more tweets?
            with open(path_for_dir_retriving_tweets_streem, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(json_response["meta"]["result_count"]) + " tweets, and there are more tweets of that user to get, I am bringing more tweets!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_tweets)
                f.write(print_total+ '\n\n')

            if "next_token" in json_response["meta"]:
                if (verbose_10 == True and counter_loops % 20 == 1):
                    print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                #elif verbose_10 == False:
                    #print(counter_loops, "Got from twitter", json_response["meta"]["result_count"], "tweets, and there are more tweets of that user to get, I am bringing more tweets!\n")
                next_token = json_response["meta"]["next_token"]
                query_params["next_token"] = next_token
                next_tokens.append(next_token)
                #ids_token_print = "next token = " + next_token + "newest id: " + json_response["meta"]["newest_id"] + " | oldest id: " + json_response["meta"]["oldest_id"]
                ids_token_print = next_token
                with open(path_for_dir_tokens, 'a') as f:
                    f.write(ids_token_print + '\n\n')
            else:
                print("no more tweets from this user")
                continue_searching = False
                print("Total amount of collected tweets = ", num_of_returned_tweets)

            if num_of_returned_tweets >=limit_amount_of_returned_tweets:
                print("oooops, There may be more tweets to return, but you asked to limit the amount of returned tweets")
                print("infact you got", num_of_returned_tweets, "returned tweets and limited the function to get", limit_amount_of_returned_tweets, "tweets")

            #In what case we suspect that there may be more tweets that we didn't get? -->
            #When the number of tweets we asked to get is equal to the number of tweets we got back

        return json_response_list, num_of_returned_tweets, next_tokens

##########################################################################################################
#### return tweets given tweet ids


    def return_tweets_given_tweet_ids_new(self, tweet_ids=[], number_of_tweets_in_batch = 100,
                                           verbose_10 = False, dir_name = "tweets_by_tweet_ids",
                                  csv_table_name = "brexit_tweet_ids", api_error_sleep_secs = 60):
        """ ## Return Tweets of of given tweet ids

This function enalbes getting all the tweets that are in a list of given tweet ids.\n

+ link to twitter-developer page regarding this capability:
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

### App rate limit:
        - App rate limit (Application-only): 900 requests per 15-minute window shared among all users of your app
        - User rate limit (User context): 900 requests per 15-minute window per each authenticated user
        
Parameters
- tweet_ids - a list with tweet ids (must be a list of strings)

- dir_name: by defualy "tweets_by_tweet_ids" --> the dir name to put all the data from the function

- number_of_tweets_in_batch = The max number of tweets to retrieve in a given call. Must be an integer between 1 to 100.

- verbose_10 - by default = False --> If True then the function will print certain things throught the run of the function.    

- csv_table_name - the csv name that you wish to give to the table that the function generates. Note that this name will also be the name of the log dir that will contain the tokens and the tweets-json file. This is important as if you wish to continue searching for more tweets of the same query, you need to provide the same csv table name
        """
        search_url = "https://api.twitter.com/2/tweets/?ids=X" #endpoint use to collect data from
        
        #creating a directory that will contain the csv file + the log directory of the Key Opinion Leader
        import os.path
        try:
            os.mkdir(dir_name)
            print("creating directory", dir_name, "to insert the tables with the tweets for the given tweet-ids")
        except:
            print("The dir", dir_name ,"already exist")
        
    ##### Creating the log directory (that will contain 3 files: The token file, the retriving tweets streem and the full json file)
        dir_log_name = os.path.join(dir_name, "log_tweets")

        # Try creating the directory for the logs, if the path exist don't create a new one. Print in either case What happened
        try:
            os.mkdir(dir_log_name)
            print("creating directory", dir_log_name, "to insert all the logs of the tweets")
        except:
            print("The dir", dir_log_name ,"already exist")
        ######################## creating a path for the specific user that we wish to retirve his tweets
        path_for_log_dir_of_certain_query = os.path.join(dir_log_name, csv_table_name)
        # Try creating the directory for the specific user, if the path exist don't create a new one. Print in either case What happened
        try:
            os.mkdir(path_for_log_dir_of_certain_query)
            print("creating directory", path_for_log_dir_of_certain_query,"in the dir",dir_log_name, "to insert all the logs of the QUERY", csv_table_name)
        except:
            print("The dir", path_for_log_dir_of_certain_query ,"already exist")
        ### creating the log-text-file of the "retriving_tweets_streem" This log file will contain a time-stamp
        # of the time you activated the function, and in each call to twitter API it will write in that log-file
        # the number of tweets that the function retirved in that call + the totla number of tweets retrived so far.
        # With this text file you can follow up in any time the function runs what is the status of the call - 
        # you can see how many tweets have been collected on a specifc user and know that the function works fine.
        path_for_dir_retriving_tweets_streem = os.path.join(path_for_log_dir_of_certain_query, 'retriving_tweets_streem.txt')
        with open(path_for_dir_retriving_tweets_streem, 'a') as f:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S (Date: %d.%m.%y)")
            current_time = "Current Time: " + current_time + "   *****************************************   "
            f.write(current_time + '\n\n')
        
        ############################################################################
        ### splitting the tweet_ids into batches
        n = number_of_tweets_in_batch
        if n > 100:
            n = 100
            print('Each batch can contain a max of 100 tweet-ids, changed to 100')
        if n < 1:
            n = 1
            print('Each batch must contain a minimum of 1 tweet-id, changed to 1')
        
        batches=[tweet_ids[i:i + n] for i in range(0, len(tweet_ids), n)]
        num_of_returned_tweets = 0 # counter of returned tweets
        problematic_batches = [] #save all the batches that weren't evaluated
        
        from tqdm.notebook import tqdm_notebook
        json_response_list = []
        json_response_list_all_batches = []
        counter_loops = 0
        for batch in tqdm_notebook(batches):
            search_url = "https://api.twitter.com/2/tweets/?ids=X"
            #print(batch)
            counter_loops +=1
            search_url, query_params = self.create_url_tweet_ids(search_url , batch)
            #print(search_url)
            try:
                json_response = self.__connect_to_endpoint(url = search_url, params= query_params)
            except Exception as e:
                print(f'Twitter API error: {e} \n Sleeping 15 min from {datetime.datetime.now()}')
                time.sleep(api_error_sleep_secs)
                problematic_batches.append(batch)

            json_response_list.append(json_response) #the first json_response itme
            
            ##### making a dataframe out of the json response:
            try:
                a = pd.json_normalize(json_response["data"])
                b = pd.json_normalize(json_response["includes"], ["users"]).add_prefix("users.")

                a.conversation_id = a.conversation_id.astype("string")
                a.id = a.id.astype("string")
                a["id_new"] = "id: " + a["id"].astype("string")
                a["conv_id_new"] = "conv_id: " + a["conversation_id"].astype("string")
                a["author_id_new"] = "author_id: " + a["author_id"].astype("string")

            #c = pd.json_normalize(json_response["includes"]["places"]).add_prefix("places.")
                df_tweets_i = pd.merge(a, b, left_on="author_id", right_on="users.id")
                list_of_cols_to_add = ['author_id', "author_id_new", 'conversation_id', "conv_id_new",
                                        "id", "id_new",'created_at','entities.mentions',
                            'public_metrics.like_count', 'public_metrics.quote_count',
                        'public_metrics.reply_count', 'public_metrics.retweet_count','referenced_tweets', 'text',
                            'users.created_at', 'users.description','users.id', 'users.name',
                        'users.public_metrics.followers_count', 'users.public_metrics.following_count',
                        'users.public_metrics.listed_count', 'users.public_metrics.tweet_count',
                        'users.username', 'users.verified']

                list_cols_to_drop = [x for x in df_tweets_i.columns if x not in list_of_cols_to_add]

                ##droping labels (columns) we don't need
                df_tweets_i = df_tweets_i.drop(labels=list_cols_to_drop, axis = 1, errors = "ignore")

                for col in list_of_cols_to_add:
                    if col not in df_tweets_i.columns:
                        df_tweets_i[col] = "NA"

                #sort columns by alphabetic order
                col_list_df_tweets_i = df_tweets_i.columns.tolist()
                col_list_df_tweets_i.sort()
                df_tweets_i = df_tweets_i.reindex(columns=col_list_df_tweets_i)
                
                num_of_returned_tweets += df_tweets_i.shape[0]
                #This will be the csv file name that will contain all the tweets of the specific user:
                name =  csv_table_name + ".csv"
                path_for_table = os.path.join(dir_name, name)
                if os.path.isfile(path_for_table) == False: #if this is the first table of tweets
                    df_tweets_i.to_csv(path_for_table, index=True)
                else:
                    df_tweets_i.to_csv(path_for_table, mode='a', index=True, header=False)
                    
                number_of_read_tweets_for_printing = df_tweets_i.shape[0]
                
                #display(df_tweets_i)
                
                ### document the tweet ids that were succsefuly evaluted:
                path_for_evaluated_tweet_ids = os.path.join(path_for_log_dir_of_certain_query, 'evaluated_tweet_ids.txt')
                with open(path_for_evaluated_tweet_ids, 'a') as f:
                    for tweet_id in batch:
                        f.write(tweet_id+'\n')

            except:
                print("no data / include in the json")
                number_of_read_tweets_for_printing = 0
                path_for_not_evaluated_tweet_ids = os.path.join(path_for_log_dir_of_certain_query, 'Problematic_tweet_ids.txt')
                with open(path_for_not_evaluated_tweet_ids, 'a') as f:
                    for tweet_id in batch:
                        f.write(tweet_id+'\n')
            ### save all the json responses in json file:
            path_for_dir_all_json_responses = os.path.join(path_for_log_dir_of_certain_query, 'all_json_responses.json')
             
            if os.path.isfile(path_for_dir_all_json_responses) == False: #if this is the first json of tweets
                with open(path_for_dir_all_json_responses, 'w') as outfile:
                    json.dump(json_response_list, outfile)
            else:
                with open(path_for_dir_all_json_responses, 'a') as outfile:
                    json.dump(json_response_list, outfile)

            ### Writing in the retrieving tweets log file the number of retrieved tweets + status - is the function finished running or keep retrieving more tweets?
            with open(path_for_dir_retriving_tweets_streem, 'a') as f:
                print_stat = str(counter_loops) + " -> Got from twitter " + str(number_of_read_tweets_for_printing) + " tweets, and there are more tweets of that user to get, I am bringing more tweets!"
                f.write(print_stat+'\n')
                print_total = "Total amount of tweets: " + str(num_of_returned_tweets)
                f.write(print_total+ '\n\n')

        return json_response_list, num_of_returned_tweets, problematic_batches



