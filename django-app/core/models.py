from django.db import models

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


    def sync(self) -> None:
        print(f"Syncing {self.full_name}")


    def track(self) -> None:
        ''' saves repo data to the db,
            marking the repo is now tracked
        '''
        pass


