from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from core.models import Repo
from .utils import repoSerialize, compute_stats, get_json_parsable_repo_data


def index(request):
    return render(request, 'index.html', {})


def search_repo(request):
    keyword = request.GET.get('keyword')
    data = []
    for repo in Repo.objects.filter(full_name__icontains=keyword):
        data.append(repoSerialize(repo))
    return JsonResponse(data, safe=False)


def repo(request, id):
    return JsonResponse(get_json_parsable_repo_data(id), safe=False)


def student_info(request, node_id):
    '''
        Edit a repo's related student's info
    '''
    repo = get_object_or_404(Repo, node_id=node_id)
    if request.method == "POST":
        print("REQUEST DATA", **request.POST)
        student = Student.objects.update_or_create(
            repo=repo,
            **request.POST
            )
        return JsonReponse(repoSerialize(get_object_or_404(Repo, node_id=node_id)))
    else:
        return JsonRsponse(data=serializeStudent(repo.student), safe=False)


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
    print("Provision request for", repo.short, repo.full_name)
    port = repo.get_code_server()
    if port:
        return JsonResponse({"port": port}, safe=False)
    else:
        return HttpResponse(status_code=500)


def kill_code_server(request, node_id):
    repo = get_object_or_404(Repo, node_id=node_id)
    repo.kill_code_server()
    return HttpResponse(200)


def repo_was_edited(request, id):
    repo = get_object_or_404(Repo, node_id=id)
    return JsonResponse({"was_edited": 1 if repo.was_edited else 0 }, safe=False)


def repo_checkout_branch(request, id):
    '''
        git checkout branch on repo
    '''
    print("Checkig out", request.GET.get("b"))
    repo = get_object_or_404(Repo, node_id=id)
    repo.checkout(request.GET.get("b"))
    return JsonResponse(get_json_parsable_repo_data(id), safe=False)
