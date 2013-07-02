DATABASES = {
    'default': dj_database_url.config(default='sqlite:///firetracker.sqlite')
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')