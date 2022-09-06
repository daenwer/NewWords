from django.http import HttpResponse
from django.views import View

from app.tasks import prepare_new_celery_tasks


class TokenVerificationView(View):

    def get(self, request):
        print()
    #     user = User.objects.get(
    #         username__iexact=form.cleaned_data['username']
    #     )
    #     login(self.request, user)
    #     return redirect(request.GET.get('next') or 'Main:index')
    # else:
    #     return render(request, self.template_name, {'form': form})


class ForTestView(View):

    def get(self, request):
        # prepare_new_celery_tasks.delay()
        prepare_new_celery_tasks()
        # send_message(365891631, 'repeat_phrase')
        return HttpResponse({})
