<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" minScale="0" maxScale="0" readOnly="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal durationField="" enabled="0" startField="" fixedDuration="0" startExpression="" endExpression="" mode="0" accumulate="0" durationUnit="min" limitMode="0" endField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="0" name="embeddedWidgets/count" type="QString"/>
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
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="profilnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="he_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mu_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kp_key" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" name="" index="0"/>
    <alias field="profilnam" name="Profilbezeichnung" index="1"/>
    <alias field="he_nr" name="NR (HYSTEM-EXTRAN)" index="2"/>
    <alias field="mu_nr" name="NR (Mike Urban)" index="3"/>
    <alias field="kp_key" name="Key (Kanal++)" index="4"/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="profilnam" applyOnUpdate="0" expression=""/>
    <default field="he_nr" applyOnUpdate="0" expression=""/>
    <default field="mu_nr" applyOnUpdate="0" expression=""/>
    <default field="kp_key" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint field="profilnam" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="he_nr" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="mu_nr" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="kp_key" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="profilnam" exp="" desc=""/>
    <constraint field="he_nr" exp="" desc=""/>
    <constraint field="mu_nr" exp="" desc=""/>
    <constraint field="kp_key" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column name="pk" type="field" hidden="0" width="-1"/>
      <column name="profilnam" type="field" hidden="0" width="-1"/>
      <column name="he_nr" type="field" hidden="0" width="-1"/>
      <column name="mu_nr" type="field" hidden="0" width="-1"/>
      <column name="kp_key" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_profile.ui</editform>
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
    <field name="he_nr" editable="1"/>
    <field name="kp_key" editable="1"/>
    <field name="mu_nr" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="profilnam" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="he_nr" labelOnTop="0"/>
    <field name="kp_key" labelOnTop="0"/>
    <field name="mu_nr" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="profilnam" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field name="he_nr" reuseLastValue="0"/>
    <field name="kp_key" reuseLastValue="0"/>
    <field name="mu_nr" reuseLastValue="0"/>
    <field name="pk" reuseLastValue="0"/>
    <field name="profilnam" reuseLastValue="0"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"profilnam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
