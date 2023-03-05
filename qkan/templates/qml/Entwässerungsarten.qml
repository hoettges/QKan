<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" maxScale="0" minScale="0" styleCategories="AllStyleCategories" version="3.22.16-Białowieża" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal limitMode="0" enabled="0" accumulate="0" endField="" startField="" startExpression="" durationUnit="min" fixedDuration="0" mode="0" durationField="" endExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option value="&quot;kuerzel&quot;" type="QString"/>
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
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bezeichnung">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kuerzel">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bemerkung">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="he_nr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kp_nr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="bezeichnung" name="Bezeichnung"/>
    <alias index="2" field="kuerzel" name="Kürzel"/>
    <alias index="3" field="bemerkung" name="Bemerkung"/>
    <alias index="4" field="he_nr" name="NR (HYSTEM-EXTRAN)"/>
    <alias index="5" field="kp_nr" name="NR (Kanal++)"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="bezeichnung" expression=""/>
    <default applyOnUpdate="0" field="kuerzel" expression=""/>
    <default applyOnUpdate="0" field="bemerkung" expression=""/>
    <default applyOnUpdate="0" field="he_nr" expression=""/>
    <default applyOnUpdate="0" field="kp_nr" expression=""/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" constraints="3" field="pk" notnull_strength="2" unique_strength="2"/>
    <constraint exp_strength="0" constraints="0" field="bezeichnung" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" constraints="0" field="kuerzel" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" constraints="0" field="bemerkung" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" constraints="0" field="he_nr" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" constraints="0" field="kp_nr" notnull_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="bezeichnung"/>
    <constraint exp="" desc="" field="kuerzel"/>
    <constraint exp="" desc="" field="bemerkung"/>
    <constraint exp="" desc="" field="he_nr"/>
    <constraint exp="" desc="" field="kp_nr"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="pk" hidden="0"/>
      <column type="field" width="-1" name="bezeichnung" hidden="0"/>
      <column type="field" width="-1" name="kuerzel" hidden="0"/>
      <column type="field" width="-1" name="bemerkung" hidden="0"/>
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
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_entwaesserungsarten.ui</editform>
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
    <field editable="1" name="bemerkung"/>
    <field editable="1" name="bezeichnung"/>
    <field editable="1" name="he_nr"/>
    <field editable="1" name="kp_nr"/>
    <field editable="1" name="kuerzel"/>
    <field editable="1" name="pk"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="bemerkung"/>
    <field labelOnTop="0" name="bezeichnung"/>
    <field labelOnTop="0" name="he_nr"/>
    <field labelOnTop="0" name="kp_nr"/>
    <field labelOnTop="0" name="kuerzel"/>
    <field labelOnTop="0" name="pk"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="bemerkung"/>
    <field reuseLastValue="0" name="bezeichnung"/>
    <field reuseLastValue="0" name="he_nr"/>
    <field reuseLastValue="0" name="kp_nr"/>
    <field reuseLastValue="0" name="kuerzel"/>
    <field reuseLastValue="0" name="pk"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"kuerzel"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
