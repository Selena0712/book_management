from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from .forms import CustomUserCreationForm, BookForm, AppealForm, ReturnBookForm, UserProfileForm, CustomPasswordChangeForm, UserEditForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Book, Loan, Appeal, CustomUser
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
User = get_user_model()

def is_admin(user):
    return user.is_staff  # 判断用户是否为管理员

# 错误页面：当用户不是管理员时
def not_admin(request):
    messages.error(request, "你并非管理员，无法使用此功能。")
    return render(request, 'books/not_admin.html')  # 返回错误页面

# 主页视图
def home(request):
    return render(request, 'books/home.html')  # 渲染主页模板

# 用户注册视图
def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # 保存用户
            return redirect('user_login')  # 注册成功后跳转到登录页面
    else:
        form = CustomUserCreationForm()

    return render(request, 'books/register.html', {'form': form})

# 用户登录视图
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # 登录成功后跳转到主页
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})

# 退出登录视图
def user_logout(request):
    logout(request)
    return redirect('home')  # 退出后返回到主页

# 图书列表视图
@login_required
def book_list(request):
    books = Book.objects.all()

    # 获取每个用户的借阅情况
    loaned_books = Loan.objects.filter(user=request.user, return_date__isnull=True).values_list('book', flat=True)

    context = {
        'books': books,
        'loaned_books': loaned_books  # 返回所有用户借阅中的书籍
    }
    return render(request, 'books/book_list.html', context)

# 添加图书视图（仅管理员）
@login_required
@user_passes_test(is_admin, login_url='not_admin')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

# 编辑图书视图（仅管理员）
@login_required
@user_passes_test(is_admin, login_url='not_admin')
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})

# 删除图书视图（仅管理员）
@login_required
@user_passes_test(is_admin, login_url='not_admin')
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

#借阅图书视图
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # 如果用户是管理员，跳过黑名单检查
    if request.user.is_staff:
        is_blacklisted = False  # 管理员不需要检查黑名单
    else:
        # 检查用户是否被列入黑名单
        is_blacklisted = request.user.is_blacklisted

    # 如果用户被列入黑名单，跳转到黑名单页面
    if is_blacklisted:
        messages.error(request, "你已被列入黑名单，无法借书")
        return redirect('blacklisted')

    # 检查用户是否已有未还书籍
    if Loan.objects.filter(user=request.user, return_date__isnull=True).exists():
        messages.error(request, "每个用户只能借阅一本书")
        return redirect('book_list')

    # 检查库存
    if book.stock < 1:
        messages.error(request, "库存不足，无法借阅此书")
        return redirect('book_list')

    # 创建借阅记录
    loan = Loan.objects.create(book=book, user=request.user)
    book.stock -= 1
    book.save()

    # 获取借书日期和应还日期
    borrow_date = loan.borrow_date
    due_date = loan.due_date

    messages.success(request, f"成功借阅《{book.title}》")

    return render(request, 'books/borrow_book.html', {
        'book': book,
        'borrow_date': borrow_date,
        'due_date': due_date
    })

#归还图书视图
@login_required
def return_book(request, book_id):
    # 获取当前用户的借书记录
    book = get_object_or_404(Book, id=book_id)
    loan = Loan.objects.filter(book=book, user=request.user, return_date__isnull=True).first()

    if loan:
        if request.method == 'POST':
            form = ReturnBookForm(request.POST)
            if form.is_valid():
                return_date = form.cleaned_data['return_date']
                loan.return_date = return_date

                # 判断是否逾期，如果逾期则加入黑名单
                if loan.return_date > loan.due_date:
                    request.user.is_blacklisted = True
                    request.user.save()

                loan.save()

                # 更新库存
                book.stock += 1
                book.save()

                messages.success(request, f"成功归还《{book.title}》")
                return redirect('loan_history')  # 跳转到借阅历史页面
        else:
            form = ReturnBookForm()

        return render(request, 'books/return_book.html', {'book': book, 'loan': loan, 'form': form})
    else:
        messages.error(request, "没有找到您的借阅记录，无法还书")
        return redirect('loan_history')  # 跳转到借阅历史页面

#借阅历史视图
@login_required
def loan_history(request):
    if request.user.is_staff:
        # 管理员可以查看所有借阅记录
        loans = Loan.objects.all()
    else:
        # 普通用户只能查看自己的借阅记录
        loans = Loan.objects.filter(user=request.user)

    today = timezone.now().date()  # 获取今天的日期
    return render(request, 'books/loan_history.html', {'loans': loans, 'today': today})

#清除借阅历史视图
@login_required
def clear_loan_history(request):
    if not request.user.is_staff:
        # 普通用户只能清空自己的借阅历史
        Loan.objects.filter(user=request.user).delete()
        messages.success(request, "已清空借阅历史")
    else:
        # 管理员可以清空所有用户的借阅历史
        Loan.objects.all().delete()
        messages.success(request, "已清空所有借阅历史")
    
    return redirect('loan_history')

#黑名单视图
@login_required
def blacklisted(request):
    # 检查当前用户是否被列入黑名单
    if not request.user.is_blacklisted:
        messages.error(request, "你并未被列入黑名单，无法访问此页面。")
        return redirect('book_list')

    # 如果被列入黑名单，渲染黑名单页面
    return render(request, 'books/blacklisted.html')

# 提交申诉
@login_required
def appeal_blacklist(request):
    # 判断用户是否被列入黑名单
    if request.user.is_blacklisted:
        if request.method == 'POST':
            form = AppealForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                # 保存申诉记录
                Appeal.objects.create(user=request.user, reason=reason)
                messages.success(request, "你的申诉已提交，等待管理员审核")
                return redirect('home')
        else:
            form = AppealForm()
        return render(request, 'books/appeal.html', {'form': form})
    else:
        messages.info(request, "你没有被列入黑名单")
        return redirect('home')

# 管理员查看申诉记录
@login_required
def view_appeals(request):
    if not request.user.is_staff:
        # 只有管理员才能查看
        messages.error(request, "你没有权限查看申诉记录")
        return redirect('home')

    # 获取所有申诉记录
    appeals = Appeal.objects.all()
    return render(request, 'books/view_appeals.html', {'appeals': appeals})


# 管理员处理申诉
@login_required
def process_appeal(request, appeal_id):
    if not request.user.is_staff:
        messages.error(request, "你没有权限执行此操作")
        return redirect('home')

    appeal = get_object_or_404(Appeal, id=appeal_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason', '')

        # 如果是接受申诉
        if action == 'approve':
            appeal.is_processed = True
            appeal.processed_by = request.user
            appeal.rejection_reason = None  # 清空拒绝理由（如果有的话）
            appeal.save()

            # 更新用户的黑名单状态
            appeal.user.is_blacklisted = False
            appeal.user.save()

            messages.success(request, f"已处理申诉 {appeal.id} ({appeal.user.username})，已将其从黑名单中移除")
        
        # 如果是拒绝申诉
        elif action == 'reject':
            appeal.is_processed = True
            appeal.processed_by = request.user
            appeal.rejection_reason = rejection_reason  # 保存拒绝理由
            appeal.save()
            messages.success(request, f"已拒绝申诉 {appeal.id} ({appeal.user.username})")

        return redirect('view_appeals')  # 跳转回申诉管理页面

    return render(request, 'books/process_appeal.html', {'appeal': appeal})

#清空申诉记录
@login_required
def clear_appeals(request):
    if not request.user.is_staff:
        messages.error(request, "你没有权限执行此操作")
        return redirect('home')

    # 清除所有已处理的申诉记录
    Appeal.objects.filter(is_processed=True).delete()

    messages.success(request, "已清除所有已处理的申诉记录")
    return redirect('view_appeals')  # 跳转回申诉管理页面

#个人中心
@login_required
def user_profile(request):
    # 获取当前登录用户
    user = request.user
    
    # 如果是POST请求，表示提交了修改的表单
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # 保存用户修改的信息
            messages.success(request, "个人信息已更新")
            return redirect('user_profile')  # 更新后重新渲染用户信息页
    else:
        # 否则，渲染包含当前用户信息的表单
        form = UserProfileForm(instance=user)
    
    return render(request, 'books/user_profile.html', {'form': form})

#密码修改
def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # 保证用户登录状态不被清除
            messages.success(request, "密码修改成功！")
            return redirect('profile')  # 重定向到个人中心页面
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/password_change.html', {'form': form})

# 用户管理视图，只有管理员可以访问
@user_passes_test(lambda u: u.is_staff)
def user_management(request):
    # 获取所有用户
    users = get_user_model().objects.all()
    return render(request, 'books/user_management.html', {'users': users})

# 编辑用户信息视图
@user_passes_test(lambda u: u.is_staff)
def edit_user(request, user_id):
    # 获取需要编辑的用户
    user = get_object_or_404(get_user_model(), id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "用户信息已更新")
            return redirect('user_management')  # 保存后重定向到用户管理页面
    else:
        form = UserEditForm(instance=user)

    return render(request, 'books/edit_user.html', {'form': form, 'user': user})

@user_passes_test(lambda u: u.is_staff)
def reset_user_password(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)

    # 重置密码为特定的密码
    new_password = "Wyj11223344"
    user.set_password(new_password)  # 使用 set_password 重置密码
    user.save()

    messages.success(request, f"{user.username} 的密码已重置为 {new_password}")
    return redirect('user_management')  # 重定向回用户管理页面

# 注销用户账号视图
@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    if user != request.user:  # 防止删除当前登录的管理员
        user.delete()
        messages.success(request, f"{user.username} 的账号已被删除")
    else:
        messages.error(request, "不能删除当前登录的管理员账户")
    
    return redirect('user_management')