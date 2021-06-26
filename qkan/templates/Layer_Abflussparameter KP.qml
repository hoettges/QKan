<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" maxScale="0" minScale="1e+08" version="3.18.3-Zürich" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|MapTips|AttributeTable|Rendering" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
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
    <field name="apnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="anfangsabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="endabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzungsverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="muldenverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzung_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mulden_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="rauheit_kst" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="pctZero" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bodenklasse" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="false"/>
            <Option type="QString" name="AllowNull" value="false"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="bknam"/>
            <Option type="QString" name="Layer" value="bodenklassen20170516122309914"/>
            <Option type="QString" name="NofColumns" value="1"/>
            <Option type="QString" name="OrderByValue" value="false"/>
            <Option type="QString" name="UseCompleter" value="false"/>
            <Option type="QString" name="Value" value="bknam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flaechentyp" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="false"/>
            <Option type="QString" name="AllowNull" value="false"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="bezeichnung"/>
            <Option type="QString" name="Layer" value="flaechentypen_ca71f66a_50bb_41cb_86df_8046fae64926"/>
            <Option type="QString" name="NofColumns" value="1"/>
            <Option type="QString" name="OrderByValue" value="false"/>
            <Option type="QString" name="UseCompleter" value="false"/>
            <Option type="QString" name="Value" value="bezeichnung"/>
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
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="apnam" name=""/>
    <alias index="2" field="anfangsabflussbeiwert" name=""/>
    <alias index="3" field="endabflussbeiwert" name=""/>
    <alias index="4" field="benetzungsverlust" name=""/>
    <alias index="5" field="muldenverlust" name=""/>
    <alias index="6" field="benetzung_startwert" name=""/>
    <alias index="7" field="mulden_startwert" name=""/>
    <alias index="8" field="rauheit_kst" name=""/>
    <alias index="9" field="pctZero" name=""/>
    <alias index="10" field="bodenklasse" name=""/>
    <alias index="11" field="flaechentyp" name=""/>
    <alias index="12" field="kommentar" name=""/>
    <alias index="13" field="createdat" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="apnam" applyOnUpdate="0" expression="''"/>
    <default field="anfangsabflussbeiwert" applyOnUpdate="0" expression=""/>
    <default field="endabflussbeiwert" applyOnUpdate="0" expression=""/>
    <default field="benetzungsverlust" applyOnUpdate="0" expression=""/>
    <default field="muldenverlust" applyOnUpdate="0" expression=""/>
    <default field="benetzung_startwert" applyOnUpdate="0" expression=""/>
    <default field="mulden_startwert" applyOnUpdate="0" expression=""/>
    <default field="rauheit_kst" applyOnUpdate="0" expression=""/>
    <default field="pctZero" applyOnUpdate="0" expression=""/>
    <default field="bodenklasse" applyOnUpdate="0" expression=""/>
    <default field="flaechentyp" applyOnUpdate="0" expression=""/>
    <default field="kommentar" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint field="apnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="anfangsabflussbeiwert" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="endabflussbeiwert" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="benetzungsverlust" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="muldenverlust" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="benetzung_startwert" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="mulden_startwert" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="rauheit_kst" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="pctZero" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="bodenklasse" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="flaechentyp" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="kommentar" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="createdat" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="apnam" desc=""/>
    <constraint exp="" field="anfangsabflussbeiwert" desc=""/>
    <constraint exp="" field="endabflussbeiwert" desc=""/>
    <constraint exp="" field="benetzungsverlust" desc=""/>
    <constraint exp="" field="muldenverlust" desc=""/>
    <constraint exp="" field="benetzung_startwert" desc=""/>
    <constraint exp="" field="mulden_startwert" desc=""/>
    <constraint exp="" field="rauheit_kst" desc=""/>
    <constraint exp="" field="pctZero" desc=""/>
    <constraint exp="" field="bodenklasse" desc=""/>
    <constraint exp="" field="flaechentyp" desc=""/>
    <constraint exp="" field="kommentar" desc=""/>
    <constraint exp="" field="createdat" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="apnam"/>
      <column width="-1" type="field" hidden="0" name="anfangsabflussbeiwert"/>
      <column width="-1" type="field" hidden="0" name="endabflussbeiwert"/>
      <column width="-1" type="field" hidden="0" name="benetzungsverlust"/>
      <column width="-1" type="field" hidden="0" name="muldenverlust"/>
      <column width="-1" type="field" hidden="0" name="benetzung_startwert"/>
      <column width="-1" type="field" hidden="0" name="mulden_startwert"/>
      <column width="-1" type="field" hidden="0" name="bodenklasse"/>
      <column width="-1" type="field" hidden="0" name="kommentar"/>
      <column width="-1" type="field" hidden="0" name="createdat"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" type="field" hidden="0" name="rauheit_kst"/>
      <column width="-1" type="field" hidden="0" name="pctZero"/>
      <column width="-1" type="field" hidden="0" name="flaechentyp"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/hoettges/Documents/qkan/forms/qkan_kp_abflussparameter.ui</editform>
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
    <field name="anfangsabflussbeiwert" editable="1"/>
    <field name="apnam" editable="1"/>
    <field name="benetzung_startwert" editable="1"/>
    <field name="benetzungsverlust" editable="1"/>
    <field name="bodenklasse" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="endabflussbeiwert" editable="1"/>
    <field name="flaechentyp" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="mulden_startwert" editable="1"/>
    <field name="muldenverlust" editable="1"/>
    <field name="pctZero" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="rauheit_kst" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="anfangsabflussbeiwert" labelOnTop="0"/>
    <field name="apnam" labelOnTop="0"/>
    <field name="benetzung_startwert" labelOnTop="0"/>
    <field name="benetzungsverlust" labelOnTop="0"/>
    <field name="bodenklasse" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="endabflussbeiwert" labelOnTop="0"/>
    <field name="flaechentyp" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="mulden_startwert" labelOnTop="0"/>
    <field name="muldenverlust" labelOnTop="0"/>
    <field name="pctZero" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="rauheit_kst" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>COALESCE( "apnam", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
