import os

API_URL = "https://api.github.com"
API_KEY = "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" # Should be set via ENV when runnning Synker or interactively

REQUEST_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization" : f"token {API_KEY}"
}

DATA_DIR = os.path.join( "/".join(os.path.realpath(__file__).split("/")[:-1]), "data")
MASTER_DATA = os.path.join(DATA_DIR, "master_data.json")