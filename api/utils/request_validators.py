from urllib.parse import urlparse


def validate_url(url):
    parsed_url = urlparse(url)
    return all([parsed_url.scheme, parsed_url.netloc])


def validate_method(method):
    return method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']


def validate_headers(headers):
    if not isinstance(headers, dict):
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in headers.items())


def validate_body(body):
    return isinstance(body, dict)


def validate_params(params):
    if not isinstance(params, dict):
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in params.items())
