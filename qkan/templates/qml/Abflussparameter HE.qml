<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="0" version="3.22.4-Białowieża" readOnly="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal endField="" durationUnit="min" accumulate="0" startField="" limitMode="0" startExpression="" fixedDuration="0" mode="0" endExpression="" enabled="0" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;apnam&quot;"/>
        <Option type="QString" value="COALESCE( &quot;apnam&quot;, '&lt;NULL>' )"/>
        <Option type="QString" value="COALESCE( &quot;apnam&quot;, '&lt;NULL>' )"/>
        <Option type="QString" value="COALESCE( &quot;apnam&quot;, '&lt;NULL>' )"/>
        <Option type="QString" value="COALESCE( &quot;apnam&quot;, '&lt;NULL>' )"/>
        <Option type="QString" value="COALESCE( &quot;apnam&quot;, '&lt;NULL>' )"/>
      </Option>
      <Option type="QString" value="0" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector" showLabelLegend="0"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="apnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="anfangsabflussbeiwert">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="endabflussbeiwert">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="benetzungsverlust">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="muldenverlust">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="benetzung_startwert">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="mulden_startwert">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="rauheit_kst">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="pctZero">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bodenklasse">
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
    <field configurationFlags="None" name="flaechentyp">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="bezeichnung" name="Key"/>
            <Option type="QString" value="flaechentypen_ca71f66a_50bb_41cb_86df_8046fae64926" name="Layer"/>
            <Option type="QString" value="Flächentypen" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/hoettges/Kanalprogramme/k_qkan/k_he8qk/beispiele/itwh_845/muster.sqlite' table=&quot;flaechentypen&quot;" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="false" name="UseCompleter"/>
            <Option type="QString" value="bezeichnung" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="createdat">
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
    <constraint constraints="3" exp_strength="0" unique_strength="1" field="pk" notnull_strength="1"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="apnam" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="anfangsabflussbeiwert" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="endabflussbeiwert" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="benetzungsverlust" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="muldenverlust" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="benetzung_startwert" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="mulden_startwert" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="rauheit_kst" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="pctZero" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="bodenklasse" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="flaechentyp" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="kommentar" notnull_strength="0"/>
    <constraint constraints="0" exp_strength="0" unique_strength="0" field="createdat" notnull_strength="0"/>
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
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="pk" hidden="1"/>
      <column type="field" width="-1" name="apnam" hidden="0"/>
      <column type="field" width="-1" name="anfangsabflussbeiwert" hidden="0"/>
      <column type="field" width="-1" name="endabflussbeiwert" hidden="0"/>
      <column type="field" width="-1" name="benetzungsverlust" hidden="0"/>
      <column type="field" width="-1" name="muldenverlust" hidden="0"/>
      <column type="field" width="-1" name="benetzung_startwert" hidden="0"/>
      <column type="field" width="-1" name="mulden_startwert" hidden="0"/>
      <column type="field" width="-1" name="rauheit_kst" hidden="1"/>
      <column type="field" width="-1" name="pctZero" hidden="1"/>
      <column type="field" width="-1" name="bodenklasse" hidden="0"/>
      <column type="field" width="-1" name="flaechentyp" hidden="0"/>
      <column type="field" width="-1" name="kommentar" hidden="0"/>
      <column type="field" width="-1" name="createdat" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_abflussparameter.ui</editform>
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
