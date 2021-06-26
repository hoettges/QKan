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
      <symbol clip_to_extent="1" type="fill" name="0" alpha="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleFill" pass="0" locked="0" enabled="1">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="116,161,198,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="221,219,80,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.8"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
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
    <field name="flnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
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
    <field name="neigkl" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="neigung" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="befgrad" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="schwerpunktlaufzeit" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="regenschreiber" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
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
    <field name="abflussparameter" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="1"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="apnam"/>
            <Option type="QString" name="Layer" value="Abflussparameter_KP_e16f4a36_8f43_4398_a67c_53cbd2e8d3e9"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="apnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="QString" name="allow_null" value="1"/>
            <Option type="QString" name="calendar_popup" value="1"/>
            <Option type="QString" name="display_format" value="yyyy.MM.dd HH:mm:ss"/>
            <Option type="QString" name="field_format" value="YYYY.MM.dd HH:mm:ss"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="flnam" name=""/>
    <alias index="2" field="haltnam" name=""/>
    <alias index="3" field="schnam" name=""/>
    <alias index="4" field="neigkl" name=""/>
    <alias index="5" field="neigung" name=""/>
    <alias index="6" field="befgrad" name=""/>
    <alias index="7" field="schwerpunktlaufzeit" name=""/>
    <alias index="8" field="regenschreiber" name=""/>
    <alias index="9" field="teilgebiet" name=""/>
    <alias index="10" field="abflussparameter" name=""/>
    <alias index="11" field="kommentar" name=""/>
    <alias index="12" field="createdat" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="flnam" applyOnUpdate="0" expression="''"/>
    <default field="haltnam" applyOnUpdate="0" expression=""/>
    <default field="schnam" applyOnUpdate="0" expression=""/>
    <default field="neigkl" applyOnUpdate="0" expression=""/>
    <default field="neigung" applyOnUpdate="0" expression=""/>
    <default field="befgrad" applyOnUpdate="0" expression=""/>
    <default field="schwerpunktlaufzeit" applyOnUpdate="0" expression=""/>
    <default field="regenschreiber" applyOnUpdate="0" expression=""/>
    <default field="teilgebiet" applyOnUpdate="0" expression=""/>
    <default field="abflussparameter" applyOnUpdate="0" expression=""/>
    <default field="kommentar" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=" format_date( now(), 'yyyy.MM.dd HH:mm:ss')"/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint field="flnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="haltnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="schnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="neigkl" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="neigung" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="befgrad" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="schwerpunktlaufzeit" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="regenschreiber" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="teilgebiet" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="abflussparameter" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="kommentar" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="createdat" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="flnam" desc=""/>
    <constraint exp="" field="haltnam" desc=""/>
    <constraint exp="" field="schnam" desc=""/>
    <constraint exp="" field="neigkl" desc=""/>
    <constraint exp="" field="neigung" desc=""/>
    <constraint exp="" field="befgrad" desc=""/>
    <constraint exp="" field="schwerpunktlaufzeit" desc=""/>
    <constraint exp="" field="regenschreiber" desc=""/>
    <constraint exp="" field="teilgebiet" desc=""/>
    <constraint exp="" field="abflussparameter" desc=""/>
    <constraint exp="" field="kommentar" desc=""/>
    <constraint exp="" field="createdat" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="&quot;regenschreiber&quot;" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="flnam"/>
      <column width="-1" type="field" hidden="0" name="haltnam"/>
      <column width="-1" type="field" hidden="0" name="neigkl"/>
      <column width="-1" type="field" hidden="0" name="regenschreiber"/>
      <column width="-1" type="field" hidden="0" name="teilgebiet"/>
      <column width="-1" type="field" hidden="0" name="abflussparameter"/>
      <column width="-1" type="field" hidden="0" name="kommentar"/>
      <column width="-1" type="field" hidden="0" name="createdat"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" type="field" hidden="0" name="schnam"/>
      <column width="-1" type="field" hidden="0" name="neigung"/>
      <column width="-1" type="field" hidden="0" name="befgrad"/>
      <column width="-1" type="field" hidden="0" name="schwerpunktlaufzeit"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_tezg.ui</editform>
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
    <field name="abflussparameter" editable="1"/>
    <field name="befgrad" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="flnam" editable="1"/>
    <field name="haltnam" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="neigkl" editable="1"/>
    <field name="neigung" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="regenschreiber" editable="1"/>
    <field name="schnam" editable="1"/>
    <field name="schwerpunktlaufzeit" editable="1"/>
    <field name="teilgebiet" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="abflussparameter" labelOnTop="0"/>
    <field name="befgrad" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="flnam" labelOnTop="0"/>
    <field name="haltnam" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="neigkl" labelOnTop="0"/>
    <field name="neigung" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="regenschreiber" labelOnTop="0"/>
    <field name="schnam" labelOnTop="0"/>
    <field name="schwerpunktlaufzeit" labelOnTop="0"/>
    <field name="teilgebiet" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>COALESCE( "pk", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
