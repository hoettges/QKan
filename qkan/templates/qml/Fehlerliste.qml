<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="1e+08" version="3.22.4-Białowieża" readOnly="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal endField="" durationUnit="min" accumulate="0" startField="" limitMode="0" startExpression="" fixedDuration="0" mode="0" endExpression="" enabled="0" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;name&quot;"/>
      </Option>
      <Option type="int" value="0" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector" showLabelLegend="0"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="warntext">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="warntyp">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="warnlevel">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="layername">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="attrname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="objname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="createdat">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="warntext" name="Warntext"/>
    <alias index="2" field="warntyp" name="Warntyp"/>
    <alias index="3" field="warnlevel" name="Warnlevel"/>
    <alias index="4" field="layername" name="Layername"/>
    <alias index="5" field="attrname" name="Attributname"/>
    <alias index="6" field="objname" name="Objektname"/>
    <alias index="7" field="createdat" name="bearbeitet"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="warntext" expression=""/>
    <default applyOnUpdate="0" field="warntyp" expression=""/>
    <default applyOnUpdate="0" field="warnlevel" expression=""/>
    <default applyOnUpdate="0" field="layername" expression=""/>
    <default applyOnUpdate="0" field="attrname" expression=""/>
    <default applyOnUpdate="0" field="objname" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" exp_strength="0" unique_strength="1" field="pk" notnull_strength="1"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="warntext" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="warntyp" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="warnlevel" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="layername" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="attrname" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="objname" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="createdat" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="warntext"/>
    <constraint exp="" desc="" field="warntyp"/>
    <constraint exp="" desc="" field="warnlevel"/>
    <constraint exp="" desc="" field="layername"/>
    <constraint exp="" desc="" field="attrname"/>
    <constraint exp="" desc="" field="objname"/>
    <constraint exp="" desc="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting notificationMessage="" type="1" id="{ce7efdcf-811f-4b6b-859e-b64a436a7a74}" capture="1" isEnabledOnlyWhenEditable="0" shortTitle="Zoom/Pan zum Objekt" icon="C:/FHAC/hoettges/Kanalprogramme/QKan/qkan/datacheck/jump.png" name="Zoom/Pan zum Objekt" action="from qgis.PyQt import QtWidgets&#xd;&#xa;from qgis.core import Qgis&#xd;&#xa;&#xd;&#xa;obj = '[%objname%]'&#xd;&#xa;attr = '[%attrname%]'&#xd;&#xa;&#xd;&#xa;activeproject = QgsProject().instance()&#xd;&#xa;layername = '[%layername%]'&#xd;&#xa;clayers = activeproject.mapLayersByName(layername)&#xd;&#xa;if not clayers:&#xd;&#xa;    QtWidgets.QMessageBox.information(None, &quot;Fehler im Programmcode der Aktion&quot;, f'Layer &quot;{layername}&quot;nicht definiert')&#xd;&#xa;else:&#xd;&#xa;    clayer = clayers[0]&#xd;&#xa;    clayer.selectByExpression(f&quot;{attr} = '{obj}'&quot;)&#xd;&#xa;    qgis.utils.iface.setActiveLayer(clayer)&#xd;&#xa;    box = clayer.boundingBoxOfSelected()&#xd;&#xa;    canvas = qgis.utils.iface.mapCanvas()&#xd;&#xa;    canvas.zoomToFeatureExtent(box)&#xd;&#xa;">
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting notificationMessage="Meldung" type="1" id="{d4291ae8-f6e0-4b91-aa30-8c3f2954515c}" capture="0" isEnabledOnlyWhenEditable="0" shortTitle="Zoom/Pan zum Objekt" icon="C:/FHAC/hoettges/Kanalprogramme/QKan/qkan/datacheck/jump.png" name="Objekt Aktivieren und Zoom/Pan zum Objekt" action="from qgis.PyQt import QtWidgets&#xa;    from qgis.core import Qgis&#xa;&#xa;    obj = '[%objname%]'&#xa;    attr = '[%attrname%]'&#xa;&#xa;    activeproject = QgsProject().instance()&#xa;    layername = '[%layername%]'&#xa;    clayers = activeproject.mapLayersByName(layername)&#xa;    if not clayers:&#xa;        QtWidgets.QMessageBox.information(None, &quot;Fehler im Programmcode der Aktion&quot;, f'Layer &quot;{layername}&quot;nicht definiert')&#xa;    else:&#xa;        clayer = clayers[0]&#xa;        clayer.selectByExpression(f&quot;{attr} = '{obj}'&quot;)&#xa;        qgis.utils.iface.setActiveLayer(clayer)&#xa;        box = clayer.boundingBoxOfSelected()&#xa;        canvas = qgis.utils.iface.mapCanvas()&#xa;        canvas.zoomToFeatureExtent(box)&#xa;    ">
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="buttonList">
    <columns>
      <column type="actions" width="57" hidden="0"/>
      <column type="field" width="38" name="pk" hidden="1"/>
      <column type="field" width="82" name="warnlevel" hidden="0"/>
      <column type="field" width="93" name="warntext" hidden="0"/>
      <column type="field" width="165" name="layername" hidden="0"/>
      <column type="field" width="99" name="objname" hidden="0"/>
      <column type="field" width="168" name="warntyp" hidden="0"/>
      <column type="field" width="-1" name="attrname" hidden="0"/>
      <column type="field" width="159" name="createdat" hidden="0"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/forms</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>uifilelayout</editorlayout>
  <editable>
    <field editable="1" name="attrname"/>
    <field editable="1" name="beschreibung"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="gruppe"/>
    <field editable="1" name="idname"/>
    <field editable="1" name="layername"/>
    <field editable="1" name="name"/>
    <field editable="1" name="objname"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="warnlevel"/>
    <field editable="1" name="warntext"/>
    <field editable="1" name="warntyp"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="attrname"/>
    <field labelOnTop="0" name="beschreibung"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="gruppe"/>
    <field labelOnTop="0" name="idname"/>
    <field labelOnTop="0" name="layername"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="objname"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="warnlevel"/>
    <field labelOnTop="0" name="warntext"/>
    <field labelOnTop="0" name="warntyp"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="attrname"/>
    <field reuseLastValue="0" name="beschreibung"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="gruppe"/>
    <field reuseLastValue="0" name="idname"/>
    <field reuseLastValue="0" name="layername"/>
    <field reuseLastValue="0" name="name"/>
    <field reuseLastValue="0" name="objname"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="warnlevel"/>
    <field reuseLastValue="0" name="warntext"/>
    <field reuseLastValue="0" name="warntyp"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
