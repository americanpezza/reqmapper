import yaml

_configFileName="config.yaml"
_data=None

def _loadconfig():
    global _data
    if _data is None:
        with open(_configFileName, 'r') as stream:
            _data = yaml.safe_load(stream)

def _getAttributes(mandatory):
    _loadconfig()
    attributes = _data['attributes']
    result = {}
    for name, value in attributes.items():
        if (mandatory and value['required']) or (not mandatory and (not value['required'])):
            result[name] = value

    return result

def getPredefinedValueAttributes():
    _loadconfig()

    result = {}
    for name, value in _data['attributes'].items():
        if "values" in value.keys():
            result[name] = { "values": value['values'], "description": value['description'] }

    return result

def getPredefinedValueAttributeDefaults():
    _loadconfig()

    result = {}
    for name, value in _data['attributes'].items():
        if "values" in value.keys():
            result[name] = value['default']

    return result

def getPredefinedValueAttributeFixes():
    _loadconfig()

    result = {}
    for name, value in _data['attributes'].items():
        if "values" in value.keys():
            result[name] = value['aliases']

    return result

def getOptionalAttributes():
    return _getAttributes(False)

def getMandatoryAttributes():
    return _getAttributes(True)

def getAttributeNames():
    _loadconfig()

    return _data['attributes'].keys()

def getAllAttributes():
    _loadconfig()

    return _data['attributes']

def getAttributeMarkers():
    _loadconfig()

    result = {}
    attributes = _data['attributes']
    for name, value in attributes.items():
        if "markers" in value:
            result[name] = value['markers']

    return result

def getColNameProbes():
    _loadconfig()

    result = {}
    attributes = _data['attributes']
    for name, value in attributes.items():
        result[name] = value['colNames']

    return result

def getAttributeMappings():
    _loadconfig()

    result = {}
    attributes = _data['attributes']
    markers = getAttributeMarkers()

    for attr in markers.keys():
        values = attributes[attr]['values']
        val = {}
        for i in range(0, len(values)):
            val[values[i]] = markers[attr][i]

        result[attr] = val

    return result

def getMapStyle(what):
    _loadconfig()

    styles = _data["styles"]
    style = what
    if what not in styles.keys():
        style = "unknown"

    return styles[style]

