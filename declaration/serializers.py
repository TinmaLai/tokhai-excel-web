# export/serializers.py
from rest_framework import serializers
from .models import ExportDeclaration

class ExportDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportDeclaration
        fields = '__all__'
