from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm

import datetime as dt

class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "signup.html"


def year(request):
    year = dt.datetime.now().year
    return {
        'year': year,
    }
