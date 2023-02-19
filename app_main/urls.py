from django.urls import path
from app_main.views import GetAutomationDataApiView

app_name = 'app_auth'

urlpatterns = [
    path('', GetAutomationDataApiView.as_view()),
]
