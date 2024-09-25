<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" maxScale="0" readOnly="0" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|Temporal|Legend|Notes" minScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal limitMode="0" startField="" endField="" enabled="0" accumulate="0" durationField="" startExpression="" durationUnit="min" endExpression="" mode="0" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;profilnam&quot;"/>
      </Option>
      <Option type="int" name="embeddedWidgets/count" value="0"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <legend type="default-vector" showLabelLegend="0"/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="profilnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kuerzel" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="he_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mu_nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kp_key" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="isybau" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="m150" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="m145" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="profilnam" name="Profilbezeichnung"/>
    <alias index="2" field="kuerzel" name=""/>
    <alias index="3" field="he_nr" name="NR (HYSTEM-EXTRAN)"/>
    <alias index="4" field="mu_nr" name="NR (Mike Urban)"/>
    <alias index="5" field="kp_key" name="Key (Kanal++)"/>
    <alias index="6" field="isybau" name=""/>
    <alias index="7" field="m150" name=""/>
    <alias index="8" field="m145" name=""/>
    <alias index="9" field="kommentar" name=""/>
  </aliases>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="profilnam" applyOnUpdate="0"/>
    <default expression="" field="kuerzel" applyOnUpdate="0"/>
    <default expression="" field="he_nr" applyOnUpdate="0"/>
    <default expression="" field="mu_nr" applyOnUpdate="0"/>
    <default expression="" field="kp_key" applyOnUpdate="0"/>
    <default expression="" field="isybau" applyOnUpdate="0"/>
    <default expression="" field="m150" applyOnUpdate="0"/>
    <default expression="" field="m145" applyOnUpdate="0"/>
    <default expression="" field="kommentar" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="2" notnull_strength="2" exp_strength="0"/>
    <constraint constraints="0" field="profilnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kuerzel" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="he_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="mu_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kp_key" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="isybau" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="m150" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="m145" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="pk"/>
    <constraint desc="" exp="" field="profilnam"/>
    <constraint desc="" exp="" field="kuerzel"/>
    <constraint desc="" exp="" field="he_nr"/>
    <constraint desc="" exp="" field="mu_nr"/>
    <constraint desc="" exp="" field="kp_key"/>
    <constraint desc="" exp="" field="isybau"/>
    <constraint desc="" exp="" field="m150"/>
    <constraint desc="" exp="" field="m145"/>
    <constraint desc="" exp="" field="kommentar"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="profilnam"/>
      <column width="-1" type="field" hidden="0" name="he_nr"/>
      <column width="-1" type="field" hidden="0" name="mu_nr"/>
      <column width="-1" type="field" hidden="0" name="kp_key"/>
      <column width="-1" type="field" hidden="0" name="kuerzel"/>
      <column width="-1" type="field" hidden="0" name="isybau"/>
      <column width="-1" type="field" hidden="0" name="m150"/>
      <column width="-1" type="field" hidden="0" name="m145"/>
      <column width="-1" type="field" hidden="0" name="kommentar"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_profile.ui</editform>
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
    <field editable="1" name="he_nr"/>
    <field editable="1" name="isybau"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="kp_key"/>
    <field editable="1" name="kuerzel"/>
    <field editable="1" name="m145"/>
    <field editable="1" name="m150"/>
    <field editable="1" name="mu_nr"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="profilnam"/>
  </editable>
  <labelOnTop>
    <field name="he_nr" labelOnTop="0"/>
    <field name="isybau" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="kp_key" labelOnTop="0"/>
    <field name="kuerzel" labelOnTop="0"/>
    <field name="m145" labelOnTop="0"/>
    <field name="m150" labelOnTop="0"/>
    <field name="mu_nr" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="profilnam" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="he_nr"/>
    <field reuseLastValue="0" name="isybau"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="kp_key"/>
    <field reuseLastValue="0" name="kuerzel"/>
    <field reuseLastValue="0" name="m145"/>
    <field reuseLastValue="0" name="m150"/>
    <field reuseLastValue="0" name="mu_nr"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="profilnam"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"profilnam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
