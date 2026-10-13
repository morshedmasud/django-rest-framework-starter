from rest_framework import renderers


class Renderer(renderers.JSONRenderer):
    """
    Wraps every JSON response in one envelope:
        {"success": bool, "status_code": int, "message": str, "data": ..., "errors": [...]}
    Error bodies come from accounts.utils.custom_exception_handler.
    """
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = (renderer_context or {}).get('response')
        status_code = response.status_code if response is not None else 200

        if status_code == 204:
            return b''

        if status_code >= 400:
            if isinstance(data, dict) and 'errors' in data:
                message, errors = data.get('message', ''), data['errors']
            else:
                message, errors = '', data
            body = {
                'success': False,
                'status_code': status_code,
                'message': message,
                'data': None,
                'errors': errors,
            }
        else:
            message = ''
            if isinstance(data, dict) and set(data) == {'message'}:
                message, data = data['message'], None
            body = {
                'success': True,
                'status_code': status_code,
                'message': message,
                'data': data,
            }

        return super().render(body, accepted_media_type, renderer_context)
