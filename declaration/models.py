from django.db import models

class ExportDeclaration(models.Model):
    declaration_id = models.CharField(max_length=36, primary_key=True)  # Tự tăng ID
    declaration_code = models.TextField(max_length=100)  # Mã khai báo
    declaration_status = models.IntegerField()  # Trạng thái khai báo
    
    class Meta:
        db_table = 'export_declaration'
    def __str__(self):
        return self.declaration_code
    