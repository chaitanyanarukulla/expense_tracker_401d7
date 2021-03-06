def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('detail', '/expenses/{id:\d+}')
    config.add_route('create', '/expenses/new-expense')
    config.add_route('update', '/expenses/{id:\d+}/edit')
    config.add_route('delete', '/expenses/{id:\d+}/delete')
    config.add_route('api_detail', '/api/expenses/{id:\d+}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
