'''
Supporting utility functions for web views
'''
from core.models import Repo, Student
from django.shortcuts import get_object_or_404
import functools

def repoSerialize(repo: Repo):
    return {
        "id": repo.node_id,
        "name": repo.name,
        "full_name": repo.full_name,
        "last_updated": repo.updated_at,
        "url": repo.url,
        "owner": repo.owner_login,
        "size": repo.size,
        "folder": repo.folder_name,
        'current_branch': repo.branch,
        'branches': repo.branches,
        "student": serializeStudent(repo.student)
    }


def serializeStudent(student: Student) -> dict:
    if student:
        return {
            "customer_no": student.customer_no,
            "surname": student.surname,
            "name": student.name,
            "email": student.email
        }
    else:
        return {"detail": "Student was never set."}


def get_json_parsable_repo_data(id):
    data = {"repo": None, "struct": None}
    repo = get_object_or_404(Repo, node_id=id)
    data["repo"] = repoSerialize(repo)
    data["struct"] = repo.dir_struct()    
    return data


def compute_stats():
    repos = Repo.objects.all()
    return {
        "repo_count": repos.count(),
        "total_size": functools.reduce(lambda a,b: a+b, [r.size for r in repos])
    }

