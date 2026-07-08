from lxml import etree
from pathlib import Path

mapattrs = {
    'styleCategories', 'maxScale', 'minScale', 'labelsEnabled', 
    'simplifyLocal', 'simplifyAlgorithm', 'readOnly', 'simplifyDrawingHints', 
    'symbologyReferenceScale', 'hasScaleBasedVisibilityFlag', 
    'simplifyDrawingTol', 'simplifyMaxScale'
}

projecttemplate = '../qkan/templates/projekt.qgs'
tree = etree.ElementTree()
qgsxml = tree.parse(projecttemplate)

for i, tag_maplayer in enumerate(qgsxml.findall(".//projectlayers/maplayer")):
    # Neues qml anlegen
    qmlxml = etree.XML("<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n"
                       '<qgis styleCategories="AllStyleCategories" '
                       'maxScale="0" minScale="100000000" labelsEnabled="0" '
                       'simplifyLocal="1" simplifyAlgorithm="0" readOnly="0" '
                       'version="3.28.13-Firenze" simplifyDrawingHints="0" '
                       'symbologyReferenceScale="-1" hasScaleBasedVisibilityFlag="0" '
                       'simplifyDrawingTol="1" simplifyMaxScale="1">\n'
                       '</qgis>'
)
    # Maplayerattribute  übernehmen
    for attr in mapattrs:
        value = tag_maplayer.get(attr)
        if value is not None:
            qmlxml.set(attr, value)
        else:
            qmlxml.clear(attr)

    layername = tag_maplayer.find("./layername").text.replace('/', '_')
    print(f'\n{layername=}')
    active = False

    wfile = Path('../qkan/templates/qml') / f'{layername}.qml'
    with open(wfile, "wb") as layerfile:
        for i, block in enumerate(tag_maplayer):
            tag = block.tag
            if tag == 'flags':
                active = True
            if active and tag not in ('editform', 'editforminitcode'):
                qmlxml.append(block)
        out = etree.ElementTree(qmlxml)
        out.write(layerfile, xml_declaration=True, encoding='utf-8', pretty_print = True)
    qml = open(wfile).read().replace('&gt;', '>')
    open(wfile, 'w').write(qml)
        # layerfile.write(etree.tostring(qmlxml, pretty_print = True))
