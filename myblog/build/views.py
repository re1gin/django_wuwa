from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import Build

def add_build(request):
    if request.method == 'POST':
        form = Build(request.POST)
        if form.is_valid():
            form.save()
            return redirect('build:build_success')
    else:
        form = Build()

    context = {
        'form': form,
        'page_title': 'Tambah Stat Rekomendasi'
    }
    return render(request, 'dashboard/build_form.html', context)

def build_success(request):
    return render(request, 'dashboard/success_page.html', {'message': 'Stat rekomendasi berhasil ditambahkan!', 'back_url_name': 'build_app:add_stat_final'})