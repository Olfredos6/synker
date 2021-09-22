from django.shortcuts import render
from django.http import JsonResponse
from core.models import Repo


def index(request):
    return render(request, 'index.html', {})

def search_repo(request):
    keyword = request.GET.get('keyword')
    data = []
    for repo in Repo.objects.filter(full_name__icontains=keyword):
        data.append({
            "id": repo.node_id,
            "name": repo.full_name,
            "last_updated": repo.updated_at,
            "url": repo.url,
            "owner": repo.owner_login
        })
    return JsonResponse(data, safe=False)