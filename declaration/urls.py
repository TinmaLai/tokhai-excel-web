# export/urls.py
from django.urls import path
from .views import ExportDeclarationList

urlpatterns = [
    path('export_declarations/', ExportDeclarationList.as_view(), name='export_declaration_list'),
    path('export_declarations/<str:id>/', ExportDeclarationList.as_view(), name='export_declaration_detail'),
]
