#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    This file is part of kothic, the realtime map renderer.

#   kothic is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   kothic is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with kothic.  If not, see <http://www.gnu.org/licenses/>.

import re

class Condition:
    def __init__(self, t, params):
        if type(params) == type(str()):
            params = (params,)
        self.type = t # eq, regex, lt, gt etc.
        self.params = params # e.g. ('highway','primary')
        self.callable = self.method_dummy
        if t == 'eq':
            if self.params[0][:2] == "::":
                self.callable = self.method_class
            else:
                self.callable = self.method_eq
        elif t == 'ne':
            self.callable = self.method_ne
        elif t == 'regex':
            self.regex = re.compile(self.params[0], re.I)
            self.callable = self.method_regex
        elif t == 'true':
            self.callable = self.method_true
        elif t == 'untrue':
            self.callable = self.method_untrue
        elif t == 'set':
            self.callable = self.method_set
        elif t == 'unset':
            self.callable = self.method_unset
        elif t == '<':
            self.callable = self.method_less
        elif t == '<=':
            self.callable = self.method_less_or_eq
        elif t == '>':
            self.callable = self.method_greater
        elif t == '>=':
            self.callable = self.method_greater_or_eq

    def method_dummy(self, tags):
        return False

    def method_class(self, tags):
        return self.params[1]

    def method_eq(self, tags):
        return tags[self.params[0]] == self.params[1]

    def method_ne(self, tags):
        return tags.get(self.params[0], "") != self.params[1]

    def method_regex(self, tags):
        return bool(self.regex.match(tags[self.params[0]]))

    def method_true(self, tags):
        return tags.get(self.params[0]) == 'yes'

    def method_untrue(self, tags):
        return tags.get(self.params[0]) == 'no'

    def method_set(self, tags):
        if self.params[0] in tags:
            return tags[self.params[0]] != ''
        return False

    def method_unset(self, tags):
        if self.params[0] in tags:
            return tags[self.params[0]] == ''
        return True

    def method_less(self, tags):
        return (Number(tags[self.params[0]]) < Number(self.params[1]))

    def method_less_or_eq(self, tags):
        return (Number(tags[self.params[0]]) <= Number(self.params[1]))

    def method_greater(self, tags):
        return (Number(tags[self.params[0]]) > Number(self.params[1]))

    def method_greater_or_eq(self, tags):
        return (Number(tags[self.params[0]]) >= Number(self.params[1]))

    def extract_tag(self):
        if self.params[0][:2] == "::" or self.type == "regex":
            return "*" # unknown
        return self.params[0]

    def test(self, tags):
        """
        Test a hash against this condition
        """
        try:
            return self.callable(tags)
        except KeyError:
            pass
        return False

    def __repr__(self):
        t = self.type
        params = self.params
        if t == 'eq' and params[0][:2] == "::":
            return "::%s" % (params[1])
        if t == 'eq':
            return "%s=%s" % (params[0], params[1])
        if t == 'ne':
            return "%s=%s" % (params[0], params[1])
        if t == 'regex':
            return "%s=~/%s/" % (params[0], params[1])
        if t == 'true':
            return "%s?" % (params[0])
        if t == 'untrue':
            return "!%s?" % (params[0])
        if t == 'set':
            return "%s" % (params[0])
        if t == 'unset':
            return "!%s" % (params[0])
        if t == '<':
            return "%s<%s" % (params[0], params[1])
        if t == '<=':
            return "%s<=%s" % (params[0], params[1])
        if t == '>':
            return "%s>%s" % (params[0], params[1])
        if t == '>=':
            return "%s>=%s" % (params[0], params[1])
        return "%s %s " % (self.type, repr(self.params))

    def __eq__(self, a):
        return (self.params == a.params) and (self.type == a.type)

def Number(tt):
    """
    Wrap float() not to produce exceptions
    """
    try:
        return float(tt)
    except ValueError:
        return 0

