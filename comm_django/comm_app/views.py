# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponseForbidden
from django.http import JsonResponse

import os
import json

from comm_app.tasks import export_file, notify_file_ready
from comm_app.models import Comment

from comm_app.utils import check_int_positive


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(HomePageView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        param = ((request.POST.get('session'), request.POST.get('message')),)
        export_file.apply_async(param, link=notify_file_ready.s())
        return HttpResponse('OK')

# show all comments
# for debug purposes only
def show_comments(request):
    return render(request, "comments.html", {'comments': Comment.objects.all()})


@csrf_exempt
def model_doc_xml(request, dockey):
    try:
        path = os.path.join('/tmp', dockey+'.xml')
        if os.path.exists(path):
            data = open(path, "rb").read()
            return HttpResponse(data, content_type="text/xml")
    except:
        pass
    raise Http404


@csrf_exempt
def model_doc_csv(request, dockey):
    try:
        path = os.path.join('/tmp', dockey+'.csv')
        if os.path.exists(path):
            data = open(path, "rb").read()
            return HttpResponse(data, content_type="text/csv")
    except:
        pass
    raise Http404


@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        # check user key
        # key = request.POST.get('key')
        # if not valid(key): return HttpResponseForbidden
        json_data = json.loads(request.body)
        try:
            user_id = check_int_positive(json_data['user_id'])
            entity_id = check_int_positive(json_data['entity_id'])
            entity_type_id = check_int_positive(json_data['entity_type_id'])
            text = json_data['text']
        except KeyError:
            return JsonResponse({'error':-1}) # invalid params
        
        if user_id > 0 and entity_id > 0 and entity_type_id > 0:
            try:
                if entity_type_id == 1: # entity type is comment
                    # check if comment exists
                    try:
                        parent_comm = Comment.objects.get(id=entity_id)
                    except ObjectDoesNotExist:
                        return JsonResponse({'error':-3}) # invalid comment id
                    # set entity_id same as parent_comm.entity_id
                    comm = Comment.objects.create(user_id=user_id, entity_id=parent_comm.entity_id, text=text, parent=parent_comm)
                else:
                    comm = Comment.objects.create(user_id=user_id, entity_id=entity_id, text=text, parent=None)
                return JsonResponse({'error':0, 'id':comm.id}) # comment created
            except:
                return JsonResponse({'error':-2}) # database error
        else:
            return JsonResponse({'error':-1}) # invalid params
    else:
        raise Http404


class ShowCommentsEntityView(TemplateView):
    def get(self, request, entity_id, **kwargs):
        return render(request, "comments.html", {'comments': Comment.objects.filter(entity_id=entity_id)})

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ShowCommentsEntityView, self).dispatch(*args, **kwargs)

    def post(self, request, entity_id, *args, **kwargs):
        try:
            comments = []
            comms = Comment.objects.filter(entity_id=entity_id)
            if comms is not None:
                for i, c in enumerate(comms):
                    comments.append({"order":i+1, "level":c.level, "text":c.text, "user_id":c.user_id, "id":c.id, "parent_id":c.parent_id, "date":c.date})
            comments = json.dumps(comments, indent=4, default=str)
            return JsonResponse({'error':0, 'comments':comments})
        except:
            return JsonResponse({'error':-2}) # database error


class ShowCommentsUserView(TemplateView):
    def get(self, request, user_id, **kwargs):
        return render(request, "comments.html", {'comments': Comment.objects.filter(user_id=user_id).order_by('-date')})

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ShowCommentsUserView, self).dispatch(*args, **kwargs)

    def post(self, request, user_id, *args, **kwargs):
        try:
            comments = []
            comms = Comment.objects.filter(user_id=user_id).order_by('-date')
            if comms is not None:
                for i, c in enumerate(comms):
                    comments.append({"order":i+1, "text":c.text, "id":c.id, "date":c.date})
            comments = json.dumps(comments, indent=4, default=str)
            return JsonResponse({'error':0, 'comments':comments})
        except:
            return JsonResponse({'error':-2}) # database error


class ShowCommentsDescendantsView(TemplateView):
    def get(self, request, parent_id, **kwargs):
        comms = None
        try:
            comms = Comment.objects.get(id=parent_id).get_descendants(include_self=False)
        except ObjectDoesNotExist:
            pass
        return render(request, "comments.html", {'comments': comms})

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ShowCommentsDescendantsView, self).dispatch(*args, **kwargs)

    def post(self, request, parent_id, *args, **kwargs):
        try:
            comments = []
            try:
                comms = Comment.objects.get(id=parent_id).get_descendants(include_self=False)
            except ObjectDoesNotExist:
                return JsonResponse({'error':-3}) # invalid comment id
            if comms is not None:
                for i, c in enumerate(comms):
                    comments.append({"order":i+1, "level":c.level, "text":c.text, "user_id":c.user_id, "id":c.id, "parent_id":c.parent_id, "date":c.date})
            comments = json.dumps(comments, indent=4, default=str)
            return JsonResponse({'error':0, 'comments':comments})
        except:
            return JsonResponse({'error':-2}) # database error


def _get_comments(request, parent_id):
    comms = Comment.objects.get(id=parent_id).get_children()
    page = check_int_positive(request.GET.get('page'))
    page_size = check_int_positive(request.GET.get('size'))
    if page_size > 0 and page > 0:
        paginator = Paginator(comms, page_size)
        if page in paginator.page_range:
            comms = paginator.page(page).object_list
    return comms

class ShowCommentsChildrenView(TemplateView):
    def get(self, request, parent_id, **kwargs):
        comms = None
        try:
            comms = _get_comments(request, parent_id)
        except ObjectDoesNotExist:
            pass
        return render(request, "comments.html", {'comments': comms})

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ShowCommentsChildrenView, self).dispatch(*args, **kwargs)

    def post(self, request, parent_id, *args, **kwargs):
        try:
            comments = []
            try:
                comms = _get_comments(request, parent_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error':-3}) # invalid comment id
            if comms is not None:
                for i, c in enumerate(comms):
                    comments.append({"order":i+1, "level":c.level, "text":c.text, "user_id":c.user_id, "id":c.id, "parent_id":c.parent_id, "date":c.date})
            comments = json.dumps(comments, indent=4, default=str)
            return JsonResponse({'error':0, 'comments':comments})
        except:
            return JsonResponse({'error':-2}) # database error


