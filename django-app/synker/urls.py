"""synker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web import views


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index, name="home"  ),
    path('search/', views.search_repo, name="search-repo"),
    path('repo/<str:id>', views.repo, name="view-repo"),
    path('repo/<str:id>/was_edited', views.repo_was_edited, name="repo-was-edited"),
    path('stats/', views.stats, name="stats"),
    path('pre-render/<str:node_id>', views.pre_render, name="pre-render"),
    path('code-server/<str:node_id>', views.code_server, name="code-server"),
    path('kill-code-server/<str:node_id>', views.kill_code_server, name="kill-code-server")
]
