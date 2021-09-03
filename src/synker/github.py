'''
Here lies all the API calls to the GitHub API
'''
from . import settings
import requests as R
import json

def GET(endpoint, return_dict=True):
    '''
        Makes a GET request to the GitHub API
        to the specified endpoint.
        Accepts:
            endpoint: API Endpoint
            return_dict: if True, the data is returned as a python dict else the untouched response.
                            This is so the caller has all say in how to process the reponse
    '''
    r = R.get(settings.API_URL + endpoint, headers=settings.REQUEST_HEADERS)
    if r.ok:
        return r.json() if not return_json else r
    else:
        print(r.status_code, r.reason)
        return None if return_dict else r


def get_current_user_info():
    return GET("/user", False)


def collect_repos():
    r = GET("/users")
    return r.json()