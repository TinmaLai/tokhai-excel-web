from django.shortcuts import render

# Create your views here.
# export/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ExportDeclaration
from .serializers import ExportDeclarationSerializer
from django.db import connection
import json
from django.shortcuts import get_object_or_404
import re

class ExportDeclarationList(APIView):
    def parseWhere(self, where_clause):
        # Loại bỏ các khoảng trắng thừa ở đầu và cuối
        where_clause = where_clause.strip()
        
        # Kiểm tra nếu mệnh đề WHERE không rỗng và không chứa các toán tử AND/OR không hợp lệ
        if not where_clause:
            return ''
        
        # Split mệnh đề WHERE bằng các từ khóa AND và OR, phải có ít nhất một biểu thức hợp lệ
        expressions = re.split(r'(?i)\s*(AND|OR)\s*', where_clause)

        # Kiểm tra từng biểu thức nếu nó có đúng định dạng field = %s
        pattern = r'^[a-zA-Z0-9_]+\s*=\s*%s$'
        
        for expr in expressions:
            expr = expr.strip()  # loại bỏ khoảng trắng ở đầu và cuối
            if not re.match(pattern, expr):
                return ''  # Nếu có biểu thức không hợp lệ, trả về chuỗi rỗng

        return where_clause  # Nếu tất cả các biểu thức hợp lệ, trả về mệnh đề WHERE ban đầu
    def post(self, request): 
        filters = request.data.get('filters', None)  # Default là None nếu không có tham số
        take = int(request.data.get('take', 0))  # Default là 10 nếu không có tham số
        limit = int(request.data.get('limit', 10))  # Default là 10 nếu không có tham số
        allowed_columns = [field.name for field in ExportDeclaration._meta.fields]
        allowed_operators = ["=", "!=", "<", ">", "<=", ">="]
        params = []
        whereClause = ""
        sql = 'SELECT * FROM export_declaration'

        # Thêm các điều kiện vào câu SQL nếu filters được truyền
        if filters:
            filter_conditions = filters
            for condition in filter_conditions:
                if 'field' in condition:
                    if(condition['field'] in allowed_columns):
                        whereClause += f" {condition['field']}"
                if 'operator' in condition:
                    if(condition['operator'] in allowed_operators):
                        whereClause += f" {condition['operator']}"
                if 'value' in condition:
                    whereClause += " %s"
                    params.append(condition['value'])

        sql += f' WHERE {self.parseWhere(whereClause)}'    
        # Thêm LIMIT và OFFSET cho phân trang
        if take > 0:
            sql += " LIMIT %s OFFSET %s"
            params.append(limit)
            params.append(take)

        cursor = connection.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            if len(row) == len(allowed_columns):
                result = dict(zip(allowed_columns, row))
                results.append(result)

        return Response(results, status=status.HTTP_200_OK) 
    def get(self, request, id=None):
        export_declaration = get_object_or_404(ExportDeclaration, declaration_id=id)
        serializer = ExportDeclarationSerializer(export_declaration)
        return Response(serializer.data, status=status.HTTP_200_OK)