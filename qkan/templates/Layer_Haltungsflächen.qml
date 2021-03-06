<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingHints="1" simplifyLocal="1" version="3.6.3-Noosa" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|GeometryOptions" hasScaleBasedVisibilityFlag="0" simplifyMaxScale="1" maxScale="0" simplifyAlgorithm="0" labelsEnabled="0" simplifyDrawingTol="1" readOnly="0" minScale="1e+08">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" symbollevels="0" enableorderby="0" type="singleSymbol">
    <symbols>
      <symbol alpha="1" name="0" clip_to_extent="1" force_rhr="0" type="fill">
        <layer class="SimpleFill" enabled="1" locked="0" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="116,161,198,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="221,219,80,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.8" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
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
    <field name="flnam">
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
    <field name="neigkl">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenschreiber">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
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
    <field name="abflussparameter">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option value="0" name="AllowMulti" type="QString"/>
            <Option value="0" name="AllowNull" type="QString"/>
            <Option value="" name="FilterExpression" type="QString"/>
            <Option value="apnam" name="Key" type="QString"/>
            <Option value="abflussparameter20161218110231636" name="Layer" type="QString"/>
            <Option value="0" name="OrderByValue" type="QString"/>
            <Option value="1" name="UseCompleter" type="QString"/>
            <Option value="apnam" name="Value" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option value="1" name="allow_null" type="QString"/>
            <Option value="1" name="calendar_popup" type="QString"/>
            <Option value="dd.MM.yyyy HH:mm" name="display_format" type="QString"/>
            <Option value="dd.MM.yyyy HH:mm" name="field_format" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" name="" index="0"/>
    <alias field="flnam" name="" index="1"/>
    <alias field="haltnam" name="" index="2"/>
    <alias field="neigkl" name="" index="3"/>
    <alias field="regenschreiber" name="" index="4"/>
    <alias field="teilgebiet" name="" index="5"/>
    <alias field="abflussparameter" name="" index="6"/>
    <alias field="kommentar" name="" index="7"/>
    <alias field="createdat" name="" index="8"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="flnam" applyOnUpdate="0"/>
    <default expression="" field="haltnam" applyOnUpdate="0"/>
    <default expression="" field="neigkl" applyOnUpdate="0"/>
    <default expression="" field="regenschreiber" applyOnUpdate="0"/>
    <default expression="" field="teilgebiet" applyOnUpdate="0"/>
    <default expression="" field="abflussparameter" applyOnUpdate="0"/>
    <default expression="" field="kommentar" applyOnUpdate="0"/>
    <default expression="now()" field="createdat" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="1" exp_strength="0" field="pk" constraints="3" unique_strength="1"/>
    <constraint notnull_strength="0" exp_strength="0" field="flnam" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="haltnam" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="neigkl" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="regenschreiber" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="teilgebiet" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="abflussparameter" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="kommentar" constraints="0" unique_strength="0"/>
    <constraint notnull_strength="0" exp_strength="0" field="createdat" constraints="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" desc="" exp=""/>
    <constraint field="flnam" desc="" exp=""/>
    <constraint field="haltnam" desc="" exp=""/>
    <constraint field="neigkl" desc="" exp=""/>
    <constraint field="regenschreiber" desc="" exp=""/>
    <constraint field="teilgebiet" desc="" exp=""/>
    <constraint field="abflussparameter" desc="" exp=""/>
    <constraint field="kommentar" desc="" exp=""/>
    <constraint field="createdat" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="">
    <columns>
      <column width="-1" name="pk" type="field" hidden="0"/>
      <column width="-1" name="flnam" type="field" hidden="0"/>
      <column width="-1" name="haltnam" type="field" hidden="0"/>
      <column width="-1" name="neigkl" type="field" hidden="0"/>
      <column width="-1" name="regenschreiber" type="field" hidden="0"/>
      <column width="-1" name="teilgebiet" type="field" hidden="0"/>
      <column width="-1" name="abflussparameter" type="field" hidden="0"/>
      <column width="-1" name="kommentar" type="field" hidden="0"/>
      <column width="-1" name="createdat" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1">C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/QKan/qkan/forms/qkan_tezg.ui</editform>
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
    <field editable="1" name="abflussparameter"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="flnam"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="neigkl"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="regenschreiber"/>
    <field editable="1" name="teilgebiet"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abflussparameter"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="flnam"/>
    <field labelOnTop="0" name="haltnam"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="neigkl"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="regenschreiber"/>
    <field labelOnTop="0" name="teilgebiet"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>COALESCE( "pk", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
