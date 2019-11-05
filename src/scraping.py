import json
import csv
import tweepy
import re
import os
import argparse
import time
import pandas as pd
from pprint import pprint

api = None


def authenticate():
    """
        Quick function to authenticate, whenever in the code you are

        api is a singleton var
    """
    global api

    if 'TWITTER_KEY' not in os.environ:
        consumer_key = input('Consumer Key ')
        consumer_secret = input('Consumer Secret ')
        access_token = input('Access Token ')
        access_token_secret = input('Access Token Secret ')
    else:
        consumer_key = os.environ['TWITTER_KEY']
        consumer_secret = os.environ['TWITTER_SECRET']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

    #create authentication for accessing Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    #initialize Tweepy API
    api = tweepy.API(auth)



def limit_handled(cursor):
    """
    # In this example, the handler is time.sleep(15 * 60),
    # but you can of course handle it in any way you want.
    """

    while True:
        try:
            yield cursor.next()
        # except tweepy.RateLimitError:
        #     print("Rate Limit exceeded, waiting 15 min")
        #     print(api.rate_limit_status())
        #     time.sleep(15 * 60)
        except tweepy.TweepError as e:
            # pprint(dir(e))
            # print(e.api_code)
            # print(type(e.response))
            # print(e.reason)
            if '429' in e.reason:
                print("Rate Limit exceeded, waiting 15 min")
                #pprint(api.rate_limit_status())
                time.sleep(15 * 60)





def retrieve_all_tweets_from_account(account_name):
    """
    INPUTS:
        account_name: 
    OUTPUTS:
        none, simply save the tweet info to a spreadsheet
    """   

    global api
    if api is None:
        authenticate()

    #get the name of the spreadsheet we will write to
    fname =  account_name

    #open the spreadsheet we will write to
    with open('%s.csv' % (fname), 'w') as file:

        w = csv.writer(file)

        #write header row to spreadsheet
        w.writerow(['timestamp', 'tweet_id', 'tweet_text', 'username', 'all_hashtags', 'followers_count'])

        #for each tweet matching our hashtags, write relevant info to the spreadsheet
        for tweet in limit_handled(
            tweepy.Cursor(
                api.user_timeline, 
                id=account_name,
                ).items()):

            # interesting fields
            """
                favorite
                coordinates
                in_reply_to_user_id_str
                in_reply_to_status_id_str
                is_quote_status
                quoted_status_id_str
                retweet
                lang
                parse?
                parse_list?

                text
                user

            """

            # filters: remove retweets, remove favorites

            print("\n\n")
            print(dir(tweet))
            w.writerow([
                tweet.created_at,
                tweet.id, 
                tweet.text.replace('\n',' ').encode('utf-8'), 
                tweet.user.screen_name.encode('utf-8'), 
                [e['text'] for e in tweet._json['entities']['hashtags']], 
                tweet.user.followers_count
                ])



def search_for_hashtags(hashtag_phrase):
    """
    INPUTS:
        hashtag_phrase: the combination of hashtags to search for
    OUTPUTS:
        none, simply save the tweet info to a spreadsheet
    """   

    global api
    if api is None:
        authenticate()

    #get the name of the spreadsheet we will write to
    fname = '_'.join(re.findall(r"#(\w+)", hashtag_phrase))

    #open the spreadsheet we will write to
    with open('%s.csv' % (fname), 'w') as file:

        w = csv.writer(file)

        #write header row to spreadsheet
        w.writerow(['timestamp', 'tweet_text', 'username', 'all_hashtags', 'followers_count', 'tweet_id'])

        #for each tweet matching our hashtags, write relevant info to the spreadsheet
        for tweet in limit_handled(
            tweepy.Cursor(
                api.search, 
                q=hashtag_phrase+' -filter:retweets',
                tweet_mode='extended').items(100)):

            w.writerow([
                tweet.created_at, 
                tweet.full_text.replace('\n',' ').encode('utf-8'), 
                tweet.user.screen_name.encode('utf-8'), 
                [e['text'] for e in tweet._json['entities']['hashtags']], 
                tweet.user.followers_count,
                tweet.id
                ])



def write_row(results_filename, modifier, row_list):
    with open(result_filename, modifier) as f:
        w = csv.writer(f)
        w.writerow(row_list)


def init_results_file(result_filename, modifier, filepath, header_row = [
            'timestamp',
            #'tweet_id', 
            #'tweet_text', 
            'username',
            #'hashtags',
            'num_followers',
            'lang',
            'favorite',
            #'is_quote_status',
            'retweet',
            'to',
            ]):

    with open(result_filename, modifier) as file:
        if filepath is None:
            #write header row to spreadsheet
            write_row(header_row)

        return file

    return None

def search_for_replies_from_user(user_name, limit=1000, filepath=None):

    return search_for_replies(user_name, limit=limit, filepath=filepath, query='from:{}'.format(user_name))



def search_for_replies(user_name, limit=1000, filepath=None, query=None):


    global api
    if api is None:
        authenticate()

    if query is None:
        query = 'to:{}'.format(user_name)
        print("search for replies to:",user_name)
    else:
        print("search for replies from:",user_name)



    #open the spreadsheet we will write to
    if filepath is None:
        result_filename = '../data/graphs/%s.csv' % (user_name+'_replies')
        modifier = 'w'
    else:
        result_filename = filepath
        modifier = 'a'

    found_repliers_list=[]

    init_results_file(result_filename, modifier, filepath)


    for tweet in limit_handled(
            tweepy.Cursor(
                api.search, 
                q=query, 
                tweet_mode='extended'
                ).items(limit)):


            user_screen_name= tweet.user.screen_name#.encode('utf-8')

            #print(dir(tweet))
            write_row(result_filename, modifier,
                [
                tweet.created_at,
                #tweet.id, 
                #tweet.full_text.replace('\n',' ').encode('utf-8'), 
                user_screen_name, 
                #[e['text'] for e in tweet._json['entities']['hashtags']], 
                tweet.user.followers_count,
                tweet.lang,
                tweet.favorited,
                tweet.retweeted,
                user_name,
                ])

            found_repliers_list.append(user_screen_name)


    return result_filename, found_repliers_list
    #return None, found_repliers_list




def search_for_tweet_replies(tweet_id, user_name):
    """
    INPUTS:
       tweet_id
    OUTPUTS:
        none, simply save the tweet info to a spreadsheet
    """   

    print("search for replies to:",tweet_id,user_name)
    global api
    if api is None:
        authenticate()

    #get the name of the spreadsheet we will write to
    fname = tweet_id

    #open the spreadsheet we will write to
    with open('%s.csv' % (fname), 'w') as file:

        w = csv.writer(file)


        #write header row to spreadsheet
        w.writerow(['timestamp', 'tweet_text', 'username'])


        replies = tweepy.Cursor(
            api.search, 
            q='to:{}'.format(user_name),
            since_id=int(tweet_id), 
            tweet_mode='extended').items(100)
        
        while True:
            try:
                reply = replies.next()
                if not hasattr(reply, 'in_reply_to_status_id_str'):
                    continue
                if reply.in_reply_to_status_id == tweet_id:
                   print("\n\n",dir(reply))

                   w.writerow([reply.created_at, reply.full_text.replace('\n',' ').encode('utf-8'), reply.user.screen_name.encode('utf-8')])

            except tweepy.RateLimitError as e:
                print("Twitter api rate limit reached".format(e))
                time.sleep(15*60)
                continue

            except tweepy.TweepError as e:
                print("Tweepy error occured:{}".format(e))
                break

            except StopIteration:
                break

            except Exception as e:
                print("Failed while fetching replies {}".format(e))
                break



def get_users_from_csv(filename):

    df = pd.read_csv(filename, encoding='utf-8')

    # seems that tweepy return b'Username', but it's a string not a byte string...
    # artificially redo? or it's because of the emojis that can appear in the name??
    # for the moment let's keep it that way. It can be modified for presentation purposes


    #pprint(df)
    #print("\n\n",df.columns,"\n\n")
    #pprint(df['username'])
    #pprint(list(set(df['username'].tolist())))
    
    return list(set(df['username'].tolist()))



def update_repliers(new_repliers, repliers1,repliers_old):
    """ 
        APPENDS  elements of replierts1 to new_repliers if they are not already present in new_repliers or replierts_old

    """

    # add elemens of list 2 without repetition
    for e in set(repliers1):
        if e not in repliers_old:
            new_repliers.append(e)


    return list(set(new_repliers))






def graph_retrieval(depth=1, breadth=100):
    """
        Retrieve users and replies in a graph data structure
        - select 4-5 politicians
        - for each:
            - get their replies in a separate csv
            - limit to 100
            - extract list of users ids' from csv
            - for each id
                - get the replies to this id
                - limit to 100
                - save in the same csv file
    """



    origins = [
        'Santi_ABASCAL',
        #'vox_es',
        # 'ivanedlm',
        # 'monasterioR',
        # 'hermanntertsch',
        # 'Ortega_Smith'
    ]

    for account in origins:
        # search for replies and write a csv file
        #    limit to 100
        filename, repliers = search_for_replies(account, limit=breadth)
        
        # extract the list of users from the csv
        #repliers = get_users_from_csv(filename)
        repliers = list(set(repliers))
        print(account, " repliers: ", repliers)

        pending_repliers=[]
        new_repliers=repliers
        treated_repliers=[]
        #auxiliar var
        repliers2=[]
        for recursion_level in range(depth):

            # fill the current level list
            pending_repliers = list(new_repliers)
            # initialize the next level list
            new_repliers = []
    
            print("++++ recursion level=",recursion_level,"++++ ")
            print("-> done_repliers")
            pprint(treated_repliers)
            print("-> pending_repliers")
            pprint(pending_repliers)

            
            avoid_repeating_list = list(treated_repliers)
            avoid_repeating_list.extend(pending_repliers)
            avoid_repeating_list = list(set(avoid_repeating_list))
            print("avoid repeating list")
            pprint(avoid_repeating_list)

            # for each replying user
            for replier in pending_repliers:
                # get the replies and write to the specific csv
                filename1, repliers1= search_for_replies(replier,limit=breadth, filepath=filename)
                
                # limit to 100
                filename2, repliers2=search_for_replies_from_user(replier,limit=breadth, filepath=filename)

                # fill the next recursion level repliers list
                repliers1.extend(repliers2)
                new_repliers = update_repliers(new_repliers, repliers1,avoid_repeating_list)


            # save treated repliers to done repliers
            treated_repliers = update_repliers(treated_repliers, pending_repliers, [])


        print("FINAL repliers list ")
        treated_repliers.extend(new_repliers)
        treated_repliers = list(set(treated_repliers))
        pprint(treated_repliers)




if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument("option", help="what function to run")
    args = parser.parse_args()


    if args.option == 'hashtag':
        hashtag_phrase = input('Hashtag Phrase: ')
        search_for_hashtags(hashtag_phrase)

    elif args.option == 'tweets':
        account = input('Account name: ')
        retrieve_all_tweets_from_account(account)


    elif args.option == 'replies_old':
        # also applicable but longer to execute
        account = input('Account name: ')
        if not account:
            account = '@Albert_Rivera'
        tweet_id = input('Tweet id: ')
        if not tweet_id:
            tweet_id = '1190196980963848193'
        search_for_tweet_replies(tweet_id,account)

    elif args.option == 'replies':
        account = input('Account name: ')
        if not account:
            account = '@Albert_Rivera'
        search_for_replies(account)

    elif args.option == 'graph':
        graph_retrieval(depth=3,breadth=2)   