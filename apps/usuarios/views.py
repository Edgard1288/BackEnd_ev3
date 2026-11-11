from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm


def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('core:inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.first_name}! Cuenta creada.")
            return redirect('core:inicio')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('core:inicio')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Sesión iniciada correctamente.")
            return redirect(request.POST.get('next') or 'core:inicio')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form, 'next': request.GET.get('next', 'core:inicio')})


def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect('core:inicio')


@login_required
def perfil_usuario(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})