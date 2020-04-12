import config


class InvalidAttribute(Exception):
    pass

class Attribute:
    attributes = config.getPredefinedValueAttributes()
    fixes = config.getPredefinedValueAttributeFixes()
    defaults = config.getPredefinedValueAttributeDefaults()

    def __init__(self, name, value, strict):
        self.name = name
        self.strict = strict
        self.value = self.fixValue(name, value)
        if not self.isValid():
            raise InvalidAttribute("The value '%s' is not valid for attribute '%s'" % (value, name))

    @staticmethod
    def getDescription(t):
        result = None
        if t in Attribute.attributes.keys():
            result = Attribute.attributes[t]['description']

        return result

    @staticmethod
    def getAttributeValues(t):
        result = None
        if t in Attribute.attributes.keys():
            result = Attribute.attributes[t]['values']

        return result

    def fixValue(self, name, value):
        result = value
        if name in self.attributes.keys():
            valid = (result in self.attributes[name]['values'])

            # Fix invalid values if we don't have to be strict
            # ignore case of both the supplied value and the configured values when fixing
            if not valid and not self.strict:
                if value is None:
                    value = ""

                value = value.lower()
                fixed = False

                # if they supplied a void value and there is a default in the config, then let's use it
                if name in self.defaults and value == "":
                    result = self.defaults[name]
                    fixed = True

                # another check: if the value starts with an actual value from the attribute predefined list, let's use this one
                if not fixed:
                    for v in self.attributes[name]['values']:
                        if value.startswith(v.lower()):
                            result = v
                            fixed = True
                            break

                # last check: if we defined an alias in the config, then let's use the correspondent value in the attributes predefined values
                if not fixed:
                    if name in self.fixes.keys() and value in self.fixes[name]:
                        result = self.attributes[name]['values'][self.fixes[name].index(value)]

        return result

    def getValue(self):
        return self.value

    def getName(self):
        return self.name

    def isValid(self):
        valid = (self.name in self.attributes.keys()) and (self.value in self.attributes[self.name]['values'])

        return valid

    def getOrder(self):
        c = -1

        if self.isValid():
            c = self.attributes[self.name]['values'].index(self.value)

        return c

class Requirement:
    def __init__(self, category, strict, attributes):
        self.reqCategory = category
        self.strict = strict

        self._setupRequiredAttrs(attributes)
        self._setupPredefinedValueAttributes(attributes)

    def getAttribute(self, name):
        result = None
        for a in self.attributes:
            if a.getName() == name:
                result = a.getValue()

        return result

    def _setupPredefinedValueAttributes(self, attributes):
        newattributes = []

        predefAttrs = config.getPredefinedValueAttributes()
        for name in predefAttrs.keys():
            if name in attributes.keys():
                newattributes.append(  Attribute(name, attributes[name], self.strict) )

        self.attributes = newattributes

    def _setupRequiredAttrs(self, attributes):
        reqAttrs = config.getMandatoryAttributes()
        essential = reqAttrs.keys()
        essentialValues = attributes.keys()

        if ("ID" not in essential) or ("CodeName" not in essential) or ("Requirement" not in essential) or ("Link" not in essential):
            raise Exception("For a valid requirement definition, all essential attributes ('ID', 'CodeName', 'Requirement' and 'Link') must be configured as required. Possible mistake in the configuration file?")

        if ("ID" not in essentialValues) or ("CodeName" not in essentialValues) or ("Requirement" not in essentialValues) or ("Link" not in essentialValues):
            raise Exception("Some essential attribute values are missing: %s" % essentialValues)

        self.id = attributes['ID']
        self.reqID = attributes['CodeName']
        self.text = attributes['Requirement']
        self.links = str(attributes['Link']).split("\n")
        if len(self.links) > 0 and self.links[0] == "":
            self.links = []

    def getAttributes(self):
        attrs = []
        for a in self.attributes:
            attrs.append(Attribute(a.getName(), a.getValue(), a.strict))

        return attrs

    def getDomain(self):
        return self.getAttribute("SecurityDomain")

    def getLinks(self):
        return self.links

    def getID(self):
        return self.reqID

    def __repr__(self):
        return ("%s -- %s" % (self.reqID, self.getText()))

    def getText(self):
        return self.text

    def getFullText(self):
        return self.text

    def getCategory(self):
        return self.reqCategory

