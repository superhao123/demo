from django import forms

from user.models import User


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'icon', 'age', 'sex']

    password2 = forms.CharField(max_length=128)  # 确认密码

    def clean_password2(self):
        super().clean()
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('密码不一致')
