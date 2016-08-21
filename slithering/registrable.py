class Registrable(object):
    pass


def registrable(cls):
    keys = set()
    for key in dir(cls):
        try:
            value = getattr(cls, key, None)
        except Exception:
            continue
        if value is Registrable or isinstance(value, Registrable):
            keys.add(key)

    def make_register_func(_key):
        def register_key(_cls, cls_to_register):
            setattr(_cls, _key, cls_to_register)
            return cls_to_register

        register_key.func_name = 'register_%s' % _key

        return register_key

    attrs = {
        key: None
        for key in keys
    }
    attrs.update({
        register_func.func_name: classmethod(register_func)
        for register_func in map(make_register_func, keys)
    })

    for key, value in attrs.iteritems():
        setattr(cls, key, value)

    return cls
