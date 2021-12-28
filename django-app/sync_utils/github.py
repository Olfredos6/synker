'''
Here lies all the API calls to the GitHub API
'''
from django.conf import settings
import requests as R
import json


def process_endpoint(endpoint):
    # automatically remove the root API:
    if settings.API_URL in endpoint:
        endpoint = endpoint.replace(settings.API_URL, "")
    return endpoint


def GET(endpoint, return_dict=True, params={} ):
    '''
        Makes a GET request to the GitHub API
        to the specified endpoint. 
        Accepts:
            endpoint: API Endpoint
            return_dict: if True, the data is returned as a python dict else the untouched response.
                            This is so the caller has all say in how to process the reponse
            params: URL parameters
    '''
    endpoint = process_endpoint(endpoint)
    
    r = R.get(settings.API_URL + endpoint, headers=settings.REQUEST_HEADERS, params=params)
    if r.ok:
        return r.json() if return_dict else r
    else:
        print("!! ERROR?", r.status_code, r.reason)
        return None if return_dict else r


def get_current_user_info():
    return GET("/user", False)


def collect_repos(type=settings.GITHUB_REPO_TYPE, page=1):
    '''
        Accepts:
            type: type of repo
            page: result page number
    '''
    print(f"Collecting repos of type {type}")
    return GET("/user/repos", True, {"type": type, "per_page": 100, "page": page})