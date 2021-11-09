from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        # response.data['status_code'] = response.status_code
        if response.data.get("detail"):
            response.data['message'] = response.data['detail']
            del response.data['detail']
            # dictionary[new_key] = dictionary.pop(old_key)

    return response