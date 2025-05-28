"""Client for DevHub API."""

import os

from requests_oauthlib import OAuth1Session


def get_client():
    """Get DevHub API client and base_url."""
    client = OAuth1Session(
        os.environ['DEVHUB_API_KEY'],
        client_secret=os.environ['DEVHUB_API_SECRET'])
    base_url = '{}/api/v2/'.format(os.environ['DEVHUB_BASE_URL'])
    return client, base_url
