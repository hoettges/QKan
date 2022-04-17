<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" simplifyAlgorithm="0" labelsEnabled="0" version="3.22.4-Białowieża" minScale="100000000" symbologyReferenceScale="-1" maxScale="0" simplifyDrawingHints="0" readOnly="0" simplifyMaxScale="1" simplifyLocal="1" styleCategories="AllStyleCategories">
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
  <renderer-v2 referencescale="-1" symbollevels="0" enableorderby="0" type="singleSymbol" forceraster="0">
    <symbols>
      <symbol alpha="1" name="0" clip_to_extent="1" type="marker" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" class="SimpleMarker" locked="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="angle" type="QString"/>
            <Option value="square" name="cap_style" type="QString"/>
            <Option value="255,127,0,255" name="color" type="QString"/>
            <Option value="1" name="horizontal_anchor_point" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="circle" name="name" type="QString"/>
            <Option value="0,0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="35,35,35,255" name="outline_color" type="QString"/>
            <Option value="solid" name="outline_style" type="QString"/>
            <Option value="0" name="outline_width" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option value="diameter" name="scale_method" type="QString"/>
            <Option value="2" name="size" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
            <Option value="MM" name="size_unit" type="QString"/>
            <Option value="1" name="vertical_anchor_point" type="QString"/>
          </Option>
          <prop v="0" k="angle"/>
          <prop v="square" k="cap_style"/>
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
  <customproperties>
    <Option type="Map">
      <Option name="dualview/previewExpressions" type="List">
        <Option value="&quot;schnam&quot;" type="QString"/>
      </Option>
      <Option value="0" name="embeddedWidgets/count" type="QString"/>
      <Option name="variableNames" type="invalid"/>
      <Option name="variableValues" type="invalid"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
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
            <Option value="dd.MM.yyyy HH:mm:ss" name="display_format" type="QString"/>
            <Option value="YYYY-MM-dd HH:mm:ss" name="field_format" type="QString"/>
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
            <Option value="dd.MM.yyyy HH:mm:ss" name="display_format" type="QString"/>
            <Option value="YYYY-MM-dd HH:mm:ss" name="field_format" type="QString"/>
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
    <alias field="schnam" name="Name" index="1"/>
    <alias field="durchm" name="Durchmesser" index="2"/>
    <alias field="kommentar" name="Kommentar" index="3"/>
    <alias field="createdat" name="bearbeitet" index="4"/>
    <alias field="baujahr" name="Baujahr" index="5"/>
    <alias field="untersuchtag" name="Untersuchungstag" index="6"/>
    <alias field="untersucher" name="durchgeführt von" index="7"/>
    <alias field="wetter" name="Wetter" index="8"/>
    <alias field="bewertungsart" name="Bewertungsart" index="9"/>
    <alias field="bewertungstag" name="Bewertungstag" index="10"/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="schnam" applyOnUpdate="0" expression=""/>
    <default field="durchm" applyOnUpdate="0" expression=""/>
    <default field="kommentar" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=""/>
    <default field="baujahr" applyOnUpdate="0" expression=""/>
    <default field="untersuchtag" applyOnUpdate="0" expression=""/>
    <default field="untersucher" applyOnUpdate="0" expression=""/>
    <default field="wetter" applyOnUpdate="0" expression=""/>
    <default field="bewertungsart" applyOnUpdate="0" expression=""/>
    <default field="bewertungstag" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint field="schnam" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="durchm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="kommentar" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="createdat" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="baujahr" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="untersuchtag" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="untersucher" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="wetter" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="bewertungsart" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="bewertungstag" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="schnam" exp="" desc=""/>
    <constraint field="durchm" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
    <constraint field="baujahr" exp="" desc=""/>
    <constraint field="untersuchtag" exp="" desc=""/>
    <constraint field="untersucher" exp="" desc=""/>
    <constraint field="wetter" exp="" desc=""/>
    <constraint field="bewertungsart" exp="" desc=""/>
    <constraint field="bewertungstag" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
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
      <column name="baujahr" type="field" hidden="0" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\schaechte_untersucht.ui</editform>
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
    <field name="baujahr" labelOnTop="0"/>
    <field name="bewertungsart" labelOnTop="0"/>
    <field name="bewertungstag" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="durchm" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="schnam" labelOnTop="0"/>
    <field name="untersucher" labelOnTop="0"/>
    <field name="untersuchtag" labelOnTop="0"/>
    <field name="wetter" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue/>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression></previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
