# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from comm_app import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name='home'),
    url(r'^comments/$', views.show_comments, name='show_comments'),
    url(r'^comments/add/$', views.add_comment, name='add_comment'),
    url(r'^comments/entity/(?P<entity_id>[0-9]{1,10})$', views.ShowCommentsEntityView.as_view(), name='show_comments_entity'),
    url(r'^comments/user/(?P<user_id>[0-9]{1,10})$', views.ShowCommentsUserView.as_view(), name='show_comments_user'),
    url(r'^comments/descendants/(?P<parent_id>[0-9]{1,10})$', views.ShowCommentsDescendantsView.as_view(), name='show_comments_descendants'),
    url(r'^comments/children/(?P<parent_id>[0-9]{1,10})$', views.ShowCommentsChildrenView.as_view(), name='show_comments_children'),
    url(r'^xml/(?P<dockey>[a-zA-Z0-9-]{36})$', views.model_doc_xml, name='model_doc_xml'),
    url(r'^csv/(?P<dockey>[a-zA-Z0-9-]{36})$', views.model_doc_csv, name='model_doc_csv'),
]
