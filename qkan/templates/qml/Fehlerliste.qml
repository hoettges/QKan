<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" version="3.20.1-Odense" minScale="1e+08" readOnly="0" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal durationField="" startField="" accumulate="0" durationUnit="min" fixedDuration="0" startExpression="" enabled="0" endField="" mode="0" endExpression="">
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
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
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
    <field configurationFlags="None" name="name">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="gruppe">
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
    <field configurationFlags="None" name="idname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="pk"/>
    <alias index="1" name="" field="name"/>
    <alias index="2" name="" field="gruppe"/>
    <alias index="3" name="" field="warntext"/>
    <alias index="4" name="" field="warnlevel"/>
    <alias index="5" name="" field="layername"/>
    <alias index="6" name="" field="idname"/>
  </aliases>
  <defaults>
    <default expression="" applyOnUpdate="0" field="pk"/>
    <default expression="" applyOnUpdate="0" field="name"/>
    <default expression="" applyOnUpdate="0" field="gruppe"/>
    <default expression="" applyOnUpdate="0" field="warntext"/>
    <default expression="" applyOnUpdate="0" field="warnlevel"/>
    <default expression="" applyOnUpdate="0" field="layername"/>
    <default expression="" applyOnUpdate="0" field="idname"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="1" exp_strength="0" constraints="3" field="pk" unique_strength="1"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="name" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="gruppe" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="warntext" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="warnlevel" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="layername" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" constraints="0" field="idname" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="name"/>
    <constraint exp="" desc="" field="gruppe"/>
    <constraint exp="" desc="" field="warntext"/>
    <constraint exp="" desc="" field="warnlevel"/>
    <constraint exp="" desc="" field="layername"/>
    <constraint exp="" desc="" field="idname"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting type="1" notificationMessage="" icon="C:/FHAC/hoettges/Kanalprogramme/QKan/qkan/datacheck/jump.png" action="from qgis.PyQt import QtWidgets&#xd;&#xa;from qgis.core import Qgis&#xd;&#xa;&#xd;&#xa;objname = '[%name%]'&#xd;&#xa;attr = '[%idname%]'&#xd;&#xa;&#xd;&#xa;activeproject = QgsProject().instance()&#xd;&#xa;layername = '[%layername%]'&#xd;&#xa;clayers = activeproject.mapLayersByName(layername)&#xd;&#xa;if not clayers:&#xd;&#xa;    QtWidgets.QMessageBox.information(None, &quot;Fehler im Programmcode der Aktion&quot;, f'Layer &quot;{layername}&quot;nicht definiert')&#xd;&#xa;else:&#xd;&#xa;    clayer = clayers[0]&#xd;&#xa;    clayer.selectByExpression(f&quot;{attr} = '{objname}'&quot;)&#xd;&#xa;    box = clayer.boundingBoxOfSelected()&#xd;&#xa;    canvas = qgis.utils.iface.mapCanvas()&#xd;&#xa;    canvas.zoomToFeatureExtent(box)&#xd;&#xa;" isEnabledOnlyWhenEditable="0" name="Zoom/Pan zum Objekt" capture="0" id="{57207846-4c1a-4e70-9ca5-0601a4202713}" shortTitle="Zoom/Pan zum Objekt">
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="buttonList" sortExpression="" sortOrder="0">
    <columns>
      <column type="actions" width="58" hidden="0"/>
      <column type="field" width="38" name="pk" hidden="0"/>
      <column type="field" width="-1" name="name" hidden="0"/>
      <column type="field" width="-1" name="gruppe" hidden="0"/>
      <column type="field" width="-1" name="warntext" hidden="0"/>
      <column type="field" width="-1" name="warnlevel" hidden="0"/>
      <column type="field" width="-1" name="layername" hidden="0"/>
      <column type="field" width="-1" name="idname" hidden="0"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
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
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="gruppe" editable="1"/>
    <field name="idname" editable="1"/>
    <field name="layername" editable="1"/>
    <field name="name" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="warnlevel" editable="1"/>
    <field name="warntext" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="gruppe"/>
    <field labelOnTop="0" name="idname"/>
    <field labelOnTop="0" name="layername"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="warnlevel"/>
    <field labelOnTop="0" name="warntext"/>
  </labelOnTop>
  <reuseLastValue>
    <field name="gruppe" reuseLastValue="0"/>
    <field name="idname" reuseLastValue="0"/>
    <field name="layername" reuseLastValue="0"/>
    <field name="name" reuseLastValue="0"/>
    <field name="pk" reuseLastValue="0"/>
    <field name="warnlevel" reuseLastValue="0"/>
    <field name="warntext" reuseLastValue="0"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
