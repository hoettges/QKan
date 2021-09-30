<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" minScale="1e+08" maxScale="0" readOnly="0" version="3.20.1-Odense" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal accumulate="0" endExpression="" endField="" startField="" startExpression="" enabled="0" mode="0" durationField="" durationUnit="min" fixedDuration="0">
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
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
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
    <field configurationFlags="None" name="idname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="name" name=""/>
    <alias index="2" field="gruppe" name=""/>
    <alias index="3" field="warntext" name=""/>
    <alias index="4" field="warnlevel" name=""/>
    <alias index="5" field="sql" name=""/>
    <alias index="6" field="layername" name=""/>
    <alias index="7" field="idname" name=""/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="name" expression=""/>
    <default applyOnUpdate="0" field="gruppe" expression=""/>
    <default applyOnUpdate="0" field="warntext" expression=""/>
    <default applyOnUpdate="0" field="warnlevel" expression=""/>
    <default applyOnUpdate="0" field="sql" expression=""/>
    <default applyOnUpdate="0" field="layername" expression=""/>
    <default applyOnUpdate="0" field="idname" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint constraints="0" field="name" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="gruppe" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="warntext" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="warnlevel" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="sql" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="layername" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="idname" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="name"/>
    <constraint exp="" desc="" field="gruppe"/>
    <constraint exp="" desc="" field="warntext"/>
    <constraint exp="" desc="" field="warnlevel"/>
    <constraint exp="" desc="" field="sql"/>
    <constraint exp="" desc="" field="layername"/>
    <constraint exp="" desc="" field="idname"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column hidden="0" type="field" name="pk" width="-1"/>
      <column hidden="0" type="field" name="name" width="-1"/>
      <column hidden="0" type="field" name="gruppe" width="-1"/>
      <column hidden="0" type="field" name="warntext" width="-1"/>
      <column hidden="0" type="field" name="warnlevel" width="-1"/>
      <column hidden="0" type="field" name="sql" width="-1"/>
      <column hidden="0" type="field" name="layername" width="-1"/>
      <column hidden="0" type="field" name="idname" width="-1"/>
      <column hidden="1" type="actions" width="-1"/>
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
    <field editable="1" name="gruppe"/>
    <field editable="1" name="idname"/>
    <field editable="1" name="layername"/>
    <field editable="1" name="name"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="sql"/>
    <field editable="1" name="warnlevel"/>
    <field editable="1" name="warntext"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="gruppe"/>
    <field labelOnTop="0" name="idname"/>
    <field labelOnTop="0" name="layername"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="sql"/>
    <field labelOnTop="0" name="warnlevel"/>
    <field labelOnTop="0" name="warntext"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="gruppe"/>
    <field reuseLastValue="0" name="idname"/>
    <field reuseLastValue="0" name="layername"/>
    <field reuseLastValue="0" name="name"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="sql"/>
    <field reuseLastValue="0" name="warnlevel"/>
    <field reuseLastValue="0" name="warntext"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
