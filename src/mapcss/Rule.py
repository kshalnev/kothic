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

TYPE_MATCHES = {
    "": ("area", "line", "way", "node"),
    "area": ("area", "way"),
    "node": ("node",),
    "way": ("line", "area", "way"),
    "line": ("line", "area")
    }

class Rule:
    def __init__(self, s=''):
        self.runtime_conditions = []
        self.conditions = []
        self.minZoom = 0
        self.maxZoom = 19
        if s == "*":
            s = ""
        self.subject = s # "", "node", "line", "way", "area" or "relation"

    def __repr__(self):
        return "%s|z%s-%s %s %s" % (self.subject, self.minZoom, self.maxZoom, self.conditions, self.runtime_conditions)

    def test(self, obj, tags, zoom):
        """
        obj - string, subject "node", "way", "line" or "area"
        tag - map<string,string>, tags from the classificator
        zoom - int, zoom level
        returns False (if rule does not match) or "::default" (it it is not a class) or class name, if rule matches
        """
        if zoom < self.minZoom or zoom > self.maxZoom:
            return False

        if self.subject != "" and not self.test_feature_compatibility(obj):
            return False

        subpart = "::default"
        for condition in self.conditions:
            res = condition.test(tags)
            if not res:
                return False
            if type(res) != bool:
                subpart = res

        return subpart

    def get_compatible_types(self):
        return TYPE_MATCHES.get(self.subject, (self.subject, ))

    def extract_tags(self):
        a = set()
        for condition in self.conditions:
            a.add(condition.extract_tag())
            if "*" in a:
                a = set(["*"])
                break
        return a

    def test_feature_compatibility(self, obj):
        """
        Checks if feature type is compatible
        """
        if self.subject == obj:
            return True
        if self.subject not in ("way", "area", "line"):
            return False
        elif self.subject == "way" and obj == "line":
            return True
        elif self.subject == "way" and obj == "area":
            return True
        elif self.subject == "area" and obj in ("way", "area"):
            return True
        elif self.subject == "line" and obj in ("way", "line", "area"):
            return True
        else:
            return False
        return True
