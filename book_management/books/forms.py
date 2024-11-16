from django import forms
from .models import Loan, Book
from django.contrib.auth.models import User
from django.utils import timezone
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from datetime import timedelta

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date', 'isbn', 'category', 'available_copies']

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['borrower', 'loan_date', 'due_date']  # 包括 loan_date 和 due_date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:  # 只有在新建对象时才设置 loan_date 和 due_date
            # 设置 loan_date 默认值为当前日期
            self.fields['loan_date'].initial = timezone.now().date()

            # 设置 due_date 默认值为 loan_date + 15天
            self.fields['due_date'].initial = timezone.now().date() + timedelta(days=15)

    def clean_due_date(self):
        loan_date = self.cleaned_data.get('loan_date')
        due_date = self.cleaned_data.get('due_date')

        if loan_date and due_date:
            if due_date <= loan_date:  # 确保 due_date 必须在 loan_date 之后
                raise forms.ValidationError("Due date must be after loan date.")
        
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')

        if book:
            # 验证库存数量
            if book.available_copies <= 0:
                raise forms.ValidationError(f'The book "{book.title}" is out of stock.')
        
        return cleaned_data

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['return_date', 'is_returned']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 只在表单初始化时填充 return_date 默认值
        if not self.instance.pk and not self.instance.return_date:
            self.fields['return_date'].initial = timezone.now().date()  # 默认值为当前日期

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='密码')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='确认密码')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("两次密码输入不一致")
        return password_confirm
    
class UserLoginForm(AuthenticationForm):
    pass