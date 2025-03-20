import tweepy
import time
import random
import logging
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cryptoxpress_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CryptoXpressBot")


class CryptoXpressBot:
    """
    Twitter bot for CryptoXpress platform that generates and posts crypto-related content
    using AI text generation APIs.
    """
    
    def __init__(self, twitter_credentials, hf_api_key=None):
        
        self.setup_twitter_api(twitter_credentials)
        self.posted_tweets = set()
        self.load_posted_tweets()
        self.hf_api_key = hf_api_key
        
        # Company info for context
        self.company_info = {
            "name": "CryptoXpress",
            "mission": "Make crypto easy",
            "features": [
                "Trade over 300 cryptocurrencies with 900+ trading pairs",
                "No commissions on trades",
                "Book flights, accommodation, tours with crypto",
                "Pay bills and services with crypto",
                "Digital wallet for cryptocurrency holdings",
                "Bridge between crypto world and everyday life",
                "NFT management",
                "Crypto payments and transfers"
            ]
        }
        
        # AI prompt templates for different tweet styles
        self.prompt_templates = [
            "Write a short, engaging tweet for CryptoXpress about making crypto easy for everyday use. Keep it under 260 characters.",
            "Create a tweet for CryptoXpress highlighting our no-commission trading feature. Keep it under 260 characters.",
            "Write a tweet for CryptoXpress about using crypto for travel bookings. Keep it under 260 characters.",
            "Create a tweet for CryptoXpress about paying bills with crypto. Keep it under 260 characters.",
            "Write an engaging tweet for CryptoXpress about our digital wallet features. Keep it under 260 characters.",
            "Create a tweet for CryptoXpress about managing NFTs in our platform. Keep it under 260 characters.",
            "Write a tweet for CryptoXpress emphasizing our 300+ cryptocurrencies and 900+ trading pairs. Keep it under 260 characters.",
            "Create a tweet for CryptoXpress about being the bridge between crypto and everyday life. Keep it under 260 characters."
        ]
        
        # For hashtags
        self.hashtags = [
            "#CryptoXpress", "#CX", "#Crypto", "#Cryptocurrency", "#NFT", 
            "#Trading", "#CryptoTrading", "#CryptoPayments", "#DigitalWallet",
            "#CryptoTravel", "#CryptoShopping", "#CryptoLife", "#CryptoMadeEasy"
        ]
        
        # Backup tweets in case AI generation fails
        self.backup_tweets = [
            "Buy and sell over 300 cryptocurrencies with 900+ trading pairs using only 3 clicks, without paying any commissions. #CryptoXpress #CryptoMadeEasy",
            "Book flights, accommodation, tours, rental cars and much more directly from CryptoXpress. Your crypto, your travel plans! #CryptoTravel #CX",
            "We're on a mission to make crypto easy! CryptoXpress is the bridge between your crypto world and everyday life. #CryptoXpress #CryptoLife",
            "Pay bills, transfer money, and maintain your cryptocurrency holdings all in one digital wallet. That's the CryptoXpress way! #DigitalWallet #CryptoPayments",
            "Trading crypto shouldn't be rocket science. With CryptoXpress, it's just 3 clicks to buy and sell - commission-free! #CryptoTrading #CX",
            "From NFTs to bill payments, CryptoXpress brings everything together in one best-in-class digital experience. #NFT #CryptoMadeEasy",
            "Why keep your crypto locked away? Use it to book your next vacation with CryptoXpress! #CryptoTravel #CryptoShopping",
            "Over 300 cryptocurrencies, 900+ trading pairs, 0 commissions. That's the CryptoXpress advantage! #CryptoTrading #CX"
        ]
        
    def setup_twitter_api(self, credentials):
        """
        Set up Twitter API connection using tweepy
        """
        try:
            client = tweepy.Client(
                consumer_key=credentials['consumer_key'],
                consumer_secret=credentials['consumer_secret'],
                access_token=credentials['access_token'],
                access_token_secret=credentials['access_token_secret']
            )
            self.twitter_client = client
            logger.info("Twitter API connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Twitter API: {str(e)}")
            raise
            
    def load_posted_tweets(self):
        """
        Load previously posted tweets from a file to avoid duplicates  
        The tweets are stored in posted_tweets.txt, one tweet per line
        """
        try:
            if os.path.exists("posted_tweets.txt"):
                with open("posted_tweets.txt", "r") as f:
                    for line in f:
                        self.posted_tweets.add(line.strip())
                logger.info(f"Loaded {len(self.posted_tweets)} previously posted tweets")
        except Exception as e:
            logger.error(f"Error loading posted tweets: {str(e)}")
    
    def save_posted_tweet(self, tweet_text):
        # Save a tweet to the posted tweets file
        try:
            with open("posted_tweets.txt", "a") as f:
                f.write(tweet_text + "\n")
        except Exception as e:
            logger.error(f"Error saving posted tweet: {str(e)}")
    
    def generate_tweet_with_huggingface(self):
        # Generate tweet content using Hugging Face Inference API
    
        try:
            # Select a random prompt template
            prompt_template = random.choice(self.prompt_templates)
            
            # Create context for the AI
            context = f"""
            CryptoXpress is a platform that makes crypto easy for everyday use.
            Key features:
            - Trade 300+ cryptocurrencies with 900+ trading pairs with no commissions
            - Book travel, accommodation, and experiences using crypto
            - Pay bills and services with cryptocurrency
            - Digital wallet for crypto holdings
            - NFT management
            - Bridge between crypto world and everyday life
            
            {prompt_template}
            """
    
            # Use the Hugging Face Inference API to generate content
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"} if self.hf_api_key else {}
            
            payload = {
                "inputs": context,
                "parameters": {
                    "max_new_tokens": 300,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                # Extract the generated text
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Remove the prompt from the generated text
                    if generated_text.startswith(context):
                        generated_text = generated_text[len(context):].strip()
                    
                    # Clean up the text - trim to 280 chars and remove quotes if present
                    tweet_text = generated_text.strip('"\'').strip()
                    
                    # Add a hashtag if there's space and the tweet doesn't already have one
                    if len(tweet_text) < 260 and '#' not in tweet_text:
                        hashtags = random.sample(self.hashtags, 1)
                        tweet_text = f"{tweet_text} {hashtags[0]}"
                    
                    if len(tweet_text) > 280:
                        tweet_text = tweet_text[:277] + "..."
                    
                    return tweet_text
                else:
                    logger.error(f"Unexpected response format from Hugging Face API: {result}")
            else:
                logger.error(f"Error from Hugging Face API: {response.status_code} - {response.text}")
                
            return None
            
        except Exception as e:
            logger.error(f"Error generating tweet with Hugging Face AI: {str(e)}")
            return None
            
    def generate_tweet_with_textgen(self):
        """
        Generate tweet content using TextGen free API
        
        Returns:
            str: Generated tweet text, or None if generation failed
        """
        try:
            # Select a random prompt template
            prompt_template = random.choice(self.prompt_templates)
            
            # Create context for the AI
            context = f"""
            CryptoXpress is a platform that makes crypto easy for everyday use.
            Key features:
            - Trade 300+ cryptocurrencies with 900+ trading pairs with no commissions
            - Book travel, accommodation, and experiences using crypto
            - Pay bills and services with cryptocurrency
            - Digital wallet for crypto holdings
            - NFT management
            - Bridge between crypto world and everyday life
            
            {prompt_template}
            """
            
            # Use the TextGen.dev API which offers free inference
            response = requests.post("https://api.textgen.dev/api/v1/generate", 
                                    json={
                                        "model": "Meta/Llama-3-8B-Instruct",
                                        "prompt": context,
                                        "max_tokens": 300,
                                        "temperature": 0.7
                                    })
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('generated_text', '')
                
                # Clean up the text - trim to 280 chars and remove quotes if present
                tweet_text = generated_text.strip('"\'').strip()
                
                # Add a hashtag if there's space and the tweet doesn't already have one
                if len(tweet_text) < 260 and '#' not in tweet_text:
                    hashtags = random.sample(self.hashtags, 1)
                    tweet_text = f"{tweet_text} {hashtags[0]}"
                
                if len(tweet_text) > 280:
                    tweet_text = tweet_text[:277] + "..."
                
                return tweet_text
            else:
                logger.error(f"Error from TextGen API: {response.status_code} - {response.text}")
                
            return None
            
        except Exception as e:
            logger.error(f"Error generating tweet with TextGen: {str(e)}")
            return None
            
    def get_ai_generated_content(self):

        # Try different generation methods in order of preference
        methods = [
            self.generate_tweet_with_huggingface,
            self.generate_tweet_with_textgen
        ]
        
        # Try each method until we get a valid tweet
        for method in methods:
            try:
                tweet_text = method()
                if tweet_text and len(tweet_text) > 0:
                    # Check if it's a duplicate
                    if tweet_text in self.posted_tweets:
                        logger.info("Generated duplicate tweet, retrying...")
                        continue
                    return tweet_text
            except Exception as e:
                logger.error(f"Error with AI generation method {method.__name__}: {str(e)}")
                continue
        
        # If all methods fail, use a backup tweet
        available_tweets = [tweet for tweet in self.backup_tweets if tweet not in self.posted_tweets]
        if not available_tweets:
            # If all backup tweets have been used, reset
            available_tweets = self.backup_tweets
            
        return random.choice(available_tweets)

    def post_tweet(self):
        try:
            tweet_text = self.get_ai_generated_content()
            
            if not tweet_text:
                logger.error("Failed to get content for tweet")
                return False
                
            # Post the tweet
            response = self.twitter_client.create_tweet(text=tweet_text)
            
            # Save the tweet to avoid duplicates
            self.posted_tweets.add(tweet_text)
            self.save_posted_tweet(tweet_text)
            
            logger.info(f"Posted tweet: {tweet_text}")
            return True
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return False
    
    def run(self, interval_minutes=60, randomize_interval=True, max_runtime_hours=None):
       # Run the bot continuously, posting tweets at regular intervals
       
        logger.info(f"CryptoXpress Bot started. Using AI-generated content. Posting interval: {interval_minutes} minutes.")
        if max_runtime_hours:
            logger.info(f"Bot will run for maximum {max_runtime_hours} hours")
            end_time = time.time() + (max_runtime_hours * 3600)
        else:
            end_time = None
        
        while True:
            # Check if runtime limit has been reached
            if end_time and time.time() > end_time:
                logger.info(f"Maximum runtime of {max_runtime_hours} hours reached. Stopping the bot.")
                break
                
            try:
                # Post a tweet
                success = self.post_tweet()
                
                if success:
                    # Calculate next interval (add randomness if enabled)
                    if randomize_interval:
                        # Add or subtract up to 20% of the base interval
                        variation = interval_minutes * 0.2
                        next_interval = interval_minutes + random.uniform(-variation, variation)
                    else:
                        next_interval = interval_minutes
                    
                    # Calculate and log next post time
                    next_post_datetime = datetime.now().timestamp() + (next_interval * 60)
                    next_post_time = datetime.fromtimestamp(next_post_datetime).strftime('%H:%M:%S')
                    logger.info(f"Next tweet scheduled in {next_interval:.1f} minutes (around {next_post_time})")
                    
                    # Sleep until next interval
                    time.sleep(next_interval * 60)
                else:
                    # If posting failed, wait a shorter time before retry
                    logger.warning("Tweet posting failed. Retrying in 10 minutes...")
                    time.sleep(600)  # 10 minutes
                    
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                logger.info("Waiting 15 minutes before continuing...")
                time.sleep(900)  # 15 minutes


def run_twitter_bot(consumer_key, consumer_secret, access_token, access_token_secret,
                   hf_api_key=None, interval_minutes=1, randomize_interval=True, max_runtime_hours=12):
    # Twitter API credentials
    twitter_creds = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    }
    
    # Create and run the bot
    bot = CryptoXpressBot(twitter_creds, hf_api_key=hf_api_key)
    
    # Run the bot with the specified settings
    bot.run(interval_minutes=interval_minutes, 
            randomize_interval=randomize_interval,
            max_runtime_hours=max_runtime_hours)


# Main execution block
if __name__ == "__main__":
    # Get Twitter API credentials
    # For Google Colab
    try:
        from google.colab import userdata
        consumer_key = userdata.get('TWITTER_CONSUMER_KEY')
        consumer_secret = userdata.get('TWITTER_CONSUMER_SECRET')
        access_token = userdata.get('TWITTER_ACCESS_TOKEN')
        access_token_secret = userdata.get('TWITTER_ACCESS_TOKEN_SECRET')
        # Optional Hugging Face API key (can be None for limited free access)
        hf_api_key = userdata.get('HF_API_KEY')
    except ImportError:
        # If not using Colab, use environment variables
        import os
        consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
        consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        hf_api_key = os.getenv('HF_API_KEY', None)

    # Check if credentials are available
    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print("Error: Twitter API credentials not found. Please set them as environment variables.")
        print("Required: TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
        exit(1)

    # Run the bot with default settings
    run_twitter_bot(
        consumer_key=consumer_key, 
        consumer_secret=consumer_secret,
        access_token=access_token, 
        access_token_secret=access_token_secret,
        hf_api_key=hf_api_key,  
        interval_minutes=1,   # Post every 1 minute by default
        randomize_interval=True,  # Add some random variation to posting times
        max_runtime_hours=12    # Run for 12 hours by default
    )