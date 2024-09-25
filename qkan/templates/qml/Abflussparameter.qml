<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" maxScale="0" readOnly="0" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|Temporal|Legend|Notes" minScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal limitMode="0" startField="" endField="" enabled="0" accumulate="0" durationField="" startExpression="" durationUnit="min" endExpression="" mode="0" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;apnam&quot;"/>
      </Option>
      <Option type="int" name="embeddedWidgets/count" value="0"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <legend type="default-vector" showLabelLegend="0"/>
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
            <Option type="bool" name="AllowMulti" value="false"/>
            <Option type="bool" name="AllowNull" value="true"/>
            <Option type="QString" name="Description" value=""/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="bknam"/>
            <Option type="QString" name="Layer" value="bodenklassen20170516122309914"/>
            <Option type="QString" name="LayerName" value="Bodenklassen"/>
            <Option type="QString" name="LayerProviderName" value="spatialite"/>
            <Option type="QString" name="LayerSource" value="dbname='juelich.sqlite' table=&quot;bodenklassen&quot;"/>
            <Option type="int" name="NofColumns" value="1"/>
            <Option type="bool" name="OrderByValue" value="false"/>
            <Option type="bool" name="UseCompleter" value="false"/>
            <Option type="QString" name="Value" value="bknam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flaechentyp" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" name="AllowMulti" value="false"/>
            <Option type="bool" name="AllowNull" value="true"/>
            <Option type="QString" name="Description" value=""/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="bezeichnung"/>
            <Option type="QString" name="Layer" value="flaechentypen_ca71f66a_50bb_41cb_86df_8046fae64926"/>
            <Option type="QString" name="LayerName" value="Flächentypen"/>
            <Option type="QString" name="LayerProviderName" value="spatialite"/>
            <Option type="QString" name="LayerSource" value="dbname='juelich.sqlite' table=&quot;flaechentypen&quot;"/>
            <Option type="int" name="NofColumns" value="1"/>
            <Option type="bool" name="OrderByValue" value="false"/>
            <Option type="bool" name="UseCompleter" value="false"/>
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
    <alias index="1" field="apnam" name="Name"/>
    <alias index="2" field="anfangsabflussbeiwert" name="Anfangsabflussbeiwert"/>
    <alias index="3" field="endabflussbeiwert" name="Endabflussbeiwert"/>
    <alias index="4" field="benetzungsverlust" name="Benetzungsverlust"/>
    <alias index="5" field="muldenverlust" name="Muldenverlust"/>
    <alias index="6" field="benetzung_startwert" name="Benetzung Startwert"/>
    <alias index="7" field="mulden_startwert" name="Mulden Startwert"/>
    <alias index="8" field="rauheit_kst" name="Rauheitsbeiwert"/>
    <alias index="9" field="pctZero" name=""/>
    <alias index="10" field="bodenklasse" name="Bodenklasse"/>
    <alias index="11" field="flaechentyp" name="Flächentyp"/>
    <alias index="12" field="kommentar" name="Kommentar"/>
    <alias index="13" field="createdat" name="bearbeitet"/>
  </aliases>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="apnam" applyOnUpdate="0"/>
    <default expression="" field="anfangsabflussbeiwert" applyOnUpdate="0"/>
    <default expression="" field="endabflussbeiwert" applyOnUpdate="0"/>
    <default expression="" field="benetzungsverlust" applyOnUpdate="0"/>
    <default expression="" field="muldenverlust" applyOnUpdate="0"/>
    <default expression="" field="benetzung_startwert" applyOnUpdate="0"/>
    <default expression="" field="mulden_startwert" applyOnUpdate="0"/>
    <default expression="" field="rauheit_kst" applyOnUpdate="0"/>
    <default expression="" field="pctZero" applyOnUpdate="0"/>
    <default expression="" field="bodenklasse" applyOnUpdate="0"/>
    <default expression="" field="flaechentyp" applyOnUpdate="0"/>
    <default expression="" field="kommentar" applyOnUpdate="0"/>
    <default expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')" field="createdat" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="2" notnull_strength="2" exp_strength="0"/>
    <constraint constraints="0" field="apnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="anfangsabflussbeiwert" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="endabflussbeiwert" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="benetzungsverlust" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="muldenverlust" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="benetzung_startwert" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="mulden_startwert" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="rauheit_kst" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="pctZero" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="bodenklasse" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="flaechentyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="pk"/>
    <constraint desc="" exp="" field="apnam"/>
    <constraint desc="" exp="" field="anfangsabflussbeiwert"/>
    <constraint desc="" exp="" field="endabflussbeiwert"/>
    <constraint desc="" exp="" field="benetzungsverlust"/>
    <constraint desc="" exp="" field="muldenverlust"/>
    <constraint desc="" exp="" field="benetzung_startwert"/>
    <constraint desc="" exp="" field="mulden_startwert"/>
    <constraint desc="" exp="" field="rauheit_kst"/>
    <constraint desc="" exp="" field="pctZero"/>
    <constraint desc="" exp="" field="bodenklasse"/>
    <constraint desc="" exp="" field="flaechentyp"/>
    <constraint desc="" exp="" field="kommentar"/>
    <constraint desc="" exp="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" type="field" hidden="1" name="pk"/>
      <column width="127" type="field" hidden="0" name="apnam"/>
      <column width="-1" type="field" hidden="0" name="anfangsabflussbeiwert"/>
      <column width="-1" type="field" hidden="0" name="endabflussbeiwert"/>
      <column width="-1" type="field" hidden="0" name="benetzungsverlust"/>
      <column width="-1" type="field" hidden="0" name="muldenverlust"/>
      <column width="-1" type="field" hidden="0" name="benetzung_startwert"/>
      <column width="-1" type="field" hidden="0" name="mulden_startwert"/>
      <column width="-1" type="field" hidden="1" name="rauheit_kst"/>
      <column width="-1" type="field" hidden="1" name="pctZero"/>
      <column width="-1" type="field" hidden="0" name="bodenklasse"/>
      <column width="-1" type="field" hidden="0" name="flaechentyp"/>
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
  <editform tolerant="1">C:\Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_abflussparameter.ui</editform>
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
  <reuseLastValue>
    <field reuseLastValue="0" name="anfangsabflussbeiwert"/>
    <field reuseLastValue="0" name="apnam"/>
    <field reuseLastValue="0" name="benetzung_startwert"/>
    <field reuseLastValue="0" name="benetzungsverlust"/>
    <field reuseLastValue="0" name="bodenklasse"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="endabflussbeiwert"/>
    <field reuseLastValue="0" name="flaechentyp"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="mulden_startwert"/>
    <field reuseLastValue="0" name="muldenverlust"/>
    <field reuseLastValue="0" name="pctZero"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="rauheit_kst"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"apnam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
