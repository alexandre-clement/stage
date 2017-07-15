
class Language(dict):

    def __getitem__(self, item):
        if item not in self:
            def metaclass(name, bases, attributes):
                self[item] = type(name, bases, attributes)
                return self[item]
            return metaclass
        return super(Language, self).__getitem__(item)


language = Language()

class Zero(metaclass=language['Z']):
    pass

print(language["Z"])