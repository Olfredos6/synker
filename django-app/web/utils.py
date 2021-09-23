'''
Supporting utility functions for web views
'''
from core.models import Repo

def repoSerialize(repo: Repo):
    return {
        "id": repo.node_id,
        "name": repo.full_name,
        "last_updated": repo.updated_at,
        "url": repo.url,
        "owner": repo.owner_login
    }
    