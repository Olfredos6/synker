import json
from time import sleep
from django.conf import settings
import os

from . import github
from core.models import Repo


def fetch_all(type="member"):
    ''' Fetch all reposiory for the current user
        of the sepcified type.
    '''
    repos = github.collect_repos(type)
    for r in repos:
        # check if repository exists, if not, create and sync
        repository = Repo.objects.filter(node_id=r.get('node_id'))
        if repository.exists():
            repository = repository[0]
        else:
            repository = Repo.create_from_payload(type, **r)
            print("Created repository", repository)
        repository.sync()


def run():
    '''
        Main function.
        Runs sync function every 5 minutes
    '''
    while True: 
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