<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.16-Białowieża" styleCategories="Fields|Forms|AttributeTable">
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="apnam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="anfangsabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="endabflussbeiwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzungsverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="muldenverlust" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="benetzung_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mulden_startwert" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
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
            <Option name="AllowMulti" value="false" type="QString"/>
            <Option name="AllowNull" value="false" type="QString"/>
            <Option name="FilterExpression" value="" type="QString"/>
            <Option name="Key" value="bknam" type="QString"/>
            <Option name="Layer" value="bodenklassen20170516122309914" type="QString"/>
            <Option name="NofColumns" value="1" type="QString"/>
            <Option name="OrderByValue" value="false" type="QString"/>
            <Option name="UseCompleter" value="false" type="QString"/>
            <Option name="Value" value="bknam" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flaechentyp" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" value="false" type="bool"/>
            <Option name="AllowNull" value="false" type="bool"/>
            <Option name="Description" value="" type="QString"/>
            <Option name="FilterExpression" value="" type="QString"/>
            <Option name="Key" value="bezeichnung" type="QString"/>
            <Option name="Layer" value="flaechentypen_ca71f66a_50bb_41cb_86df_8046fae64926" type="QString"/>
            <Option name="LayerName" value="Flächentypen" type="QString"/>
            <Option name="LayerProviderName" value="spatialite" type="QString"/>
            <Option name="LayerSource" value="dbname='muster.sqlite' table=&quot;flaechentypen&quot;" type="QString"/>
            <Option name="NofColumns" value="1" type="int"/>
            <Option name="OrderByValue" value="false" type="bool"/>
            <Option name="UseCompleter" value="false" type="bool"/>
            <Option name="Value" value="bezeichnung" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
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
    <alias name="" field="pk" index="0"/>
    <alias name="Name" field="apnam" index="1"/>
    <alias name="Anfangsabflussbeiwert" field="anfangsabflussbeiwert" index="2"/>
    <alias name="Endabflussbeiwert" field="endabflussbeiwert" index="3"/>
    <alias name="Benetzungsverlust" field="benetzungsverlust" index="4"/>
    <alias name="Muldenverlust" field="muldenverlust" index="5"/>
    <alias name="Benetzung Startwert" field="benetzung_startwert" index="6"/>
    <alias name="Mulden Startwert" field="mulden_startwert" index="7"/>
    <alias name="Rauheitsbeiwert" field="rauheit_kst" index="8"/>
    <alias name="" field="pctZero" index="9"/>
    <alias name="Bodenklasse" field="bodenklasse" index="10"/>
    <alias name="Flächentyp" field="flaechentyp" index="11"/>
    <alias name="Kommentar" field="kommentar" index="12"/>
    <alias name="bearbeitet" field="createdat" index="13"/>
  </aliases>
  <defaults>
    <default field="pk" expression="" applyOnUpdate="0"/>
    <default field="apnam" expression="" applyOnUpdate="0"/>
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
    <default field="createdat" expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" unique_strength="2" field="pk" exp_strength="0" notnull_strength="2"/>
    <constraint constraints="0" unique_strength="0" field="apnam" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="anfangsabflussbeiwert" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="endabflussbeiwert" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="benetzungsverlust" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="muldenverlust" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="benetzung_startwert" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="mulden_startwert" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="rauheit_kst" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="pctZero" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="bodenklasse" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="flaechentyp" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="kommentar" exp_strength="0" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="createdat" exp_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="pk" exp=""/>
    <constraint desc="" field="apnam" exp=""/>
    <constraint desc="" field="anfangsabflussbeiwert" exp=""/>
    <constraint desc="" field="endabflussbeiwert" exp=""/>
    <constraint desc="" field="benetzungsverlust" exp=""/>
    <constraint desc="" field="muldenverlust" exp=""/>
    <constraint desc="" field="benetzung_startwert" exp=""/>
    <constraint desc="" field="mulden_startwert" exp=""/>
    <constraint desc="" field="rauheit_kst" exp=""/>
    <constraint desc="" field="pctZero" exp=""/>
    <constraint desc="" field="bodenklasse" exp=""/>
    <constraint desc="" field="flaechentyp" exp=""/>
    <constraint desc="" field="kommentar" exp=""/>
    <constraint desc="" field="createdat" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column name="pk" width="-1" type="field" hidden="0"/>
      <column name="apnam" width="-1" type="field" hidden="0"/>
      <column name="anfangsabflussbeiwert" width="-1" type="field" hidden="1"/>
      <column name="endabflussbeiwert" width="-1" type="field" hidden="0"/>
      <column name="benetzungsverlust" width="-1" type="field" hidden="1"/>
      <column name="muldenverlust" width="-1" type="field" hidden="1"/>
      <column name="benetzung_startwert" width="-1" type="field" hidden="1"/>
      <column name="mulden_startwert" width="-1" type="field" hidden="1"/>
      <column name="rauheit_kst" width="-1" type="field" hidden="1"/>
      <column name="pctZero" width="-1" type="field" hidden="1"/>
      <column name="bodenklasse" width="-1" type="field" hidden="0"/>
      <column name="flaechentyp" width="-1" type="field" hidden="1"/>
      <column name="kommentar" width="-1" type="field" hidden="0"/>
      <column name="createdat" width="-1" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_kp_abflussparameter.ui</editform>
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
  <layerGeometryType>4</layerGeometryType>
</qgis>
