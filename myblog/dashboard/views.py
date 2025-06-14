# dashboard/views.py

from django.shortcuts import render, redirect, get_object_or_404

# Import Models
from resonators.models import Resonator
from build.models import Build

from build.forms import BuildForm


# --- Common Dashboard Views ---
def home_dashboard(request):
    """Halaman utama dashboard, bisa berisi ringkasan atau navigasi."""
    return render(request, 'dashboard/home.html', {})

# --- Resonator Views ---
def resonator_list(request):
    resonators = Resonator.objects.all().order_by('character')
    return render(request, 'dashboard/resonators/resonators_list.html', {'resonators': resonators})


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
