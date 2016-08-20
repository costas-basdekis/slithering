class StrategyCreator(object):
    @classmethod
    def create(cls, item, **kwargs):
        class_for_item = cls.for_item(item)
        for_item = class_for_item(item=item, **kwargs)
        return for_item.create_item()

    @classmethod
    def for_item(cls, item):
        return cls

    def create_item(self):
        raise NotImplementedError()
