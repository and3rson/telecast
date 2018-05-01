from telecast.contrib.rest_framework.server import method


@method()
def add(request, a, b):
    return a + b


@method()
def hello(request, name='stranger'):
    return 'Hello, {}!'.format(name)


@method(http_method_names=['GET'])
def foo(request):
    return 'bar'


def just_a_view(request):
    return 'BOO'
