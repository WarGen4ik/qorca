from django.shortcuts import render


def main(request, *args, **kwargs):
    if request.user.is_authenticated:
        return render(request, 'core/index.html', {'user': request.user, 'gender': 'male' if request.user.profile.gender == 1 else 'female'})
    else:
        return render(request, 'core/index.html')
