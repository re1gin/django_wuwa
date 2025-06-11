from django.shortcuts import render

# weapons_app/views.py
from django.shortcuts import render, redirect
from .forms import WeaponForm

def add_weapon(request):
    if request.method == 'POST':
        form = WeaponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('weapons_app:weapon_success')
    else:
        form = WeaponForm()

    context = {
        'form': form,
        'page_title': 'Tambah Senjata Baru'
    }
    return render(request, 'dashboard/weapon_form.html', context)

def weapon_success(request):
    return render(request, 'dashboard/success_page.html', {'message': 'Senjata berhasil ditambahkan!', 'back_url_name': 'weapons_app:add_weapon'})
