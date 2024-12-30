# export/urls.py
from django.urls import path, include
from .views.export_declaration_list_view import ExportDeclarationList
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'export_declaration', ExportDeclarationList, basename='export_declaration')

urlpatterns = [
    path('', include(router.urls)),
]
