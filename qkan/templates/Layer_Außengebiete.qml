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
            <Option type="QString" name="color" value="225,89,137,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="225,89,137,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
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
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="gebnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="false"/>
            <Option type="QString" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schnam" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="false"/>
            <Option type="QString" name="AllowNull" value="false"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="schnam"/>
            <Option type="QString" name="Layer" value="schaechte20161220162259105"/>
            <Option type="QString" name="NofColumns" value="1"/>
            <Option type="QString" name="OrderByValue" value="false"/>
            <Option type="QString" name="UseCompleter" value="false"/>
            <Option type="QString" name="Value" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="hoeheob" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="hoeheun" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fliessweg" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="false"/>
            <Option type="QString" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="basisabfluss" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="cn" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="false"/>
            <Option type="QString" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenschreiber" configurationFlags="None">
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
            <Option type="QString" name="AllowMulti" value="false"/>
            <Option type="QString" name="AllowNull" value="false"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="tgnam"/>
            <Option type="QString" name="Layer" value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0"/>
            <Option type="QString" name="NofColumns" value="1"/>
            <Option type="QString" name="OrderByValue" value="false"/>
            <Option type="QString" name="UseCompleter" value="false"/>
            <Option type="QString" name="Value" value="tgnam"/>
          </Option>
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
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="gebnam" name=""/>
    <alias index="2" field="schnam" name=""/>
    <alias index="3" field="hoeheob" name=""/>
    <alias index="4" field="hoeheun" name=""/>
    <alias index="5" field="fliessweg" name=""/>
    <alias index="6" field="basisabfluss" name=""/>
    <alias index="7" field="cn" name=""/>
    <alias index="8" field="regenschreiber" name=""/>
    <alias index="9" field="teilgebiet" name=""/>
    <alias index="10" field="kommentar" name=""/>
    <alias index="11" field="createdat" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="gebnam" applyOnUpdate="0" expression="''"/>
    <default field="schnam" applyOnUpdate="0" expression=""/>
    <default field="hoeheob" applyOnUpdate="0" expression=""/>
    <default field="hoeheun" applyOnUpdate="0" expression=""/>
    <default field="fliessweg" applyOnUpdate="0" expression=""/>
    <default field="basisabfluss" applyOnUpdate="0" expression=""/>
    <default field="cn" applyOnUpdate="0" expression=""/>
    <default field="regenschreiber" applyOnUpdate="0" expression=""/>
    <default field="teilgebiet" applyOnUpdate="0" expression=""/>
    <default field="kommentar" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint field="gebnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="schnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="hoeheob" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="hoeheun" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="fliessweg" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="basisabfluss" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="cn" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="regenschreiber" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="teilgebiet" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="kommentar" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="createdat" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="gebnam" desc=""/>
    <constraint exp="" field="schnam" desc=""/>
    <constraint exp="" field="hoeheob" desc=""/>
    <constraint exp="" field="hoeheun" desc=""/>
    <constraint exp="" field="fliessweg" desc=""/>
    <constraint exp="" field="basisabfluss" desc=""/>
    <constraint exp="" field="cn" desc=""/>
    <constraint exp="" field="regenschreiber" desc=""/>
    <constraint exp="" field="teilgebiet" desc=""/>
    <constraint exp="" field="kommentar" desc=""/>
    <constraint exp="" field="createdat" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="gebnam"/>
      <column width="-1" type="field" hidden="0" name="schnam"/>
      <column width="-1" type="field" hidden="0" name="hoeheob"/>
      <column width="-1" type="field" hidden="0" name="hoeheun"/>
      <column width="-1" type="field" hidden="0" name="fliessweg"/>
      <column width="-1" type="field" hidden="0" name="basisabfluss"/>
      <column width="-1" type="field" hidden="0" name="cn"/>
      <column width="-1" type="field" hidden="0" name="regenschreiber"/>
      <column width="-1" type="field" hidden="0" name="teilgebiet"/>
      <column width="-1" type="field" hidden="0" name="kommentar"/>
      <column width="-1" type="field" hidden="0" name="createdat"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">../../Users/hoettges/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/forms</editform>
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
    <field name="basisabfluss" editable="1"/>
    <field name="cn" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="fliessweg" editable="1"/>
    <field name="gebnam" editable="1"/>
    <field name="hoeheob" editable="1"/>
    <field name="hoeheun" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="regenschreiber" editable="1"/>
    <field name="schnam" editable="1"/>
    <field name="teilgebiet" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="basisabfluss" labelOnTop="0"/>
    <field name="cn" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="fliessweg" labelOnTop="0"/>
    <field name="gebnam" labelOnTop="0"/>
    <field name="hoeheob" labelOnTop="0"/>
    <field name="hoeheun" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="regenschreiber" labelOnTop="0"/>
    <field name="schnam" labelOnTop="0"/>
    <field name="teilgebiet" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>COALESCE( "gebnam", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
