<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" hasScaleBasedVisibilityFlag="0" labelsEnabled="0" simplifyMaxScale="1" simplifyAlgorithm="0" simplifyLocal="1" styleCategories="Symbology|Labeling|Fields|Forms|Actions|AttributeTable|Rendering" simplifyDrawingHints="0" version="3.16.5-Hannover" maxScale="0" minScale="100000000">
  <renderer-v2 symbollevels="0" forceraster="0" enableorderby="0" type="singleSymbol">
    <symbols>
      <symbol clip_to_extent="1" name="0" alpha="1" force_rhr="0" type="marker">
        <layer enabled="1" class="SimpleMarker" pass="0" locked="0">
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
    <field configurationFlags="None" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="schnam">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="durchm">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="createdat">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="untersuchtag">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="untersucher">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="wetter">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bewertungsart">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bewertungstag">
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
    <alias field="untersuchtag" name="" index="5"/>
    <alias field="untersucher" name="" index="6"/>
    <alias field="wetter" name="" index="7"/>
    <alias field="bewertungsart" name="" index="8"/>
    <alias field="bewertungstag" name="" index="9"/>
  </aliases>
  <defaults>
    <default field="pk" expression="" applyOnUpdate="0"/>
    <default field="schnam" expression="" applyOnUpdate="0"/>
    <default field="durchm" expression="" applyOnUpdate="0"/>
    <default field="kommentar" expression="" applyOnUpdate="0"/>
    <default field="createdat" expression="" applyOnUpdate="0"/>
    <default field="untersuchtag" expression="" applyOnUpdate="0"/>
    <default field="untersucher" expression="" applyOnUpdate="0"/>
    <default field="wetter" expression="" applyOnUpdate="0"/>
    <default field="bewertungsart" expression="" applyOnUpdate="0"/>
    <default field="bewertungstag" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint field="schnam" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="durchm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="kommentar" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="createdat" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="untersuchtag" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="untersucher" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="wetter" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="bewertungsart" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="bewertungstag" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" desc="" exp=""/>
    <constraint field="schnam" desc="" exp=""/>
    <constraint field="durchm" desc="" exp=""/>
    <constraint field="kommentar" desc="" exp=""/>
    <constraint field="createdat" desc="" exp=""/>
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
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="">
    <columns>
      <column name="pk" type="field" hidden="0" width="-1"/>
      <column name="schnam" type="field" hidden="0" width="-1"/>
      <column name="durchm" type="field" hidden="0" width="-1"/>
      <column name="kommentar" type="field" hidden="0" width="-1"/>
      <column name="createdat" type="field" hidden="0" width="-1"/>
      <column name="untersuchtag" type="field" hidden="0" width="-1"/>
      <column name="untersucher" type="field" hidden="0" width="-1"/>
      <column name="wetter" type="field" hidden="0" width="-1"/>
      <column name="bewertungsart" type="field" hidden="0" width="-1"/>
      <column name="bewertungstag" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/Nora/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/schaechte_untersucht.ui</editform>
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
    <field editable="1" name="bewertungsart"/>
    <field editable="1" name="bewertungstag"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="durchm"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="schnam"/>
    <field editable="1" name="untersucher"/>
    <field editable="1" name="untersuchtag"/>
    <field editable="1" name="wetter"/>
  </editable>
  <labelOnTop>
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
