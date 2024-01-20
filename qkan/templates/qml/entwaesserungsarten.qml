<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" readOnly="0" version="3.22.16-Białowieża" minScale="0" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
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
  <fieldConfiguration>
    <field configurationFlags="None" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bezeichnung">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kuerzel">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bemerkung">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="he_nr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kp_nr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="m150">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="isybau">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="transport">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="druckdicht">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" index="0" name=""/>
    <alias field="bezeichnung" index="1" name="Bezeichnung"/>
    <alias field="kuerzel" index="2" name="Kürzel"/>
    <alias field="bemerkung" index="3" name="Bemerkung"/>
    <alias field="he_nr" index="4" name="NR (HYSTEM-EXTRAN)"/>
    <alias field="kp_nr" index="5" name="NR (Kanal++)"/>
    <alias field="m145" index="6" name="Nr (DWA-M 145)"/>
    <alias field="m150" index="7" name="Nr (DWA-M 150)"/>
    <alias field="isybau" index="8" name="Nr (ISYBAU)"/>
    <alias field="transport" index="9" name="Transport"/>
    <alias field="druckdicht" index="10" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="bezeichnung" applyOnUpdate="0" expression=""/>
    <default field="kuerzel" applyOnUpdate="0" expression=""/>
    <default field="bemerkung" applyOnUpdate="0" expression=""/>
    <default field="he_nr" applyOnUpdate="0" expression=""/>
    <default field="kp_nr" applyOnUpdate="0" expression=""/>
    <default field="m145" applyOnUpdate="0" expression=""/>
    <default field="m150" applyOnUpdate="0" expression=""/>
    <default field="isybau" applyOnUpdate="0" expression=""/>
    <default field="transport" applyOnUpdate="0" expression=""/>
    <default field="druckdicht" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" field="pk" notnull_strength="2" unique_strength="2" constraints="3"/>
    <constraint exp_strength="0" field="bezeichnung" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="kuerzel" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="bemerkung" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="he_nr" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="kp_nr" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="m145" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="m150" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="isybau" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="transport" notnull_strength="0" unique_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="druckdicht" notnull_strength="0" unique_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" desc="" exp=""/>
    <constraint field="bezeichnung" desc="" exp=""/>
    <constraint field="kuerzel" desc="" exp=""/>
    <constraint field="bemerkung" desc="" exp=""/>
    <constraint field="he_nr" desc="" exp=""/>
    <constraint field="kp_nr" desc="" exp=""/>
    <constraint field="m145" desc="" exp=""/>
    <constraint field="m150" desc="" exp=""/>
    <constraint field="isybau" desc="" exp=""/>
    <constraint field="transport" desc="" exp=""/>
    <constraint field="druckdicht" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="bezeichnung"/>
      <column width="-1" type="field" hidden="0" name="kuerzel"/>
      <column width="-1" type="field" hidden="0" name="bemerkung"/>
      <column width="-1" type="field" hidden="0" name="he_nr"/>
      <column width="-1" type="field" hidden="0" name="kp_nr"/>
      <column width="-1" type="field" hidden="0" name="m145"/>
      <column width="-1" type="field" hidden="0" name="m150"/>
      <column width="-1" type="field" hidden="0" name="isybau"/>
      <column width="-1" type="field" hidden="0" name="transport"/>
      <column width="-1" type="field" hidden="0" name="druckdicht"/>
      <column width="-1" type="actions" hidden="1"/>
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
    <field editable="1" name="druckdicht"/>
    <field editable="1" name="he_nr"/>
    <field editable="1" name="isybau"/>
    <field editable="1" name="kp_nr"/>
    <field editable="1" name="kuerzel"/>
    <field editable="1" name="m145"/>
    <field editable="1" name="m150"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="transport"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="bemerkung"/>
    <field labelOnTop="0" name="bezeichnung"/>
    <field labelOnTop="0" name="druckdicht"/>
    <field labelOnTop="0" name="he_nr"/>
    <field labelOnTop="0" name="isybau"/>
    <field labelOnTop="0" name="kp_nr"/>
    <field labelOnTop="0" name="kuerzel"/>
    <field labelOnTop="0" name="m145"/>
    <field labelOnTop="0" name="m150"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="transport"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="bemerkung"/>
    <field reuseLastValue="0" name="bezeichnung"/>
    <field reuseLastValue="0" name="druckdicht"/>
    <field reuseLastValue="0" name="he_nr"/>
    <field reuseLastValue="0" name="isybau"/>
    <field reuseLastValue="0" name="kp_nr"/>
    <field reuseLastValue="0" name="kuerzel"/>
    <field reuseLastValue="0" name="m145"/>
    <field reuseLastValue="0" name="m150"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="transport"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"kuerzel"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
