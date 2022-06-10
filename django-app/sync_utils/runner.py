from django.conf import settings
from datetime import datetime, timedelta

from . import github
from core.models import Repo


def fetch_all(type=settings.GITHUB_REPO_TYPE):
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
        'cloned': 0,
        'old_skipped': 0
    }

    while collect_next_page:
        repos = github.collect_repos(type, page=next_page)
        # print(f"----> Collected {len(repos)} repos from page {next_page} of results")

        if len(repos) < settings.GITHUB_PER_PAGE:
            collect_next_page = False
        else:
            next_page += 1

        stats['collected'] += len(repos)
        
        for r in repos:

            # This will perhaps be removed later? But then, some repos may already
            # oust ITCS as collaborator. But for my own sake, disk sake, we are going to
            # limit repos to work with on to those that were created less than 12 months ago
            # and update none lest than 3 months ago
            date_created_on_github = datetime.strptime(r.get('created_at'),'%Y-%m-%dT%H:%M:%SZ')
            last_updated = datetime.strptime(r.get('pushed_at'),'%Y-%m-%dT%H:%M:%SZ')
            print("FIX THE REPO DISK USAGE ISSUE!!!!") # -> A message meant to annoy to make me remember
            if date_created_on_github  > datetime.now() - timedelta(days=12*30) and \
            (last_updated + timedelta(days=3*30)) > datetime.now() :
            # check if repository exists, if not, create and sync
                repository = Repo.objects.filter(node_id=r.get('node_id'))
                if repository.exists():
                    repository = repository[0]

                else:
                    # Only proceed with creation if the repo has a branch.
                    # This is the case when updated_at != created_at
                    # @TODO: check if has any branch if created_at and pdated_at are equal *********
                    # if r.get('updated_at') == r.get('created_at'):
                    #     continue # skip this repo
                        
                    repository = Repo.create_from_payload(type, **r)
                    # print("Created repository", repository)


                feedback = repository.sync(
                    datetime.strptime(
                        r.get('pushed_at'),
                        "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        r.get('size'))
                if feedback == 1:
                    stats['updated'] += 1
                elif feedback == 2:
                    stats['cloned'] += 1
            else:
                stats['old_skipped'] += 1
        
    print(datetime.now(), stats)

import threading
def run():
    '''
        Main function.
        Runs sync function every 5 minutes
    '''
    fetch_all()
    timer = threading.Timer(300, run)
    timer.start()