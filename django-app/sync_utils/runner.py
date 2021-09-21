import json
from time import sleep
from django.conf import settings
import os
from datetime import datetime

from . import github
from core.models import Repo


def fetch_all(type="member"):
    ''' Fetch all reposiory for the current user
        of the sepcified type.

        Uses a chec variable collect_next_page used to request the next result page
        from the /user/repo GitHub endpoint. We keep requesting for the next page
        as long as the result count is 100.

    '''
    collect_next_page = True
    next_page = 1
    stats = {
        'collected': 0,
        'updated': 0,
        'cloned': 0
    }

    while collect_next_page:
        repos = github.collect_repos(type, page=next_page)
        print(f"----> Collected {len(repos)} repos from page {next_page} of results")

        if len(repos) < settings.GITHUB_PER_PAGE:
            collect_next_page = False
        else:
            next_page += 1

        stats['collected'] += len(repos)
        
        for r in repos:
            # check if repository exists, if not, create and sync
            sync_repo = False
            repository = Repo.objects.filter(node_id=r.get('node_id'))
            if repository.exists():
                repository = repository[0]

            else:
                repository = Repo.create_from_payload(type, **r)
                # print("Created repository", repository)

            feedback = repository.sync(
                datetime.strptime(
                    r.get('updated_at'),
                    "%Y-%m-%dT%H:%M:%SZ"
                    ))
            if feedback == 1:
                stats['updated'] += 1
            elif feedback == 2:
                stats['cloned'] += 1
        
    print(stats)

def run():
    '''
        Main function.
        Runs sync function every 5 minutes
    '''
    while True: 
        print(f"-------> Running sync at {datetime.now()}")
        fetch_all()
        sleep(300)


# def check_data():
#     '''
#         Make sure all the required files are ready.
#         If not, create them(setup).
#     '''

#     DIR_DATA_EXISTED = True
#     if not os.path.exists(settings.DATA_DIR):
#         DIR_DATA_EXISTED = False
#         os.mkdir(settings.DATA_DIR)
    
#     print("DIR DATA EXIST?", DIR_DATA_EXISTED)
#     if not DIR_DATA_EXISTED:
#         setup()
        

# def setup():
#     git_reponse = github.get_current_user_info()
#     if git_reponse.ok:
#         with open(settings.MASTER_DATA, "x") as file:
#             file.write(git_reponse.text)
#     else:
#         raise f"{git_reponse.status_code}: {git_reponse.reason}"
    

#     # Repos list file
#     db.init()

# def sync(type="member"):
#     ''' 

#     '''
#     # check_data()
#     # print("syncing...")
#     # setup()
#     print("Getting repositories ffrom MASTER's repository")
#     repos = github.collect_repos(type)
#     for r in repos:
#         repo = repository.Repo(type=type, **r)
#         if not repo.is_tracked:
#             print(f"Syncing {repo.full_name}")
#     # print(settings.API_URL)