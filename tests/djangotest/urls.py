from django.conf.urls import url
from djangotest import views

urlpatterns = [
    url(r'add', views.add),
    url(r'hello', views.hello),
    url(r'foo', views.foo),
    url(r'just-a-view', views.just_a_view),
]
