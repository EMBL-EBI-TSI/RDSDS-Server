from authlib.integrations.starlette_client import OAuth
from app.core.config import ELIXIR_CLIENT_ID, ELIXIR_CLIENT_SECRET, ELIXIR_METADATA_URL
from starlette.config import Config

class OAuthClient:
    client: OAuth = None

oauth = OAuthClient()

def load_oauth_client():
    oauth.client =  OAuth(Config('.env'))
    oauth.client.register(
        name='elixir',
        server_metadata_url=ELIXIR_METADATA_URL,
        client_kwargs={
            'scope': 'openid email profile bona_fide_status'
        },
        client_id=ELIXIR_CLIENT_ID,
        client_secret=ELIXIR_CLIENT_SECRET
    )
    
    
