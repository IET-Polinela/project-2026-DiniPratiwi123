from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control rounded-3',
            'placeholder': 'Masukkan nama pengguna'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control rounded-3',
            'placeholder': 'Masukkan email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control rounded-3',
            'placeholder': 'Masukkan sandi'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control rounded-3',
            'placeholder': 'Ulangi sandi'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = False
        user.is_member = True
        if commit:
            user.save()
        return user