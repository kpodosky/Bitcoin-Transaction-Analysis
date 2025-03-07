import tweepy
from keys import consumer_key, consumer_secret, access_token, access_token_secret

def test_hello_tweet():
    # Set up authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    try:
        # Verify credentials
        api.verify_credentials()
        print("Authentication OK")
        
        # Post a simple tweet
        tweet = api.update_status("Hello from Alert Shark! 🦈")
        print(f"Tweet posted successfully! Tweet ID: {tweet.id}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_hello_tweet()
