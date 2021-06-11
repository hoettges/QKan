<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="1e+08" hasScaleBasedVisibilityFlag="0" maxScale="0" version="3.18.3-Zürich" styleCategories="Symbology|Labeling|Fields|Forms|MapTips|AttributeTable|Rendering">
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="apnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="anfangsabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="endabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzungsverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="muldenverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzung_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mulden_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
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
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="bknam" name="Key"/>
            <Option type="QString" value="bodenklassen20170516122309914" name="Layer"/>
            <Option type="QString" value="Bodenklassen" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/QKan/test/work/itwh.sqlite' table=&quot;bodenklassen&quot;" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="false" name="UseCompleter"/>
            <Option type="QString" value="bknam" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flaechentyp" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="bezeichnung" name="Key"/>
            <Option type="QString" value="flaechentypen_ca71f66a_50bb_41cb_86df_8046fae64926" name="Layer"/>
            <Option type="QString" value="flaechentypen" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/QKan/test/work/itwh.sqlite' table=&quot;flaechentypen&quot;" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="false" name="UseCompleter"/>
            <Option type="QString" value="bezeichnung" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
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
    <alias field="pk" index="0" name=""/>
    <alias field="apnam" index="1" name=""/>
    <alias field="anfangsabflussbeiwert" index="2" name=""/>
    <alias field="endabflussbeiwert" index="3" name=""/>
    <alias field="benetzungsverlust" index="4" name=""/>
    <alias field="muldenverlust" index="5" name=""/>
    <alias field="benetzung_startwert" index="6" name=""/>
    <alias field="mulden_startwert" index="7" name=""/>
    <alias field="rauheit_kst" index="8" name=""/>
    <alias field="pctZero" index="9" name=""/>
    <alias field="bodenklasse" index="10" name=""/>
    <alias field="flaechentyp" index="11" name=""/>
    <alias field="kommentar" index="12" name=""/>
    <alias field="createdat" index="13" name=""/>
  </aliases>
  <defaults>
    <default field="pk" expression="" applyOnUpdate="0"/>
    <default field="apnam" expression="''" applyOnUpdate="0"/>
    <default field="anfangsabflussbeiwert" expression="" applyOnUpdate="0"/>
    <default field="endabflussbeiwert" expression="" applyOnUpdate="0"/>
    <default field="benetzungsverlust" expression="" applyOnUpdate="0"/>
    <default field="muldenverlust" expression="" applyOnUpdate="0"/>
    <default field="benetzung_startwert" expression="" applyOnUpdate="0"/>
    <default field="mulden_startwert" expression="" applyOnUpdate="0"/>
    <default field="rauheit_kst" expression="" applyOnUpdate="0"/>
    <default field="pctZero" expression="" applyOnUpdate="0"/>
    <default field="bodenklasse" expression="" applyOnUpdate="0"/>
    <default field="flaechentyp" expression="" applyOnUpdate="0"/>
    <default field="kommentar" expression="" applyOnUpdate="0"/>
    <default field="createdat" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" field="pk" unique_strength="1" notnull_strength="1" constraints="3"/>
    <constraint exp_strength="0" field="apnam" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="anfangsabflussbeiwert" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="endabflussbeiwert" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="benetzungsverlust" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="muldenverlust" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="benetzung_startwert" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="mulden_startwert" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="rauheit_kst" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="pctZero" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="bodenklasse" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="flaechentyp" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="kommentar" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" field="createdat" unique_strength="0" notnull_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="apnam" exp="" desc=""/>
    <constraint field="anfangsabflussbeiwert" exp="" desc=""/>
    <constraint field="endabflussbeiwert" exp="" desc=""/>
    <constraint field="benetzungsverlust" exp="" desc=""/>
    <constraint field="muldenverlust" exp="" desc=""/>
    <constraint field="benetzung_startwert" exp="" desc=""/>
    <constraint field="mulden_startwert" exp="" desc=""/>
    <constraint field="rauheit_kst" exp="" desc=""/>
    <constraint field="pctZero" exp="" desc=""/>
    <constraint field="bodenklasse" exp="" desc=""/>
    <constraint field="flaechentyp" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="">
    <columns>
      <column type="field" hidden="0" name="pk" width="-1"/>
      <column type="field" hidden="0" name="apnam" width="-1"/>
      <column type="field" hidden="0" name="anfangsabflussbeiwert" width="-1"/>
      <column type="field" hidden="0" name="endabflussbeiwert" width="-1"/>
      <column type="field" hidden="0" name="benetzungsverlust" width="-1"/>
      <column type="field" hidden="0" name="muldenverlust" width="-1"/>
      <column type="field" hidden="0" name="benetzung_startwert" width="-1"/>
      <column type="field" hidden="0" name="mulden_startwert" width="-1"/>
      <column type="field" hidden="0" name="bodenklasse" width="-1"/>
      <column type="field" hidden="0" name="kommentar" width="-1"/>
      <column type="field" hidden="0" name="createdat" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column type="field" hidden="0" name="rauheit_kst" width="-1"/>
      <column type="field" hidden="0" name="pctZero" width="-1"/>
      <column type="field" hidden="0" name="flaechentyp" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_abflussparameter.ui</editform>
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
  <dataDefinedFieldProperties/>
  <widgets/>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
