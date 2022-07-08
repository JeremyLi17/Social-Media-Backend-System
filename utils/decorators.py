from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(request_attr='query_params', params=None):
    """
    使用decorator -> 进行代码简化
    if ... not in request.query_params: return 400

    E.g:
    @required_params(...)
    def list(self, request, *args, **kwargs):
        ...
    就等价于：
    def list = required_params(list)

    ————————————————————————————————————————————————————————
    required_params结构 -> 接收的是一个function和参数
    ...
    return decorator -> 返回的是一个函数: decorator(list(...))
    然后当list(...)被传入之后, return的是另一个decorator: wrapped_view(list(...))
    因此：总的来说required_params返回的是 decorator(wrapped_view(list(...)))
    """

    # 从效果上来说，参数中写 params=[] 很多时候也没有太大问题
    # 但是从好的编程习惯上来说，函数的参数列表中的值不能是一个 mutable 的参数
    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator函数通过wraps来将view_func里的参数解析出来传递给_wrapped_view
        这里的instance参数其实就是在view_func里的self
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            # getattr -> 等于request.request_attr
            # 因为这里request_attr是string类型，因此只能用getattr
            data = getattr(request, request_attr)

            # params是必须有的参数 -> params里有，但data里没有的param
            missing_params = [
                param
                for param in params
                if param not in data
            ]

            # 如果有缺失的parameter -> 把params拼接一下 return 400
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # 做完检测之后，再去调用被 @required_params 包裹起来的 view_func
            return view_func(instance, request, *args, **kwargs)

        return _wrapped_view

    return decorator
