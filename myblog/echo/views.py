# echo_app/views.py
from django.shortcuts import render, redirect
from .forms import EchoForm

def add_echo(request):
    if request.method == 'POST':
        form = EchoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('echo_app:echo_success')
    else:
        form = EchoForm()

    context = {
        'form': form,
        'page_title': 'Tambah Echo Baru'
    }
    return render(request, 'dashboard/echo_form.html', context)

def echo_success(request):
    return render(request, 'dashboard/success_page.html', {'message': 'Echo berhasil ditambahkan!', 'back_url_name': 'echo_app:add_echo'})