from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegistrationForm
from .models import Book, Loan
from .forms import BookForm, LoanForm, ReturnForm
from .forms import UserLoginForm

# Create your views here.
def book_list(request):
    books = Book.objects.all()
    books_with_loans = []

    for book in books:
        # 获取未归还的借阅记录
        unreturned_loan = book.loan_set.filter(is_returned=False).first()  # 获取第一个未归还的借阅记录
        books_with_loans.append({
            'book': book,
            'unreturned_loan': unreturned_loan
        })
    
    return render(request, 'books/book_list.html', {'books_with_loans': books_with_loans})

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()  # 保存新图书
            return redirect('book_list')  # 保存后重定向到图书列表页面
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})

def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})

def delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/delete_book.html', {'book': book})

def loan_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.book = book  # 关联当前图书
            loan.loan_date = form.cleaned_data['loan_date']  # 使用表单中的 loan_date
            loan.due_date = form.cleaned_data['due_date']  # 使用表单中的 due_date

            loan.save()

            # 更新图书的可借副本数
            book.available_copies -= 1
            book.save()

            return redirect('book_list')  # 借阅成功后，跳转到书籍列表页面
    else:
        # 自动填充 loan_date 和 due_date（due_date = loan_date + 15天）
        initial_data = {
            'loan_date': timezone.now().date(),
            'due_date': timezone.now().date() + timedelta(days=15),
        }
        form = LoanForm(initial=initial_data)  # 使用初始数据填充表单

    return render(request, 'books/loan_book.html', {'form': form, 'book': book})

def return_book(request, loan_id):
    # 获取借阅记录对象
    loan = get_object_or_404(Loan, pk=loan_id)
    
    if request.method == 'POST':
        # 使用 ReturnForm 处理归还表单
        form = ReturnForm(request.POST, instance=loan)
        
        if form.is_valid():
            # 获取表单提交的数据
            loan = form.save(commit=False)  # 表单有效，暂时不提交数据库
            
            # 设置归还日期，确保使用表单中的数据
            loan.return_date = form.cleaned_data['return_date'] if form.cleaned_data.get('return_date') else timezone.now().date()
            loan.is_returned = True  # 标记为已归还
            loan.status = 'returned'  # 更新状态为已归还
            
            # 更新书籍的可借副本数量
            loan.book.available_copies += 1
            loan.book.save()  # 保存图书
            loan.save()  # 保存借阅记录
            
            return redirect('book_list')  # 归还成功后重定向到图书列表
            
    else:
        form = ReturnForm(instance=loan)  # 如果是GET请求，则直接显示归还表单
    
    return render(request, 'books/return_book.html', {'form': form, 'loan': loan})


def loan_history(request):
    loans = Loan.objects.all()  # 或者根据用户过滤 Loan.objects.filter(borrower=request.user)
    return render(request, 'books/loan_history.html', {'loans': loans})

def clear_loan_history(request):
    if request.method == 'POST':
        # 删除所有借阅记录
        Loan.objects.all().delete()

        # 显示成功消息
        messages.success(request, "所有借阅记录已成功删除。")
        return redirect('book_list')  # 重定向到图书列表页面
    
    return render(request, 'books/clear_loan_history.html')  # 渲染清空借阅历史页面

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])  # 对密码进行加密
            user.save()
            login(request, user)  # 用户注册后自动登录
            return redirect('book_list')  # 注册后重定向到书籍列表页面
    else:
        form = UserRegistrationForm()
    return render(request, 'books/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # 用户登录
            return redirect('book_list')  # 登录后重定向到书籍列表页面
    else:
        form = UserLoginForm()
    return render(request, 'books/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('book_list')  # 退出后重定向到书籍列表页面