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
    <field configurationFlags="None" name="sql">
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
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="gruppe" name="Gruppe"/>
    <alias index="2" field="warntext" name="Warntext"/>
    <alias index="3" field="warntyp" name="Warntyp"/>
    <alias index="4" field="warnlevel" name="Warnlevel"/>
    <alias index="5" field="sql" name=""/>
    <alias index="6" field="layername" name="Layername"/>
    <alias index="7" field="attrname" name="Attributname"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="gruppe" expression=""/>
    <default applyOnUpdate="0" field="warntext" expression=""/>
    <default applyOnUpdate="0" field="warntyp" expression=""/>
    <default applyOnUpdate="0" field="warnlevel" expression=""/>
    <default applyOnUpdate="0" field="sql" expression=""/>
    <default applyOnUpdate="0" field="layername" expression=""/>
    <default applyOnUpdate="0" field="attrname" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" exp_strength="0" unique_strength="1" field="pk" notnull_strength="1"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="gruppe" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="warntext" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="warntyp" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="warnlevel" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="sql" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="layername" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="attrname" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="gruppe"/>
    <constraint exp="" desc="" field="warntext"/>
    <constraint exp="" desc="" field="warntyp"/>
    <constraint exp="" desc="" field="warnlevel"/>
    <constraint exp="" desc="" field="sql"/>
    <constraint exp="" desc="" field="layername"/>
    <constraint exp="" desc="" field="attrname"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="pk" hidden="0"/>
      <column type="field" width="-1" name="gruppe" hidden="0"/>
      <column type="field" width="-1" name="warntext" hidden="0"/>
      <column type="field" width="-1" name="warnlevel" hidden="0"/>
      <column type="field" width="-1" name="sql" hidden="0"/>
      <column type="field" width="-1" name="layername" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
      <column type="field" width="-1" name="warntyp" hidden="0"/>
      <column type="field" width="-1" name="attrname" hidden="0"/>
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
    <field editable="1" name="gruppe"/>
    <field editable="1" name="idname"/>
    <field editable="1" name="layername"/>
    <field editable="1" name="name"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="sql"/>
    <field editable="1" name="warnlevel"/>
    <field editable="1" name="warntext"/>
    <field editable="1" name="warntyp"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="attrname"/>
    <field labelOnTop="0" name="gruppe"/>
    <field labelOnTop="0" name="idname"/>
    <field labelOnTop="0" name="layername"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="sql"/>
    <field labelOnTop="0" name="warnlevel"/>
    <field labelOnTop="0" name="warntext"/>
    <field labelOnTop="0" name="warntyp"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="attrname"/>
    <field reuseLastValue="0" name="gruppe"/>
    <field reuseLastValue="0" name="idname"/>
    <field reuseLastValue="0" name="layername"/>
    <field reuseLastValue="0" name="name"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="sql"/>
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
