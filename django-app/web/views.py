from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from core.models import Repo
from .utils import repoSerialize, compute_stats


def index(request):
    return render(request, 'index.html', {})

def search_repo(request):
    keyword = request.GET.get('keyword')
    data = []
    for repo in Repo.objects.filter(full_name__icontains=keyword):
        data.append(repoSerialize(repo))
    return JsonResponse(data, safe=False)


def repo(request, id):
    '''
    collects necessary data about a repository. That is:
     - repo object data
     - repo directory structure
    '''

    data = {"repo": None, "struct": None}
    repo = get_object_or_404(Repo, node_id=id)
    data["repo"] = repoSerialize(repo)
    data["struct"] = repo.dir_struct()

    return JsonResponse(data, safe=False)


def stats(request):
    response = render(request, "renderer-default.html", {"stats":compute_stats()})
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response


config_php = '''<?php
	$cd_host = "companydir-db";
	$cd_port = 3306;
	$cd_socket = "";
	$cd_user = "root";
	$cd_password = "root";
	$cd_dbname = "companydirectory";
?>'''
def pre_render(request, node_id):
    '''
        Runs utility functions before when a repo is
        clicked to render
    '''
    print("Running utility functions for", node_id)
    # Company Directory config.php substitution
    get_object_or_404(Repo, node_id=node_id).find_file_update("config.php", config_php)
    return HttpResponse()


def code_server(request, node_id):
    '''
        Process requests to start or get the container runninga code-server
        instance on the current repo.

        @TODO:
            This implementation is not perfect at all imo!!
            It needs more thinking...
    '''
    repo = get_object_or_404(Repo, node_id=node_id)
    port = repo.get_code_server()
    if port:
        return JsonResponse({"port": port}, safe=False)
    else:
        return HttpResponse(500)