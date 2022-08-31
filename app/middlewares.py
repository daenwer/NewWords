import os
import sys

from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from threading import local

from django.db import connection
from django.urls import reverse_lazy, reverse
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.test.utils import CaptureQueriesContext

from app.models import User


# thread_locals = local()


class TokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/login/'):
            token = request.path.split('/login/')[1].rstrip('/')
            # TODO: добваить валидацию на юид
            user = User.objects.filter(token=token)
            if user:
                user = user[0]
                login(request, user)
            # return redirect('admin')
            # TODO: как сделать красиво
            return redirect(f'http://127.0.0.1:8000/admin/', request=request)
            # return reverse('admin')
            # return H('admin')


        print()
        # thread_locals.request = request

    # def process_response(self, request, response):
    #     thread_locals.request = None
    #     return response


# class CourseMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         if request.user.is_authenticated and \
#                 request.path != reverse_lazy('Main:logout'):
#             managed_courses = request.user.get_moderated_courses(
#                 TeacherRoles.get_list(), ids_only=True
#             )
#             attended_courses = request.user.get_attended_courses(ids_only=True)
#             allowed_courses = list(managed_courses) + list(attended_courses)
#             if (
#                 not allowed_courses and
#                 request.path not in [
#                     reverse_lazy('Main:my_access_requests'),
#                     reverse_lazy('Main:settings'),
#                 ] and
#                 not request.path.startswith(settings.MEDIA_URL) and
#                 not request.path.startswith(settings.STATIC_URL)
#             ):
#                 return redirect('Main:my_access_requests')
#             course_in_session = request.session.get('course')
#             if course_in_session not in allowed_courses:
#                 request.session['course'] = \
#                     allowed_courses[0] if allowed_courses else None
#
#
# class RangesMiddleware(MiddlewareMixin):
#     def process_response(self, request, response):
#         if (
#             response.status_code != 200 or
#             not hasattr(response, 'file_to_stream')
#         ):
#             return response
#         http_range = request.META.get('HTTP_RANGE')
#         if not (
#             http_range and http_range.startswith('bytes=') and
#             http_range.count('-') == 1
#         ):
#             return response
#         if_range = request.META.get('HTTP_IF_RANGE')
#         if (
#             if_range and if_range != response.get('Last-Modified') and
#             if_range != response.get('ETag')
#         ):
#             return response
#         file_object = response.file_to_stream
#         stat_object = os.fstat(file_object.fileno())
#         start, end = http_range.split('=')[1].split('-')
#         if not start:  # requesting the last N bytes
#             start = max(0, stat_object.st_size - int(end))
#             end = ''
#         start, end = int(start or 0), int(end or stat_object.st_size - 1)
#         assert 0 <= start < stat_object.st_size, (start, stat_object.st_size)
#         end = min(end, stat_object.st_size - 1)
#         file_object.seek(start)
#         old_read = file_object.read
#         file_object.read = lambda n: old_read(
#             min(n, end + 1 - file_object.tell())
#         )
#         response.status_code = 206
#         response['Content-Length'] = end + 1 - start
#         response['Content-Range'] = 'bytes %d-%d/%d' % (
#             start, end, stat_object.st_size
#         )
#         return response
#
#
# class QueriesAmountMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         self.is_enabled = False
#
#         if (
#             not sys.modules.get('pytest') and
#             settings.COLLECT_QUERIES_AMOUNT and
#             not settings.DEBUG and
#             not set(request.path_info.split('/')).intersection(
#                 {'static', 'media', 'favicon.ico'}
#             )
#         ):
#             self.is_enabled = True
#             self.queries_context = CaptureQueriesContext(connection).__enter__()
#
#     def process_response(self, request, response):
#         if self.is_enabled:
#
#             from Main.tasks import save_queries_amount_task
#
#             self.queries_context.__exit__(None, None, None)
#             save_queries_amount_task.delay(
#                 request.method, request.path_info,
#                 self.queries_context.final_queries
#             )
#         return response
#
#
# class LanguageMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         language_code = Languages.EN.value
#         if request.user.is_authenticated:
#             language_code = request.user.settings.language
#         else:
#             if accept_language := request.META.get('HTTP_ACCEPT_LANGUAGE'):
#                 languages = [
#                     language.split(',')[-1]
#                     for language in accept_language.split(';')
#                     if language.split(',')[-1].isalpha()
#                 ]
#                 available_languages = [
#                     language[0] for language in settings.LANGUAGES
#                 ]
#                 for language in languages:
#                     if language in available_languages:
#                         language_code = language
#                         break
#         translation.activate(language_code)
#         request.session[translation.LANGUAGE_SESSION_KEY] = language_code
