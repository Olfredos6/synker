from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from core.models import Repo
from .utils import repoSerialize


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