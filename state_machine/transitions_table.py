# -*- coding: utf-8 -*-
__author__ = 'ecialo'
import transformation as tr
from registry.utility import binary_list
STAND, WALK, CROUCH, RUN, FALL, JUMP = binary_list(6)

class Transitions_Table(object):

    def __init__(self, transition_table=None):
        self._transitions = None
        if transition_table is not None:
            self.load_transitions(transition_table)

    def load_transitions(self, table):
        transitions = {}
        #STAND, WALK, CROUCH, RUN, FALL, JUMP = binary_list(6)
        #table = None
        with open(table) as table:
            macros = {}
            order = None
            state = 0
            i, j = 0, 0
            for line in table:
                if line.strip() == '---':
                    state += 1
                elif state == 0:
                    key, val = line.split()
                    macros[key] = val
                elif state == 1:
                    order = line.split()
                else:
                    row = line.split()
                    print row
                    for i in xrange(len(order)):
                        from_name = order[j]
                        if from_name in macros:
                            from_elem = eval(macros[from_name])
                        else:
                            from_elem = eval(from_name)
                        to_name = order[i]
                        if to_name in macros:
                            to_elem = eval((macros[to_name]))
                        else:
                            to_elem = eval(to_name)
                        transitions[(from_elem, to_elem)] = row[i]
                    j += 1
        self._transitions = transitions

    def get_animation(self, source, from_state, to_state):
        name = self._transitions[(from_state, to_state)]
        if name == 'x':
            raise Exception
        elif name == 'i':
            return tr.Instant()
        elif name == 'r':
            rname = self._transitions[(to_state, from_state)]
            animation = source.find_animation(rname)
            return tr.Reversed_Animation(animation)
        else:
            return source.find_animation(name)