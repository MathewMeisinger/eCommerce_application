from django.conf import settings
import tweepy
from stores.models import Store
from products.models import Product


def tweet_new_product(product_id):
    """Post a short X/Twitter update announcing a newly created product."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        print(f"Product with id {product_id} does not exist.")
        return
    text = (
        # Build the post text and keep it within the X character limit.
        f"New product just landed!\n\n"
        f"{product.name}\n"
        f"{product.description[:140]}\n"
        f"Price: R{product.price:,.2f}\n"
    )[:280]
    try:
        # Create a Tweepy client using credentials loaded from settings.
        client = tweepy.Client(
            consumer_key=settings.X_CONSUMER_KEY,
            consumer_secret=settings.X_CONSUMER_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET,
        )
        response = client.create_tweet(text=text)
        print(f"Tweeted new product; POST ID: {response.data['id']}")
    except tweepy.TweepyException as e:
        print(f"Error tweeting new product: {e}")


def tweet_new_store(store_id):
    """Post a short X/Twitter update announcing a newly created store."""
    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        print(f"Store with id {store_id} does not exist.")
        return
    text = (
        # Build the post text and keep it within the X character limit.
        f"New store just opened!\n\n"
        f"{store.name}\n"
        f"{store.description[:140]}\n"
    )[:280]
    try:
        # Create a Tweepy client using credentials loaded from settings.
        client = tweepy.Client(
            consumer_key=settings.X_CONSUMER_KEY,
            consumer_secret=settings.X_CONSUMER_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET,
        )
        response = client.create_tweet(text=text)
        print(f"Tweeted new store; POST ID: {response.data['id']}")
    except tweepy.TweepyException as e:
        print(f"Error tweeting new store: {e}")
