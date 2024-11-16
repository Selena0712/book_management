from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),  # 将根路径指向图书列表
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('books/loan/<int:book_id>/', views.loan_book, name='loan_book'),  # 借书
    path('books/return/<int:loan_id>/', views.return_book, name='return_book'),  # 还书
    path('loan_history/', views.loan_history, name='loan_history'),
    path('clear-loan-history/', views.clear_loan_history, name='clear_loan_history'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
