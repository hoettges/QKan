<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Labeling|Fields|Forms|Actions|AttributeTable|Rendering" simplifyDrawingHints="0" simplifyMaxScale="1" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" labelsEnabled="0" maxScale="0" minScale="100000000" simplifyAlgorithm="0" simplifyDrawingTol="1" version="3.16.5-Hannover">
  <renderer-v2 forceraster="0" type="singleSymbol" enableorderby="0" symbollevels="0">
    <symbols>
      <symbol name="0" alpha="1" type="marker" clip_to_extent="1" force_rhr="0">
        <layer locked="0" class="SimpleMarker" enabled="1" pass="0">
          <prop v="0" k="angle"/>
          <prop v="255,127,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="schnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="durchm" configurationFlags="None">
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
    <field name="createdat" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option value="true" name="allow_null" type="bool"/>
            <Option value="true" name="calendar_popup" type="bool"/>
            <Option value="dd.MM.yyyy HH:mm" name="display_format" type="QString"/>
            <Option value="dd.MM.yyyy HH:mm" name="field_format" type="QString"/>
            <Option value="false" name="field_iso_format" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="baujahr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="untersuchtag" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option value="true" name="allow_null" type="bool"/>
            <Option value="true" name="calendar_popup" type="bool"/>
            <Option value="dd.MM.yyyy HH:mm" name="display_format" type="QString"/>
            <Option value="dd.MM.yyyy HH:mm" name="field_format" type="QString"/>
            <Option value="false" name="field_iso_format" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="untersucher" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="wetter" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bewertungsart" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bewertungstag" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" name="" index="0"/>
    <alias field="schnam" name="" index="1"/>
    <alias field="durchm" name="" index="2"/>
    <alias field="kommentar" name="" index="3"/>
    <alias field="createdat" name="" index="4"/>
    <alias field="baujahr" name="" index="5"/>
    <alias field="untersuchtag" name="" index="6"/>
    <alias field="untersucher" name="" index="7"/>
    <alias field="wetter" name="" index="8"/>
    <alias field="bewertungsart" name="" index="9"/>
    <alias field="bewertungstag" name="" index="10"/>
  </aliases>
  <defaults>
    <default field="pk" expression="" applyOnUpdate="0"/>
    <default field="schnam" expression="" applyOnUpdate="0"/>
    <default field="durchm" expression="" applyOnUpdate="0"/>
    <default field="kommentar" expression="" applyOnUpdate="0"/>
    <default field="createdat" expression="" applyOnUpdate="0"/>
    <default field="baujahr" expression="" applyOnUpdate="0"/>
    <default field="untersuchtag" expression="" applyOnUpdate="0"/>
    <default field="untersucher" expression="" applyOnUpdate="0"/>
    <default field="wetter" expression="" applyOnUpdate="0"/>
    <default field="bewertungsart" expression="" applyOnUpdate="0"/>
    <default field="bewertungstag" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" notnull_strength="1" exp_strength="0" unique_strength="1"/>
    <constraint constraints="0" field="schnam" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="durchm" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="kommentar" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="createdat" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="baujahr" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="untersuchtag" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="untersucher" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="wetter" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="bewertungsart" notnull_strength="0" exp_strength="0" unique_strength="0"/>
    <constraint constraints="0" field="bewertungstag" notnull_strength="0" exp_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" desc="" exp=""/>
    <constraint field="schnam" desc="" exp=""/>
    <constraint field="durchm" desc="" exp=""/>
    <constraint field="kommentar" desc="" exp=""/>
    <constraint field="createdat" desc="" exp=""/>
    <constraint field="baujahr" desc="" exp=""/>
    <constraint field="untersuchtag" desc="" exp=""/>
    <constraint field="untersucher" desc="" exp=""/>
    <constraint field="wetter" desc="" exp=""/>
    <constraint field="bewertungsart" desc="" exp=""/>
    <constraint field="bewertungstag" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column width="-1" name="pk" type="field" hidden="0"/>
      <column width="-1" name="schnam" type="field" hidden="0"/>
      <column width="-1" name="durchm" type="field" hidden="0"/>
      <column width="-1" name="kommentar" type="field" hidden="0"/>
      <column width="-1" name="createdat" type="field" hidden="0"/>
      <column width="-1" name="untersuchtag" type="field" hidden="0"/>
      <column width="-1" name="untersucher" type="field" hidden="0"/>
      <column width="-1" name="wetter" type="field" hidden="0"/>
      <column width="-1" name="bewertungsart" type="field" hidden="0"/>
      <column width="-1" name="bewertungstag" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" name="baujahr" type="field" hidden="0"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">../AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/schaechte_untersucht.ui</editform>
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
    <field name="baujahr" editable="1"/>
    <field name="bewertungsart" editable="1"/>
    <field name="bewertungstag" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="durchm" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="schnam" editable="1"/>
    <field name="untersucher" editable="1"/>
    <field name="untersuchtag" editable="1"/>
    <field name="wetter" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="baujahr"/>
    <field labelOnTop="0" name="bewertungsart"/>
    <field labelOnTop="0" name="bewertungstag"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="durchm"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="schnam"/>
    <field labelOnTop="0" name="untersucher"/>
    <field labelOnTop="0" name="untersuchtag"/>
    <field labelOnTop="0" name="wetter"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>0</layerGeometryType>
</qgis>
