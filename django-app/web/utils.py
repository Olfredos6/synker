'''
Supporting utility functions for web views
'''
from core.models import Repo
import functools

def repoSerialize(repo: Repo):
    return {
        "id": repo.node_id,
        "name": repo.name,
        "full_name": repo.full_name,
        "last_updated": repo.updated_at,
        "url": repo.url,
        "owner": repo.owner_login,
        "size": repo.size,
        "folder": repo.folder_name 
    }


def compute_stats():
    repos = Repo.objects.all()
    return {
        "repo_count": repos.count(),
        "total_size": functools.reduce(lambda a,b: a+b, [r.size for r in repos])
    }

