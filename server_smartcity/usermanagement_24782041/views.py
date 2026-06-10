from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.views import View

from .forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = 'usermanagement_24782041/login.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['username'].widget.attrs.update({
            'class': 'form-control rounded-3',
            'placeholder': 'Masukkan nama pengguna'
        })
        form.fields['password'].widget.attrs.update({
            'class': 'form-control rounded-3',
            'placeholder': 'Masukkan sandi'
        })
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Login berhasil.')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Logout berhasil.')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'usermanagement_24782041/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrasi berhasil. Silakan login.')
            return redirect('login')
        return render(request, 'usermanagement_24782041/register.html', {'form': form})