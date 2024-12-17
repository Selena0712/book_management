from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)  # 标识是否为管理员
    is_blacklisted = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # 电话号码
    email_address = models.EmailField(max_length=255, blank=True, null=True)  # 邮箱地址

class Book(models.Model):
    # 图书名称
    title = models.CharField(max_length=200)
    # 作者
    author = models.CharField(max_length=200)
    # 出版社
    publisher = models.CharField(max_length=200)
    # 出版日期
    published_date = models.DateField()
    # ISBN
    isbn = models.CharField(max_length=13, unique=True)
    # 库存数量
    stock = models.PositiveIntegerField(default=0)
    # 描述
    description = models.TextField()
    # 类别（使用一个Choice字段来选择类别）
    CATEGORY_CHOICES = [
        ('fiction', '小说'),
        ('non_fiction', '非小说'),
        ('education', '教育'),
        ('science', '科学'),
        ('technology', '技术'),
        ('arts', '艺术'),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='fiction',
    )
    
    def __str__(self):
        return self.title
    
class Loan(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 使用 settings.AUTH_USER_MODEL
    borrow_date = models.DateField(default=timezone.now)  # 默认是当前时间
    due_date = models.DateField(null=True, blank=True)  # 应还日期
    return_date = models.DateField(null=True, blank=True)  # 还书日期
    is_blacklisted = models.BooleanField(default=False)  # 是否被列入黑名单

    def save(self, *args, **kwargs):
        if not self.due_date:
            # 默认应还日期为借书日期 + 15 天
            self.due_date = self.borrow_date + timedelta(days=15)

        # 检查是否逾期并自动更新黑名单状态
        if self.return_date and self.return_date > self.due_date:
            self.is_blacklisted = True  # 逾期后自动加入黑名单
        
        super(Loan, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
    
class Appeal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appeals')
    reason = models.TextField()  # 申诉理由
    date_submitted = models.DateTimeField(auto_now_add=True)  # 申诉提交时间
    is_processed = models.BooleanField(default=False)  # 是否已处理
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_appeals')  # 处理人（管理员）
    rejection_reason = models.TextField(null=True, blank=True)  # 拒绝原因

    def __str__(self):
        return f"申诉 {self.id} - {self.user.username}"