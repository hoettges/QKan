<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" maxScale="0" styleCategories="AllStyleCategories" version="3.20.1-Odense" minScale="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal endField="" endExpression="" mode="0" startExpression="" durationUnit="min" enabled="0" fixedDuration="0" durationField="" accumulate="0" startField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="pk" type="QString" name="dualview/previewExpressions"/>
      <Option value="0" type="QString" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="apnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="anfangsabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="endabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzungsverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="muldenverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzung_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mulden_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
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
            <Option value="false" type="QString" name="AllowMulti"/>
            <Option value="false" type="QString" name="AllowNull"/>
            <Option value="" type="QString" name="FilterExpression"/>
            <Option value="bknam" type="QString" name="Key"/>
            <Option value="bodenklassen20170516122309914" type="QString" name="Layer"/>
            <Option value="1" type="QString" name="NofColumns"/>
            <Option value="false" type="QString" name="OrderByValue"/>
            <Option value="false" type="QString" name="UseCompleter"/>
            <Option value="bknam" type="QString" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flaechentyp" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option value="false" type="QString" name="AllowMulti"/>
            <Option value="false" type="QString" name="AllowNull"/>
            <Option value="" type="QString" name="FilterExpression"/>
            <Option value="bezeichnung" type="QString" name="Key"/>
            <Option value="flaechentypen_ca71f66a_50bb_41cb_86df_8046fae64926" type="QString" name="Layer"/>
            <Option value="1" type="QString" name="NofColumns"/>
            <Option value="false" type="QString" name="OrderByValue"/>
            <Option value="false" type="QString" name="UseCompleter"/>
            <Option value="bezeichnung" type="QString" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
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
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="apnam" expression=""/>
    <default applyOnUpdate="0" field="anfangsabflussbeiwert" expression=""/>
    <default applyOnUpdate="0" field="endabflussbeiwert" expression=""/>
    <default applyOnUpdate="0" field="benetzungsverlust" expression=""/>
    <default applyOnUpdate="0" field="muldenverlust" expression=""/>
    <default applyOnUpdate="0" field="benetzung_startwert" expression=""/>
    <default applyOnUpdate="0" field="mulden_startwert" expression=""/>
    <default applyOnUpdate="0" field="rauheit_kst" expression=""/>
    <default applyOnUpdate="0" field="pctZero" expression=""/>
    <default applyOnUpdate="0" field="bodenklasse" expression=""/>
    <default applyOnUpdate="0" field="flaechentyp" expression=""/>
    <default applyOnUpdate="0" field="kommentar" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression=""/>
  </defaults>
  <constraints>
    <constraint notnull_strength="1" unique_strength="1" exp_strength="0" field="pk" constraints="3"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="apnam" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="anfangsabflussbeiwert" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="endabflussbeiwert" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="benetzungsverlust" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="muldenverlust" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="benetzung_startwert" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="mulden_startwert" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="rauheit_kst" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="pctZero" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="bodenklasse" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="flaechentyp" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="kommentar" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="createdat" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="apnam"/>
    <constraint exp="" desc="" field="anfangsabflussbeiwert"/>
    <constraint exp="" desc="" field="endabflussbeiwert"/>
    <constraint exp="" desc="" field="benetzungsverlust"/>
    <constraint exp="" desc="" field="muldenverlust"/>
    <constraint exp="" desc="" field="benetzung_startwert"/>
    <constraint exp="" desc="" field="mulden_startwert"/>
    <constraint exp="" desc="" field="rauheit_kst"/>
    <constraint exp="" desc="" field="pctZero"/>
    <constraint exp="" desc="" field="bodenklasse"/>
    <constraint exp="" desc="" field="flaechentyp"/>
    <constraint exp="" desc="" field="kommentar"/>
    <constraint exp="" desc="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" hidden="0" name="pk" width="-1"/>
      <column type="field" hidden="0" name="apnam" width="-1"/>
      <column type="field" hidden="0" name="anfangsabflussbeiwert" width="-1"/>
      <column type="field" hidden="0" name="endabflussbeiwert" width="-1"/>
      <column type="field" hidden="0" name="benetzungsverlust" width="-1"/>
      <column type="field" hidden="0" name="muldenverlust" width="-1"/>
      <column type="field" hidden="0" name="benetzung_startwert" width="-1"/>
      <column type="field" hidden="0" name="mulden_startwert" width="-1"/>
      <column type="field" hidden="0" name="rauheit_kst" width="-1"/>
      <column type="field" hidden="0" name="pctZero" width="-1"/>
      <column type="field" hidden="0" name="bodenklasse" width="-1"/>
      <column type="field" hidden="0" name="flaechentyp" width="-1"/>
      <column type="field" hidden="0" name="kommentar" width="-1"/>
      <column type="field" hidden="0" name="createdat" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
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
    <field editable="1" name="anfangsabflussbeiwert"/>
    <field editable="1" name="apnam"/>
    <field editable="1" name="benetzung_startwert"/>
    <field editable="1" name="benetzungsverlust"/>
    <field editable="1" name="bodenklasse"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="endabflussbeiwert"/>
    <field editable="1" name="flaechentyp"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="mulden_startwert"/>
    <field editable="1" name="muldenverlust"/>
    <field editable="1" name="pctZero"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="rauheit_kst"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="anfangsabflussbeiwert"/>
    <field labelOnTop="0" name="apnam"/>
    <field labelOnTop="0" name="benetzung_startwert"/>
    <field labelOnTop="0" name="benetzungsverlust"/>
    <field labelOnTop="0" name="bodenklasse"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="endabflussbeiwert"/>
    <field labelOnTop="0" name="flaechentyp"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="mulden_startwert"/>
    <field labelOnTop="0" name="muldenverlust"/>
    <field labelOnTop="0" name="pctZero"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="rauheit_kst"/>
  </labelOnTop>
  <reuseLastValue>
    <field name="anfangsabflussbeiwert" reuseLastValue="0"/>
    <field name="apnam" reuseLastValue="0"/>
    <field name="benetzung_startwert" reuseLastValue="0"/>
    <field name="benetzungsverlust" reuseLastValue="0"/>
    <field name="bodenklasse" reuseLastValue="0"/>
    <field name="createdat" reuseLastValue="0"/>
    <field name="endabflussbeiwert" reuseLastValue="0"/>
    <field name="flaechentyp" reuseLastValue="0"/>
    <field name="kommentar" reuseLastValue="0"/>
    <field name="mulden_startwert" reuseLastValue="0"/>
    <field name="muldenverlust" reuseLastValue="0"/>
    <field name="pctZero" reuseLastValue="0"/>
    <field name="pk" reuseLastValue="0"/>
    <field name="rauheit_kst" reuseLastValue="0"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"apnam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
