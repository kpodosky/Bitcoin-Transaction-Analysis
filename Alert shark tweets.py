import time
import tweepy
import logging
from alert_pricebar import test_display as btc_price_display
from eth_pricebar import test_display as eth_price_display
from btc_monitor import BitcoinWhaleTracker  # Fixed import path
from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret

class TwitterBot:
    def __init__(self):
        # Use Twitter API v2 authentication
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Test authentication
        try:
            me = self.client.get_me()
            print(f"Authentication OK - User ID: {me.data.id}")
        except Exception as e:
            print("Error during authentication:", str(e))
            raise
            
        self.whale_tracker = BitcoinWhaleTracker(min_btc=1000)  # Changed to 1000 BTC minimum
        
        # Updated known exchange names to filter for
        self.known_exchanges = [
            'binance', 'coinbase', 'kraken', 'bybit', 
            'huobi', 'okex', 'kucoin', 'bitfinex',
            'exchangex'  # Added ExchangeX
        ]
        
        # Add high-risk entity tracking
        self.high_risk_entities = [
            'lazarus_group',
            'exchangex',
            'stolen_funds'
        ]
        
        # Add priority alert thresholds
        self.alert_thresholds = {
            'normal': 1000,  # Regular whale transfers (updated from 500)
            'high_risk': 100  # Lower threshold for suspicious transfers
        }
        
        # Add timeout settings
        self.timeouts = {
            'btc_monitor': 30,  # Maximum seconds to wait for BTC monitor
            'price_update': 15,  # Maximum seconds to wait for price updates
            'tweet_delay': 60    # Delay between tweets
        }
        
        # Track last update times
        self.last_updates = {
            'btc_price': 0,
            'eth_price': 0,
            'whale_alert': 0
        }
        
        # Update timing configurations
        self.post_intervals = {
            'btc_price': 900,    # 15 minutes
            'eth_price': 900,    # 15 minutes
            'whale_alert': 300   # 5 minutes
        }
        
        self.wait_times = {
            'after_btc_price': 120,  # 2 minutes
            'after_eth_price': 180,  # 3 minutes
            'between_alerts': 30      # 30 seconds between whale alerts
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('TwitterBot')

    def post_tweet(self, message):
        try:
            # Use v2 create_tweet instead of update_status
            tweet = self.client.create_tweet(text=message)
            self.logger.info(f"Tweet posted successfully with id: {tweet.data['id']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to tweet: {e}")
            return False

    def check_price_update(self):
        """Run and post price status from alert_pricebar.py"""
        try:
            status = btc_price_display()  # Using correct function name
            if status:
                self.logger.info("Price status generated successfully")
                return status
            return None
        except Exception as e:
            self.logger.error(f"Error in price update: {e}")
            return None

    def check_whale_alert(self):
        """Run and post whale alerts with proper timing"""
        try:
            alerts = self.whale_tracker.monitor_transactions()
            
            if alerts:
                for alert in alerts:
                    # High risk check
                    if any(entity in alert.lower() for entity in self.high_risk_entities):
                        alert = "🚨 URGENT ALERT 🚨\n" + alert
                    
                    # Post with delay between alerts
                    if self.post_tweet(alert):
                        self.logger.info(f"Posted whale alert: {alert[:50]}...")
                        time.sleep(self.wait_times['between_alerts'])
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in whale alert: {e}")
            return False

    def check_eth_price(self):
        """Run and post ETH price status"""
        try:
            eth_status = eth_price_display()
            if eth_status:
                self.logger.info("ETH price status generated")
                if self.post_tweet(eth_status):
                    self.logger.info("Posted ETH price update successfully")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error in ETH price update: {e}")
            return False

    def run(self):
        """Main loop with specified sequence and timing"""
        self.logger.info("Starting Twitter Bot...")
        
        while True:
            try:
                current_time = time.time()
                
                # 1. First check BTC price from alert_pricebar.py
                if current_time - self.last_updates['btc_price'] >= self.post_intervals['btc_price']:
                    self.logger.info("Step 1: Checking BTC price from alert_pricebar.py...")
                    btc_status = btc_price_display()
                    if btc_status and self.post_tweet(btc_status):
                        self.last_updates['btc_price'] = current_time
                        self.logger.info("BTC price posted, waiting 2 minutes...")
                        time.sleep(self.wait_times['after_btc_price'])
                
                # 2. Then check ETH price after 2 minutes
                if current_time - self.last_updates['eth_price'] >= self.post_intervals['eth_price']:
                    self.logger.info("Step 2: Checking ETH price...")
                    if self.check_eth_price():
                        self.last_updates['eth_price'] = current_time
                        self.logger.info("ETH price posted, waiting 3 minutes...")
                        time.sleep(self.wait_times['after_eth_price'])
                
                # 3. Finally check BTC monitor after 3 minutes
                if current_time - self.last_updates['whale_alert'] >= self.post_intervals['whale_alert']:
                    self.logger.info("Step 3: Checking BTC monitor...")
                    if self.check_whale_alert():
                        self.last_updates['whale_alert'] = current_time
                        time.sleep(self.wait_times['between_alerts'])
                
                # Small delay before next cycle
                time.sleep(15)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.logger.info("Waiting 30 seconds before retry...")
                time.sleep(30)

if __name__ == "__main__":
    bot = TwitterBot()
    bot.run()