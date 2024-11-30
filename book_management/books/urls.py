from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeView
from .forms import CustomPasswordChangeForm
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 图书相关的路由
    path('books/', views.book_list, name='book_list'),  # 图书列表
    path('books/add/', views.add_book, name='add_book'),  # 添加图书
    path('books/edit/<int:pk>/', views.edit_book, name='edit_book'),  # 编辑图书
    path('books/delete/<int:pk>/', views.delete_book, name='delete_book'),  # 删除图书

    #图书借阅
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
    path('loan_history/', views.loan_history, name='loan_history'),
    path('clear_loan_history/', views.clear_loan_history, name='clear_loan_history'),

    #黑名单管理
    path('blacklisted/', views.blacklisted, name='blacklisted'),
    path('appeal/', views.appeal_blacklist, name='appeal_blacklist'),

    #申诉管理
    path('appeals/', views.view_appeals, name='view_appeals'),
    path('appeals/process/<int:appeal_id>/', views.process_appeal, name='process_appeal'),
    path('appeals/clear/', views.clear_appeals, name='clear_appeals'),

    # 用户相关的路由
    path('register/', views.user_register, name='user_register'),  # 用户注册
    path('login/', views.user_login, name='user_login'),  # 用户登录
    path('logout/', views.user_logout, name='user_logout'),  # 用户登出
    path('profile/', views.user_profile, name='user_profile'),
    path('password_change/', PasswordChangeView.as_view(form_class=CustomPasswordChangeForm,template_name='books/password_change.html'), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='books/password_change_done.html'), name='password_change_done'),
    path('user_management/', views.user_management, name='user_management'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('reset_user_password/<int:user_id>/', views.reset_user_password, name='reset_user_password'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    # 忘记密码
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='books/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='books/password_reset_done.html'), name='password_reset_done'),
    
    # 密码重置
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='books/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='books/password_reset_complete.html'), name='password_reset_complete'),
]