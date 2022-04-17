<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="0" version="3.22.4-Białowieża" readOnly="0" styleCategories="AllStyleCategories">
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
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="abflusstyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="he_nr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kp_nr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="abflusstyp" name="Name"/>
    <alias index="2" field="he_nr" name="NR (HYSTEM-EXTRAN)"/>
    <alias index="3" field="kp_nr" name="NR (Kanal++)"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="abflusstyp" expression=""/>
    <default applyOnUpdate="0" field="he_nr" expression=""/>
    <default applyOnUpdate="0" field="kp_nr" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" exp_strength="0" unique_strength="1" field="pk" notnull_strength="1"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="abflusstyp" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="he_nr" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="kp_nr" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="abflusstyp"/>
    <constraint exp="" desc="" field="he_nr"/>
    <constraint exp="" desc="" field="kp_nr"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="pk" hidden="0"/>
      <column type="field" width="-1" name="abflusstyp" hidden="0"/>
      <column type="field" width="-1" name="he_nr" hidden="0"/>
      <column type="field" width="-1" name="kp_nr" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
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
    <field editable="1" name="abflusstyp"/>
    <field editable="1" name="he_nr"/>
    <field editable="1" name="kp_nr"/>
    <field editable="1" name="pk"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abflusstyp"/>
    <field labelOnTop="0" name="he_nr"/>
    <field labelOnTop="0" name="kp_nr"/>
    <field labelOnTop="0" name="pk"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="abflusstyp"/>
    <field reuseLastValue="0" name="he_nr"/>
    <field reuseLastValue="0" name="kp_nr"/>
    <field reuseLastValue="0" name="pk"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"abflusstyp"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
