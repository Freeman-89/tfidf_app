from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import UploadFileView

urlpatterns = [
    path('', UploadFileView.as_view(), name='upload_file'),
    path('login/', LoginView.as_view(template_name='tfidfapp/login.html', next_page='/'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
]