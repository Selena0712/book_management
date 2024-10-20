from django.shortcuts import render

# Create your views here.
from .models import Book

def book_list(request):
    books = Book.objects.all()  # 获取所有图书
    return render(request, 'books/book_list.html', {'books': books})