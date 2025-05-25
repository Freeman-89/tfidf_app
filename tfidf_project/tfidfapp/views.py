import os
import pickle
import uuid
from typing import Dict, Any
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import TfIdfCompute


class UploadFileView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request: HttpRequest) -> HttpResponse:
        context: Dict[str, Any] = {}

        tfidf_hex = request.session.get('tfidf_list')
        filename = request.session.get('filename')

        if tfidf_hex and filename:
            tfidf_list = pickle.loads(bytes.fromhex(tfidf_hex))
            paginator = Paginator(tfidf_list, 50)
            page_number = request.GET.get('page', 1)

            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            context['tfidf_page'] = page_obj
            context['filename'] = filename

        return render(request, 'tfidfapp/base.html', context)


    def post(self, request: HttpRequest) -> HttpResponse:
        request.session.pop('tfidf_list', None)
        request.session.pop('filename', None)
        uploaded_file = request.FILES.get('file')
        context: Dict[str, Any] = {}
        media_root: str = settings.MEDIA_ROOT
        if uploaded_file:
            ''' Проверяем есть ли файлы в директории и очищаем её'''
            if os.listdir(media_root):
                for file in os.listdir(media_root):
                    os.unlink(os.path.join(media_root, file))

            ''' Производим запись файла на диск, для отладки '''
            file_path: str = os.path.join(media_root, uploaded_file.name)
            with open(file_path, 'wb+') as new_file:
                for chunk in uploaded_file.chunks(chunk_size=8192):
                    new_file.write(chunk)

            file_name = uploaded_file.name
            context['filename'] = file_name
            uuid_document_name = f'{uuid.uuid4()}_{file_name}'
            tfidf = TfIdfCompute(file=uploaded_file, document_name=uuid_document_name)
            context['tf'], context['idf']  = tfidf.compute_tfidf()

            tfidf_list = sorted(
                [(word, context['tf'][word], context['idf'][word]) for word in context['tf'].keys()],
                key=lambda item: item[2],
                reverse=True
            )
            paginator = Paginator(tfidf_list, 50)
            page_number = request.GET.get('page', 1)

            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            context['tfidf_page'] = page_obj

            request.session['tfidf_list'] = pickle.dumps(tfidf_list).hex()
            request.session['filename'] = file_name

        return redirect(f"{request.path}?page=1")
        # return render(request, 'tfidfapp/base.html', context)