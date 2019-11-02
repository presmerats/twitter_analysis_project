import json
import csv
import tweepy
import re
import os

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
        except tweepy.RateLimitError:
            print("Rate Limit exceeded, waiting 15 min")
            print(api.rate_limit_status())
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



def search_for_replies(user_name):

    print("search for replies to:",user_name)
    global api
    if api is None:
        authenticate()



    #open the spreadsheet we will write to
    with open('%s.csv' % (user_name+'_replies'), 'w') as file:

        w = csv.writer(file)

        #write header row to spreadsheet
        w.writerow([
            'timestamp',
            'tweet_id', 
            'tweet_text', 
            'username',
            'hashtags',
            'num_followers',
            'lang',
            'favorite',
            #'is_quote_status',
            'retweet',
            ])

        for tweet in limit_handled(
                tweepy.Cursor(
                    api.search, 
                    q='to:{}'.format(user_name), 
                    tweet_mode='extended'
                    ).items(5000)):

                #print(dir(tweet))
                w.writerow([
                    tweet.created_at,
                    tweet.id, 
                    tweet.full_text.replace('\n',' ').encode('utf-8'), 
                    tweet.user.screen_name.encode('utf-8'), 
                    [e['text'] for e in tweet._json['entities']['hashtags']], 
                    tweet.user.followers_count,
                    tweet.lang,
                    tweet.favorited,
                    tweet.retweeted,
                    ])




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


if __name__ == '__main__':
    
    #hashtag_phrase = input('Hashtag Phrase: ')
    #search_for_hashtags(hashtag_phrase)

    #account = input('Account name: ')
    #retrieve_all_tweets_from_account(account)


    ## also applicable but longer to execute
    # account = input('Account name: ')
    # if not account:
    #     account = '@Albert_Rivera'
    # tweet_id = input('Tweet id: ')
    # if not tweet_id:
    #     tweet_id = '1190196980963848193'
    # search_for_tweet_replies(tweet_id,account)

    account = input('Account name: ')
    if not account:
        account = '@Albert_Rivera'
    search_for_replies(account)