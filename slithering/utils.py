import os
import errno

BASE_DIRECTORY = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    return directory


class cached_property(property):
    def __get__(self, instance, owner):
        if not instance:
            return self._get(instance, owner)

        key = self.fget.func_name
        if key not in instance.__dict__:
            instance.__dict__[key] = \
                self._get(instance, owner)

        return instance.__dict__[key]

    def _get(self, instance, owner):
        return super(cached_property, self).__get__(instance, owner)


class cached_property_on_freeze(cached_property):
    def __get__(self, instance, owner):
        key = self.fget.func_name
        if instance and key in instance.__dict__:
            return instance.__dict__[key]

        if not instance or not instance._frozen:
            return self._get(instance, owner)

        instance.__dict__[key] = self._get(instance, owner)

        return instance.__dict__[key]
