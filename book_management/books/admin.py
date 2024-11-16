from django.contrib import admin
from .models import Book, Author, Loan
# Register your models here.
# 自定义Loan管理界面
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'loan_date', 'return_date', 'status')  # 在列表中显示的字段
    list_filter = ('status',)  # 添加过滤器
    search_fields = ('book__title', 'borrower__username')  # 添加搜索框功能
# 注册模型
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Loan,LoanAdmin)