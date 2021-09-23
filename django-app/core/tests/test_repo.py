from django.test import TestCase
import os
from core.models import Repo
import json
from random import randrange


class RepoTest(TestCase):
    def tearDown(self) -> None:
        # delete
        return super().tearDown()

    def setUp(self) -> None:
        # print("~~~>", os.path.join(*__file__.split("/")[:-1], "repo_fixtures.json"))
        with open( "/" + os.path.join(*__file__.split("/")[:-1], "repo_fixtures.json")  , 'r') as file:
            self.repos_fixtures = json.loads(file.read())
        
        # randomly pick 2 repos and save them to the db:
        x = randrange(len(self.repos_fixtures))
        self.saved_repos_index = [x, x-1] # -1 so that we never get out of range
        self.first_repo =  Repo.create_from_payload("member", **self.repos_fixtures[self.saved_repos_index[0]])
        self.second_repo = Repo.create_from_payload("member", **self.repos_fixtures[self.saved_repos_index[1]])

        return super().setUp()

    # def test_can_update_repo(self):
    #     assert False

    # def test_can_create_from_github_payload(self): ---> see setup
    #     assert False