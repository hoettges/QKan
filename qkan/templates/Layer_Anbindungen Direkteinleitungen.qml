<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" maxScale="0" minScale="100000000" simplifyDrawingHints="1" version="3.18.3-Zürich" simplifyAlgorithm="0" simplifyDrawingTol="1" simplifyLocal="1" simplifyMaxScale="1" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|MapTips|AttributeTable|Rendering" hasScaleBasedVisibilityFlag="0" labelsEnabled="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0">
    <symbols>
      <symbol clip_to_extent="1" type="line" name="0" alpha="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" pass="0" locked="0" enabled="1">
          <Option type="Map">
            <Option type="QString" name="align_dash_pattern" value="0"/>
            <Option type="QString" name="capstyle" value="square"/>
            <Option type="QString" name="customdash" value="5;2"/>
            <Option type="QString" name="customdash_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="customdash_unit" value="MM"/>
            <Option type="QString" name="dash_pattern_offset" value="0"/>
            <Option type="QString" name="dash_pattern_offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="dash_pattern_offset_unit" value="MM"/>
            <Option type="QString" name="draw_inside_polygon" value="0"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="line_color" value="151,153,223,255"/>
            <Option type="QString" name="line_style" value="solid"/>
            <Option type="QString" name="line_width" value="0.26"/>
            <Option type="QString" name="line_width_unit" value="MM"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="ring_filter" value="0"/>
            <Option type="QString" name="tweak_dash_pattern_on_corners" value="0"/>
            <Option type="QString" name="use_custom_dash" value="0"/>
            <Option type="QString" name="width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
          </Option>
          <prop v="0" k="align_dash_pattern"/>
          <prop v="square" k="capstyle"/>
          <prop v="5;2" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
          <prop v="0" k="dash_pattern_offset"/>
          <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
          <prop v="MM" k="dash_pattern_offset_unit"/>
          <prop v="0" k="draw_inside_polygon"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="151,153,223,255" k="line_color"/>
          <prop v="solid" k="line_style"/>
          <prop v="0.26" k="line_width"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="tweak_dash_pattern_on_corners"/>
          <prop v="0" k="use_custom_dash"/>
          <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
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
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="elnam" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="1"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="elnam"/>
            <Option type="QString" name="Layer" value="einleit20171004110830029"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="elnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltnam" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="1"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="haltnam"/>
            <Option type="QString" name="Layer" value="haltungen20161016203756230"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="haltnam"/>
          </Option>
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
    <field name="teilgebiet" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="1"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="tgnam"/>
            <Option type="QString" name="Layer" value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="tgnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="geom" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="gbuf" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="elnam" name=""/>
    <alias index="2" field="haltnam" name=""/>
    <alias index="3" field="schnam" name=""/>
    <alias index="4" field="teilgebiet" name=""/>
    <alias index="5" field="geom" name=""/>
    <alias index="6" field="gbuf" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="elnam" applyOnUpdate="0" expression="''"/>
    <default field="haltnam" applyOnUpdate="0" expression=""/>
    <default field="schnam" applyOnUpdate="0" expression=""/>
    <default field="teilgebiet" applyOnUpdate="0" expression=""/>
    <default field="geom" applyOnUpdate="0" expression=""/>
    <default field="gbuf" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint field="elnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="haltnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="schnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="teilgebiet" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="geom" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="gbuf" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="elnam" desc=""/>
    <constraint exp="" field="haltnam" desc=""/>
    <constraint exp="" field="schnam" desc=""/>
    <constraint exp="" field="teilgebiet" desc=""/>
    <constraint exp="" field="geom" desc=""/>
    <constraint exp="" field="gbuf" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="elnam"/>
      <column width="-1" type="field" hidden="0" name="haltnam"/>
      <column width="-1" type="field" hidden="0" name="teilgebiet"/>
      <column width="-1" type="field" hidden="0" name="geom"/>
      <column width="-1" type="field" hidden="0" name="gbuf"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" type="field" hidden="0" name="schnam"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_anbindungeinleit.ui</editform>
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
    <field name="elnam" editable="1"/>
    <field name="gbuf" editable="1"/>
    <field name="geom" editable="1"/>
    <field name="haltnam" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="schnam" editable="1"/>
    <field name="teilgebiet" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="elnam" labelOnTop="0"/>
    <field name="gbuf" labelOnTop="0"/>
    <field name="geom" labelOnTop="0"/>
    <field name="haltnam" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="schnam" labelOnTop="0"/>
    <field name="teilgebiet" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression> "elnam" || ' - ' ||  "haltnam" </previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
