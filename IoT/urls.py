from django.urls import path
from django.conf.urls import url
from . import views

app_name = "IoT"

urlpatterns = [
    path("", views.CoisaListView.as_view(), name="list"),
    path("<slug:slug>/", views.CoisaDetailView.as_view(), name="detail"),
    #path("<slug:slug>/add/", views.CoisaDetailView_add.as_view(template_name="add_temporizador.html"), name="detail/add"),
    url(r'^(?P<slug>[a-zA-Z0-9]+)/add/$', views.add_temp, name="add_temp"),
    url(r'^(?P<slug>[a-zA-Z0-9]+)/remove/(?P<poss>[0-9])/$', views.remov_temp, name="remove_temp"),
    url(r'^(?P<slug>[a-zA-Z0-9]+)/atualizar_temporizador/(?P<pos>[0-9])/$', views.atualizar_temporizador, name="modifica_temporizador"),
    url(r'^(?P<slug>[a-zA-Z0-9]+)/timer/$', views.set_timer, name="timer"),
    url(r'^(?P<slug>[a-zA-Z1-9]+)/lampada/$', views.altera_lamp, name="altera_lamp"),
]