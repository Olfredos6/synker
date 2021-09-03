from time import sleep
from . import settings
from . import github
import os


def run():
    '''
        Main function.
        Runs sync function every 5 minutes
    '''
    check_data()
    # while True:
    #     sync()
    #     sleep(60)


def check_data():
    '''
        Make sure all the required files are ready.
        If not, create them.
    '''

    DIR_DATA_EXISTED = True
    if not os.path.exists(settings.DATA_DIR):
        DIR_DATA_EXISTED = False
        os.mkdir(settings.DATA_DIR)
    
    if not DIR_DATA_EXISTED:
        # create the current user's data file
        user_data = github.get_current_user_info()
        print(user_data, dir(user_data))



def sync_user_data():
    github.get_current_user_info()


def sync():
    '''

    '''
    # check_data()
    # print("syncing...")
    # sync_user_data()
    # repos = github.collect_repos()
    # for r in repos:
    #     print(r)
    # print(settings.API_URL)