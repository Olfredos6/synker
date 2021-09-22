from django.db import models
from pathlib import Path
from django.conf import settings
import subprocess
from datetime import datetime
from os import environ
from pytz import utc as UTC

# from . import utils
# from . import settings
# from . import db


class Repo(models.Model):
   
    node_id = models.CharField(max_length=32, null=False, primary_key=True)
    type = models.CharField(max_length=10, null=False)
    full_name = models.CharField(max_length=100)
    updated_at = models.DateTimeField(null=True)
    url = models.URLField(max_length=10, null=False)
    clone_url = models.URLField(max_length=10, null=False)
    size = models.IntegerField()
    owner_login = models.CharField(max_length=100, null=False)


    @staticmethod
    def create_from_payload(type, **kwargs):
        '''
            Simplifies creating Repo objects using GitHub's repository payload
        '''
        new_repo = Repo()
        new_repo.type = type
        new_repo.node_id = kwargs.get('node_id')
        new_repo.full_name = kwargs.get('full_name')
        new_repo.updated_at = kwargs.get('updated_at')
        new_repo.clone_url = kwargs.get('clone_url')
        new_repo.size = kwargs.get('size')
        new_repo.owner_login = kwargs.get('owner').get('login')
        new_repo.save()
        return new_repo
    
    @staticmethod
    def check_update():
        ''' 
            For each known repos URL, check if the repo
            updated_at timstamp has changed. If so, sync the repo.
        '''
        pass


    @property
    def path(self):
        ''' returns the repo directory path '''
        return settings.SYNKER_REPO_DIR.joinpath(self.node_id)

    
    def update_db(self, **payload):
        '''
            Updates the repo's data on on the databse. 
            For now, the most important piece of information
            requiring an update is the updated_at timestamp. 
            This info is updated everytime the repo is pulled.
        '''
        return Repo.objects.filter(node_id=self.node_id).update(
            updated_at=payload.get('updated_at')
        )


    def sync(self, timestamp:datetime = None)-> None:
        '''
        Syncs a repository. 
        Starts by checking if the repos folder contains a repo that matches this repo's GitHub node_id
            creates it if necessay.
        If the repo is created
            use git clone. 
            Otherwwise, check if the updated_at are different.
                If different, git pull
        
        Accepts:
            timestamp: a datetime.
                    Using this argument forces aplying git clone on the repo.

                    Defaults to self.updated_at
        
        Returns: 0 if not updated
                 1 if updated
                 2 if cloned   
        '''
        feedback = 0
        if not timestamp:
            timestamp = self.updated_at
        
        # print(f"Syncing {self.full_name} using timestamp {timestamp}")
        created_repo = False
        if not self.path.exists():
            self.path.mkdir()
            created_repo = True
        else:
            # print("repo folder exists, updating...")
            pass
        
        if created_repo:
            # git clone
            # print(f"Cloning {self.full_name} into {self.path}")
            self.clone()
            self.update_db(updated_at=timestamp)
            feedback = 2

        else:
            # print(f"will only update if {self.updated_at} is greater than {timestamp.replace(tzinfo=UTC)}")
            if self.updated_at < timestamp.replace(tzinfo=UTC):
                # print(f"Updating/pulling {self.full_name}")
                self.pull()
                self.update_db(updated_at=timestamp)
                feedback = 1
        
        return feedback


    def clone(self):
        ''' clone the repo using git's clone command '''
        # insert GitHub's auth_token inot repo's clone URL
        authed_url = self.clone_url.replace("github.com", f"{environ.get('GITHUB_TOKEN')}@github.com")
        # print("New URL", authed_url)
        cloning_proc = subprocess.run(['git', 'clone', authed_url, self.path ], capture_output=True)
        print(cloning_proc, cloning_proc.stdout)


    def pull(self):
        ''' git pull on the repo '''
        pull_proc = subprocess.run(['git', 'pull'], capture_output=True, cwd=self.path)
        # print(pull_proc, pull_proc.stdout)


    def track(self) -> None:
        ''' saves repo data to the db,
            marking the repo is now tracked
        '''
        pass

    def dir_struct(self) -> dict:
        ''' returns a dictionary object representing the 
            the folder structure of the repo. We only go 3 level down.
        '''
        from os import scandir

        def traverse(path, parent):
            ''' traverse dir at path to form a structure inside
                parent and return the updated parent
            '''
            print(f"Traversing {path}")
            for entry in scandir(path):
                parent["-"] = [] # will list files 
                if entry.is_dir():
                    parent[entry.name] = {"-": []}
                    traverse(entry, parent[entry.name])
                else:
                    parent.get("-").append(entry.name)
            
            return parent
        
        return traverse(self.path,{"-": []})
