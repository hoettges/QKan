<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" maxScale="0" styleCategories="AllStyleCategories" version="3.20.1-Odense" minScale="1e+08" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal endField="" endExpression="" mode="0" startExpression="" durationUnit="min" enabled="0" fixedDuration="0" durationField="" accumulate="0" startField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option value="&quot;name&quot;" type="QString"/>
      </Option>
      <Option value="0" type="int" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="gruppe" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="warntext" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="warntyp" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="warnlevel" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="sql" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="layername" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="attrname" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="gruppe" name=""/>
    <alias index="2" field="warntext" name=""/>
    <alias index="3" field="warntyp" name=""/>
    <alias index="4" field="warnlevel" name=""/>
    <alias index="5" field="sql" name=""/>
    <alias index="6" field="layername" name=""/>
    <alias index="7" field="attrname" name=""/>
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
    <constraint notnull_strength="1" unique_strength="1" exp_strength="0" field="pk" constraints="3"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="gruppe" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="warntext" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="warntyp" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="warnlevel" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="sql" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="layername" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="attrname" constraints="0"/>
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
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" hidden="0" name="pk" width="-1"/>
      <column type="field" hidden="0" name="gruppe" width="-1"/>
      <column type="field" hidden="0" name="warntext" width="-1"/>
      <column type="field" hidden="0" name="warnlevel" width="-1"/>
      <column type="field" hidden="0" name="sql" width="-1"/>
      <column type="field" hidden="0" name="layername" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" hidden="0" name="warntyp" width="-1"/>
      <column type="field" hidden="0" name="attrname" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\</editform>
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
    <field name="attrname" reuseLastValue="0"/>
    <field name="gruppe" reuseLastValue="0"/>
    <field name="idname" reuseLastValue="0"/>
    <field name="layername" reuseLastValue="0"/>
    <field name="name" reuseLastValue="0"/>
    <field name="pk" reuseLastValue="0"/>
    <field name="sql" reuseLastValue="0"/>
    <field name="warnlevel" reuseLastValue="0"/>
    <field name="warntext" reuseLastValue="0"/>
    <field name="warntyp" reuseLastValue="0"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
