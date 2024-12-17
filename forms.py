from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser
from django import forms
from .models import Book, CustomUser
from django.forms import DateInput
from django.utils import timezone
import re

# 自定义注册表单
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
        help_texts = {
            'username': None,  # 移除用户名的帮助信息
            'password1': None,  # 移除密码1的帮助信息
            'password2': None,  # 移除密码2的帮助信息
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None  # 确保密码1没有帮助文本
        self.fields['password2'].help_text = None  # 确保密码2没有帮助文本
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email_address', 'phone_number']  # 包括需要修改的字段
    username = forms.CharField(
        required=True,
        max_length=150,
        error_messages={
            'required': '请输入用户名。',
            'max_length': '用户名不能超过150个字符。',
        },
        help_text='',  # 不显示默认的帮助文本
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 手动设置每个字段的标签
        self.fields['username'].label = '用户名'
        self.fields['email_address'].label = '电子邮件地址'
        self.fields['phone_number'].label = '电话号码'

    # 校验电话号码
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        # 如果用户输入了电话号码，进行格式校验
        if phone_number:
            # 匹配中国大陆的手机号，11位数字，以1开头，第二位数字为3-9之一
            pattern = re.compile(r'^[1][3-9][0-9]{9}$')
            if not pattern.match(phone_number):
                raise forms.ValidationError("请输入有效的电话号码（如：13812345678）")
        
        return phone_number

    # 校验邮箱（Django自带邮箱格式验证）
    def clean_email_address(self):
        email_address = self.cleaned_data.get('email_address')
        return email_address
    
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, 
        help_text=''  # 这里不显示密码的帮助文本
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, 
        help_text=''  # 这里不显示密码的帮助文本
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 手动设置每个字段的标签
        self.fields['old_password'].label = '旧密码'
        self.fields['new_password1'].label = '新密码'
        self.fields['new_password2'].label = '确认新密码'

# 登录表单
class AuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
#图书表单
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'published_date', 'isbn', 'stock', 'description', 'category']
        labels = {
            'title': '标题',
            'author': '作者',
            'publisher': '出版社',
            'published_date': '出版日期',
            'isbn': 'ISBN编号',
            'stock': '库存',
            'description': '描述',
            'category': '类别',
        }

class ReturnBookForm(forms.Form):
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),  # 使用日期输入框
        label="还书日期"  # 自定义标签
    )

class AppealForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label='申诉原因', required=True)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email_address', 'phone_number']
        
    username = forms.CharField(
        required=True,
        max_length=150,
        error_messages={
            'required': '请输入用户名。',
            'max_length': '用户名不能超过150个字符。',
        },
        help_text='',  # 不显示默认的帮助文本
    )