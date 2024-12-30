from django.shortcuts import render

# Create your views here.
# export/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from ..models import ExportDeclaration
from ..serializers import ExportDeclarationSerializer
import re
from enums.mode_enum import ModeEnum
from django.core.paginator import Paginator, EmptyPage

class ExportDeclarationList(ModelViewSet):
    """
    Dùng ModelViewSet để có sẵn các method cơ bản CRUD, chỉ viết lại những method cần (@action ở dưới)
    """
    queryset = ExportDeclaration.objects.all()
    serializer_class = ExportDeclarationSerializer
    @action(detail=False, methods=['post'])
    def get_list(self, request):
        """
        Lấy danh sách tờ khai theo điều kiện
        + filters: Danh sách các trường lọc
        + take: trang số mấy
        + limit: số lượng bản ghi cần lấy
        """
        # parse param từ client
        filters = request.data.get('filters', None)  # Default là None nếu không có tham số
        take = int(request.data.get('take', 0))  # Trang hiện tại
        limit = int(request.data.get('limit', 10))  # Số lượng bản ghi

        # Danh sách các cột, biểu thức có thể so sánh
        allowed_columns = [field.name for field in ExportDeclaration._meta.fields]
        allowed_operators = ["=", "!=", "<", ">", "<=", ">="]

        # Xây dựng các điều kiện filter động
        filter_kwargs = {}

        if filters:
            for condition in filters:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')

                # Kiểm tra trường hợp filter hợp lệ
                if field not in allowed_columns:
                    return Response({"error": f"wrong field {field}"}, status=status.HTTP_400_BAD_REQUEST)

                if operator not in allowed_operators:
                    return Response({"error": f"wrong operator {operator}"}, status=status.HTTP_400_BAD_REQUEST)

                # Xử lý giá trị lọc theo operator
                if operator == "=":
                    filter_kwargs[f'{field}'] = value
                elif operator == "!=":
                    filter_kwargs[f'{field}__neq'] = value  # Django ORM không hỗ trợ trực tiếp "!=" nhưng có thể dùng '__neq'
                elif operator == "<":
                    filter_kwargs[f'{field}__lt'] = value
                elif operator == ">":
                    filter_kwargs[f'{field}__gt'] = value
                elif operator == "<=":
                    filter_kwargs[f'{field}__lte'] = value
                elif operator == ">=":
                    filter_kwargs[f'{field}__gte'] = value

        # Sử dụng filter() để lọc theo các điều kiện đã xây dựng
        queryset = ExportDeclaration.objects.filter(**filter_kwargs)

        # Thực hiện phân trang nếu cần
        # Tạo Paginator để phân trang
        paginator = Paginator(queryset, limit)

        try:
            # Lấy trang cần thiết
            page_obj = paginator.page(take)
        except EmptyPage:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)

         # Chuyển kết quả thành dạng list
        results = list(page_obj.object_list.values())

        return Response(results, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'])
    def save_declaration(self, request):
        """
        Thực hiện lưu/sửa bản ghi tờ khai
        mode: 1 - insert, 2 - update
        """
        # Lấy mode từ request
        mode = request.data.get('mode', 1)  # Mặc định là mode 1 (thêm mới)
        record = request.data.get('record')

        # Nếu mode là 1 (thêm mới)
        if mode == ModeEnum.ADD.value:
            serializer = ExportDeclarationSerializer(data=record)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Nếu mode là 2 (sửa bản ghi)
        elif mode == ModeEnum.UPDATE.value:
            # Tìm bản ghi theo `declaration_id`
            try:
                export_declaration = ExportDeclaration.objects.get(declaration_id=record.get('declaration_id'))
            except ExportDeclaration.DoesNotExist:
                return Response({"detail": "Bản ghi không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

            # Cập nhật bản ghi
            serializerUpdate = ExportDeclarationSerializer(export_declaration, data=record, partial=True)
            if serializerUpdate.is_valid():
                serializerUpdate.save()
                return Response(serializerUpdate.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Trả về lỗi nếu mode không hợp lệ
        return Response({"detail": "Mode không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
    