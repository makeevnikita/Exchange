from django.urls import path
from . import views
from django.conf.urls.static import static
from cryptosite import settings

urlpatterns = [
    path('news/', views.ArticleListView.as_view()),
    path('news/<slug:article_slug>/', views.ArticlePageView.as_view(), name='article'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if (settings.DEBUG):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)