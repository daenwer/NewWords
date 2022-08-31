# from django.contrib.admin.sites import DefaultAdminSite
from django.shortcuts import render
from django.views import View
from django.views.generic import FormView

from app.models import User


# from app.models import User


# Create your views here.


# class NewAdmin(DefaultAdminSite):
#     def _setup(self, *args, **kwargs):
#         user = User.objects.filter(is_superuser=True).first()
#         print()
#         super()._setup()
#
#
# site = NewAdmin()


class TokenVerification(View):

    def get(self, request):
        print()
    #     user = User.objects.get(
    #         username__iexact=form.cleaned_data['username']
    #     )
    #     login(self.request, user)
    #     return redirect(request.GET.get('next') or 'Main:index')
    # else:
    #     return render(request, self.template_name, {'form': form})


