# -*- coding: utf-8 -*-
"""
Что эта хрень должна уметь:
1) Хранить произвольные параметры в 2 экземплярах: изменяемом и не очень.
2) Хранить все текущие модификаторы на характеристики.
3) Предоставлять доступ только к текущим характеристикам
4) При добавлении/удалении модификаторов поддерживать текущие харки в актуальном состоянии
5) В перспективе уведомлять компоненты зависящие от характеристик о том, что те были изменены
"""
__author__ = 'ecialo'
SKIP_PREFIX = len('source_')


class Characteristics(object):

    def __init__(self, name_values):
        self._source_characteristics = name_values.copy()
        self.modifers = []
        for name, val in name_values.iteritems():
            self.__setattr__(name, val)

    def __getattr__(self, item):
        if item.startwith('source_'):
            return self._source_characteristics[item[SKIP_PREFIX::]]
        else:
            return self.__dict__[item]

    def apply(self, modifer):
        self.modifers.append(modifer)
        modifer.apply(self)

    def unapply(self, modifer):
        self.modifers.remove(modifer)
        modifer.unapply(self)