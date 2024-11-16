from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 创建作者模型
class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="姓名")
    birth_date = models.DateField(null=True, blank=True, verbose_name="出生日期")
    nationality = models.CharField(max_length=50, verbose_name="国籍")

    def __str__(self):
        return self.name

# 创建书籍模型
class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="书名")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="作者")
    published_date = models.DateField(verbose_name="出版日期")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    category = models.CharField(max_length=50, verbose_name="分类")
    available_copies = models.IntegerField(default=1, verbose_name="库存数量")

    def __str__(self):
        return self.title

# 创建借阅记录模型（只保留Loan）
class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_date = models.DateField(default=timezone.now)  # 自动设置默认日期
    return_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50, 
        choices=[('borrowed', 'Borrowed'), ('returned', 'Returned')], 
        default='borrowed'
    )

    def save(self, *args, **kwargs):
        # 自动同步 status 和 is_returned 字段
        if self.is_returned:
            self.status = 'returned'
        else:
            self.status = 'borrowed'
        super(Loan, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - {self.borrower.username}"