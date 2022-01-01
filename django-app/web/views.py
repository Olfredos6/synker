from json.encoder import JSONEncoder
from django.db.models.fields import DateField
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from core.models import Repo, Student, Token, Know, KnowTag
from django.db.models import Q
from .utils import repoSerialize, compute_stats, get_json_parsable_repo_data
import json
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt


def req_body_to_json(request):
    return json.loads(request.body.decode("utf-8"))

def is_authed(token):
    ''' Used to auth requests passing it a token slug from in their
        path. If the token is invalid or expired, drop the request by
        returning a 403
    '''
    token_qs = Token.objects.filter(value=token)
    if token_qs.exists():
        if not token_qs[0].has_expired:
            return True

    return False


def index(request):    
    ''' Init page, collects token and redirects to index or prompts for authentication '''
    return render(request, 'landing.html', {})


def landing(request, token):
    token_qs = Token.objects.filter(value=token)
    if token_qs.exists():
        if not token_qs[0].has_expired:
            return render(request, 'index.html', {})
    return redirect('index')


def auth(request):
    # print(request.body.decode("utf-8"))
    email = json.loads(request.body.decode("utf-8")).get("email", None)
    if Token.is_valid_email(email):
        # create new token
        token, created = Token.issue(email=email)
        return JsonResponse({"message": "OTP required" }, safe=False)
    return JsonResponse({"message": "Invalid email"}, safe=False)


def confirm_otp(request):
    otp = json.loads(request.body.decode("utf-8")).get("otp", None)
    token_qs = Token.objects.filter(otp=otp)
    if token_qs.exists():
        return JsonResponse({"token": token_qs[0].value}, safe=False)
    return JsonResponse({"error": "Invalid OTP"}, safe=False)


def search_repo(request):
    keyword = request.GET.get('keyword')
    data = []
    for repo in Repo.objects.filter( Q(full_name__icontains=keyword) | Q(student__name__icontains=keyword) | Q(student__surname__icontains=keyword)| Q(student__customer_no__contains=keyword)| Q(student__email__contains=keyword) ):
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
        # print("REUET____>", json.loads(request.body))
        data = json.loads(request.body)
        student = None
        # if a student with the given details does not exists, create and assign to repo
        student_match = Student.objects.filter(customer_no=data.get("customer_no"))
        if not student_match.exists():
            student = Student.objects.create(**{i:data.get(i) for i in data if i != 'csrfmiddlewaretoken' })# updates repo's student info
            repo.set_student(student)
        else:
            student = student_match[0]
            data = {i:data.get(i) for i in data if i not in ['csrfmiddlewaretoken', 'customer_no'] }
            print("Existing student --->", student, repo.student, "\nUpdating using", data)
            Student.objects.filter(customer_no=repo.student.customer_no).update(**data)
        
    return JsonResponse(get_json_parsable_repo_data(node_id), safe=False)


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


@csrf_exempt
def list_knwoledges(request, token):
    if is_authed(token):
        if request.method == "POST":
            token = Token.get(token)
            print(token, req_body_to_json(request))
            payload = req_body_to_json(request)

            # to edit a know, insert its primary key value in the payload
            if payload.get('id', None):
                print(Know.objects.filter(id=payload.get("id")).update(                    
                    last_edited_by=token.email,
                    title=payload.get('title'),
                    tags=payload.get('tags'),
                    text=payload.get('text'),
                    ))
                new_know = Know.objects.get(id=payload.get('id'))
            else:
                new_know = Know.objects.create(
                    last_edited_by=token.email,
                    title=payload.get('title'),
                    tags=payload.get('tags'),
                    text=payload.get('text'),
                )
            # submit new knowledge
            # can update ags, title, content, click count
            return JsonResponse(json.loads(serialize('json', [new_know])), safe=False)
        
        # if a GET request, we either display top clicked on or perform
        # a search based on the received query parameter
        k_list = []
        search_term =  request.GET.get("search")
        if search_term:
            k_list = Know.objects.filter(
                Q( title__icontains = search_term) | 
                Q( tags__icontains = search_term) |
                Q( text__icontains = search_term )
            )
        else:
            k_list = Know.objects.all().order_by('click_count')[:25]
        
        return JsonResponse(json.loads(serialize('json', k_list)), safe=False)
    return HttpResponseForbidden()
