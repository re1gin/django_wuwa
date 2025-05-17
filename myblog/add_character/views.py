from django.shortcuts import render, redirect
from .forms import CharacterForm, BaseStatForm, FinalStatForm

def add_character(request):
    if request.method == 'POST':
        char_form = CharacterForm(request.POST, request.FILES)
        base_form = BaseStatForm(request.POST)
        final_form = FinalStatForm(request.POST)

        if char_form.is_valid() and base_form.is_valid() and final_form.is_valid():
            base_stat = base_form.save()
            final_stat = final_form.save()
            character = char_form.save(commit=False)
            character.base_stat = base_stat
            character.final_stat = final_stat
            character.save()
            return redirect('character-add')  # Redirect ke halaman yang sama
    else:
        char_form = CharacterForm()
        base_form = BaseStatForm()
        final_form = FinalStatForm()

    return render(request, 'add_character.html', {
        'char_form': char_form,
        'base_form': base_form,
        'final_form': final_form
    })
