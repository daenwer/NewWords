# from asgiref.sync import sync_to_async
#
#
# def check_if_user_is_active(func):
#     def wrapper(*args, **kwargs):
#         # TODO: если except делать юзера не активным, найти ошибку
#         try:
#             func(*args, **kwargs)
#             print('yes ' * 20)
#         except:
#             print('no ' * 50)
#     return wrapper
