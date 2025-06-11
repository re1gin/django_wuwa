# dashboard/views.py

from django.shortcuts import render, redirect, get_object_or_404

# Import Models
from resonators.models import Resonator
from weapon.models import Weapon
from build.models import Build
from echo.models import Echo

# Import Forms dari aplikasi masing-masing
from resonators.forms import ResonatorForm
from weapon.forms import WeaponForm
from build.forms import BuildForm
from echo.forms import EchoForm


# --- Common Dashboard Views ---
def home_dashboard(request):
    """Halaman utama dashboard, bisa berisi ringkasan atau navigasi."""
    return render(request, 'dashboard/home.html', {})

# --- Resonator Views ---
def resonator_list(request):
    resonators = Resonator.objects.all().order_by('character')
    return render(request, 'dashboard/resonators/resonators_list.html', {'resonators': resonators})

def resonator_create(request):
    if request.method == 'POST':
        form = ResonatorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:resonators_list')
    else:
        form = ResonatorForm()
    return render(request, 'dashboard/resonators/resonators_form.html', {'form': form, 'title': 'Tambah Resonator Baru'})

def resonator_detail_update(request, pk):
    resonator = get_object_or_404(Resonator, pk=pk)
    if request.method == 'POST':
        form = ResonatorForm(request.POST, instance=resonator)
        if form.is_valid():
            form.save()
            return redirect('dashboard:resonator_detail_update', pk=resonator.pk)
    else:
        form = ResonatorForm(instance=resonator)
    return render(request, 'dashboard/resonators/resonators_form.html', {'form': form, 'resonator': resonator, 'title': f'Edit Resonator: {resonator.character}'})

def resonator_delete(request, pk):
    resonator = get_object_or_404(Resonator, pk=pk)
    if request.method == 'POST':
        resonator.delete()
        return redirect('dashboard:resonator_list')
    return render(request, 'dashboard/resonators/resonators_confirm_delete.html', {'resonator': resonator})

# --- Weapon Views ---
def weapon_list(request):
    weapons = Weapon.objects.all().order_by('nama')
    return render(request, 'dashboard/weapon/weapon_list.html', {'weapons': weapons})

def weapon_create(request):
    if request.method == 'POST':
        form = WeaponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:weapon_list')
    else:
        form = WeaponForm()
    return render(request, 'dashboard/weapon_form.html', {'form': form, 'title': 'Tambah Senjata Baru'})

def weapon_detail_update(request, pk):
    weapon = get_object_or_404(Weapon, pk=pk)
    if request.method == 'POST':
        form = WeaponForm(request.POST, instance=weapon)
        if form.is_valid():
            form.save()
            return redirect('dashboard:weapon_detail_update', pk=weapon.pk)
    else:
        form = WeaponForm(instance=weapon)
    return render(request, 'dashboard/weapon_form.html', {'form': form, 'weapon': weapon, 'title': f'Edit Senjata: {weapon.nama}'})

def weapon_delete(request, pk):
    weapon = get_object_or_404(Weapon, pk=pk)
    if request.method == 'POST':
        weapon.delete()
        return redirect('dashboard:weapon_list')
    return render(request, 'dashboard/weapon_confirm_delete.html', {'weapon': weapon})


def build_list(request):
    builds = Build.objects.all().order_by('character_id')
    return render(request, 'dashboard/build/build_list.html', {'builds': builds})

def build_create(request):
    if request.method == 'POST':
        form = BuildForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:build_list')
    else:
        form = BuildForm()
    return render(request, 'dashboard/build/build_form.html', {'form': form, 'title': 'Tambah Build Baru'})

def build_detail_update(request, pk):
    build = get_object_or_404(Build, pk=pk)
    if request.method == 'POST':
        form = BuildForm(request.POST, instance=build)
        if form.is_valid():
            form.save()
            return redirect('dashboard:build_detail_update', pk=build.pk)
    else:
        form = BuildForm(instance=build)
    return render(request, 'dashboard/build/build_form.html', {'form': form, 'build': build, 'title': f'Edit Build untuk {build.character_id}'})

def build_delete(request, pk):
    build = get_object_or_404(Build, pk=pk)
    if request.method == 'POST':
        build.delete()
        return redirect('dashboard:build_list')
    return render(request, 'dashboard/build/build_confirm_delete.html', {'build': build})

# --- Echo Views ---
def echo_list(request):
    echoes = Echo.objects.all().order_by('nama')
    return render(request, 'dashboard/echo/echo_list.html', {'echoes': echoes})

def echo_create(request):
    if request.method == 'POST':
        form = EchoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:echo_list')
    else:
        form = EchoForm()
    return render(request, 'dashboard/echo/echo_form.html', {'form': form, 'title': 'Tambah Echo Set Baru'})

def echo_detail_update(request, pk):
    echo = get_object_or_404(Echo, pk=pk)
    if request.method == 'POST':
        form = EchoForm(request.POST, instance=echo)
        if form.is_valid():
            form.save()
            return redirect('dashboard:echo_detail_update', pk=echo.pk)
    else:
        form = EchoForm(instance=echo)
    return render(request, 'dashboard/echo/echo_form.html', {'form': form, 'echo': echo, 'title': f'Edit Echo Set: {echo.nama}'})

def echo_delete(request, pk):
    echo = get_object_or_404(Echo, pk=pk)
    if request.method == 'POST':
        echo.delete()
        return redirect('dashboard:echo_list')
    return render(request, 'dashboard/echo_confirm_delete.html', {'echo': echo})