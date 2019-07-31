<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingHints="1" simplifyLocal="1" version="3.6.3-Noosa" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|GeometryOptions" hasScaleBasedVisibilityFlag="0" simplifyMaxScale="1" maxScale="0" simplifyAlgorithm="0" labelsEnabled="0" simplifyDrawingTol="1" readOnly="0" minScale="1e+08">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" symbollevels="0" enableorderby="0" type="singleSymbol">
    <symbols>
      <symbol alpha="1" name="0" clip_to_extent="1" force_rhr="0" type="line">
        <layer class="SimpleLine" enabled="1" locked="0" pass="0">
          <prop v="square" k="capstyle"/>
          <prop v="5;2" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
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
          <prop v="0" k="use_custom_dash"/>
          <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
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
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="elnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option value="0" name="AllowMulti" type="QString"/>
            <Option value="0" name="AllowNull" type="QString"/>
            <Option value="" name="FilterExpression" type="QString"/>
            <Option value="haltnam" name="Key" type="QString"/>
            <Option value="haltungen20161016203756230" name="Layer" type="QString"/>
            <Option value="0" name="OrderByValue" type="QString"/>
            <Option value="1" name="UseCompleter" type="QString"/>
            <Option value="haltnam" name="Value" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="teilgebiet">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option value="0" name="AllowMulti" type="QString"/>
            <Option value="0" name="AllowNull" type="QString"/>
            <Option value="" name="FilterExpression" type="QString"/>
            <Option value="tgnam" name="Key" type="QString"/>
            <Option value="teilgebiete20170214092005309" name="Layer" type="QString"/>
            <Option value="0" name="OrderByValue" type="QString"/>
            <Option value="1" name="UseCompleter" type="QString"/>
            <Option value="tgnam" name="Value" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="geom">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="gbuf">
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
    <alias field="elnam" name="" index="1"/>
    <alias field="haltnam" name="" index="2"/>
    <alias field="teilgebiet" name="" index="3"/>
    <alias field="geom" name="" index="4"/>
    <alias field="gbuf" name="" index="5"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="elnam" applyOnUpdate="0"/>
    <default expression="" field="haltnam" applyOnUpdate="0"/>
    <default expression="" field="teilgebiet" applyOnUpdate="0"/>
    <default expression="" field="geom" applyOnUpdate="0"/>
    <default expression="" field="gbuf" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="1" exp_strength="0" field="pk" constraints="3" unique_strength="1"/>
    <constraint notnull_strength="0" exp_strength="0" field="elnam" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="haltnam" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="teilgebiet" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="geom" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="gbuf" constraints="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" desc="" exp=""/>
    <constraint field="elnam" desc="" exp=""/>
    <constraint field="haltnam" desc="" exp=""/>
    <constraint field="teilgebiet" desc="" exp=""/>
    <constraint field="geom" desc="" exp=""/>
    <constraint field="gbuf" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="">
    <columns>
      <column width="-1" name="pk" type="field" hidden="0"/>
      <column width="-1" name="elnam" type="field" hidden="0"/>
      <column width="-1" name="haltnam" type="field" hidden="0"/>
      <column width="-1" name="teilgebiet" type="field" hidden="0"/>
      <column width="-1" name="geom" type="field" hidden="0"/>
      <column width="-1" name="gbuf" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1">C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/QKan/qkan/forms/qkan_anbindungeinleit.ui</editform>
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
    <field editable="1" name="elnam"/>
    <field editable="1" name="gbuf"/>
    <field editable="1" name="geom"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="teilgebiet"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="elnam"/>
    <field labelOnTop="0" name="gbuf"/>
    <field labelOnTop="0" name="geom"/>
    <field labelOnTop="0" name="haltnam"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="teilgebiet"/>
  </labelOnTop>
  <widgets/>
  <previewExpression> "elnam" || ' - ' ||  "haltnam" </previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
