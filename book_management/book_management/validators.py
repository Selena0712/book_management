# book_management/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        # 密码至少 8 个字符
        if len(password) < 8:
            raise ValidationError(_('您的密码必须至少包含 8 个字符。'))
        # 密码不能完全是数字
        if password.isdigit():
            raise ValidationError(_('您的密码不能完全是数字。'))
        # 密码必须包含至少一个大写字母
        if password.lower() == password:
            raise ValidationError(_('您的密码必须包含至少一个大写字母。'))

    def get_help_text(self):
        return _('您的密码必须至少包含 8 个字符，不能完全是数字，并且包含至少一个大写字母。')
