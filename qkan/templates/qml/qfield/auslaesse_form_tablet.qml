<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Forms" version="3.22.4-Białowieża">
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohlhoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="deckelhoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="durchm">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="druckdicht">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ueberstauflaeche">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="entwart">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="bezeichnung"/>
            <Option name="Layer" type="QString" value="entwaesserungsarten20161018090806784"/>
            <Option name="LayerName" type="QString" value="Entwässerungsarten"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Höttges/QGIS/muster.sqlite' table=&quot;entwaesserungsarten&quot;"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="strasse">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="teilgebiet">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="tgnam"/>
            <Option name="Layer" type="QString" value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0"/>
            <Option name="LayerName" type="QString" value="Teilgebiete"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Hoettges/QKan/Uebung/qfield/Modell_02.sqlite' table=&quot;teilgebiete&quot; (geom)"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="tgnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="knotentyp">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="knotentyp"/>
            <Option name="Layer" type="QString" value="knotentypen_52223d4a_7631_4169_b6e4_0fa742c73d3c"/>
            <Option name="LayerName" type="QString" value="Knotentypen"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Höttges/QGIS/muster.sqlite' table=&quot;knotentypen&quot;"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="knotentyp"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="auslasstyp">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="bezeichnung"/>
            <Option name="Layer" type="QString" value="auslasstypen20161201095045204"/>
            <Option name="LayerName" type="QString" value="Auslasstypen"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Höttges/QGIS/muster.sqlite' table=&quot;auslasstypen&quot;"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schachttyp">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="schachttyp"/>
            <Option name="Layer" type="QString" value="schachttypen_4be33fc7_32a2_4f96_b120_4253af1bd597"/>
            <Option name="LayerName" type="QString" value="Schachttypen"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Hoettges/QKan/Uebung/qfield/Modell_02.sqlite' table=&quot;schachttypen&quot;"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="schachttyp"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="simstatus">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="bezeichnung"/>
            <Option name="Layer" type="QString" value="simulationsstatus20161201095050780"/>
            <Option name="LayerName" type="QString" value="Planungsstatus"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Hoettges/QKan/Uebung/qfield/Modell_02.sqlite' table=&quot;simulationsstatus&quot;"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="material">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="xsch">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ysch">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option name="allow_null" type="bool" value="true"/>
            <Option name="calendar_popup" type="bool" value="true"/>
            <Option name="display_format" type="QString" value="dd.MM.yyyy HH:mm:ss"/>
            <Option name="field_format" type="QString" value="YYYY-MM-dd HH:mm:ss"/>
            <Option name="field_iso_format" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="geom">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="x">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="false"/>
            <Option name="UseHtml" type="QString" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="y">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <editform tolerant="1">C:/Users/User/Desktop/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/qkan_auslaesse.ui</editform>
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
  <editorlayout>tablayout</editorlayout>
  <attributeEditorForm>
    <attributeEditorContainer groupBox="0" columnCount="2" name="Objektdaten" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorContainer groupBox="1" columnCount="1" name="Basisdaten" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
        <attributeEditorField name="schnam" showLabel="1" index="1"/>
        <attributeEditorField name="durchm" showLabel="1" index="4"/>
        <attributeEditorField name="material" showLabel="1" index="14"/>
      </attributeEditorContainer>
      <attributeEditorContainer groupBox="1" columnCount="1" name="Lage" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
        <attributeEditorField name="sohlhoehe" showLabel="1" index="2"/>
        <attributeEditorField name="deckelhoehe" showLabel="1" index="3"/>
        <attributeEditorField name="x" showLabel="1" index="20"/>
        <attributeEditorField name="y" showLabel="1" index="21"/>
      </attributeEditorContainer>
      <attributeEditorContainer groupBox="1" columnCount="1" name="sontiges" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
        <attributeEditorField name="druckdicht" showLabel="1" index="5"/>
        <attributeEditorField name="ueberstauflaeche" showLabel="1" index="6"/>
        <attributeEditorField name="entwart" showLabel="1" index="7"/>
        <attributeEditorField name="strasse" showLabel="1" index="8"/>
        <attributeEditorField name="knotentyp" showLabel="1" index="10"/>
        <attributeEditorField name="auslasstyp" showLabel="1" index="11"/>
        <attributeEditorField name="schachttyp" showLabel="1" index="12"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer groupBox="0" columnCount="1" name="sonstige Daten" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorField name="teilgebiet" showLabel="1" index="9"/>
      <attributeEditorField name="simstatus" showLabel="1" index="13"/>
      <attributeEditorField name="createdat" showLabel="1" index="18"/>
    </attributeEditorContainer>
    <attributeEditorContainer groupBox="0" columnCount="1" name="Kommentar" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorField name="kommentar" showLabel="1" index="17"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field name="auslasstyp" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="deckelhoehe" editable="1"/>
    <field name="druckdicht" editable="1"/>
    <field name="durchm" editable="1"/>
    <field name="entwart" editable="1"/>
    <field name="geom" editable="1"/>
    <field name="istauslass" editable="1"/>
    <field name="istspeicher" editable="1"/>
    <field name="knotentyp" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="material" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="schachttyp" editable="1"/>
    <field name="schnam" editable="1"/>
    <field name="simstatus" editable="1"/>
    <field name="sohlhoehe" editable="1"/>
    <field name="strasse" editable="1"/>
    <field name="teilgebiet" editable="1"/>
    <field name="ueberstauflaeche" editable="1"/>
    <field name="x" editable="0"/>
    <field name="xsch" editable="1"/>
    <field name="y" editable="0"/>
    <field name="ysch" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="auslasstyp" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="deckelhoehe" labelOnTop="0"/>
    <field name="druckdicht" labelOnTop="0"/>
    <field name="durchm" labelOnTop="0"/>
    <field name="entwart" labelOnTop="0"/>
    <field name="geom" labelOnTop="0"/>
    <field name="istauslass" labelOnTop="0"/>
    <field name="istspeicher" labelOnTop="0"/>
    <field name="knotentyp" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="material" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="schachttyp" labelOnTop="0"/>
    <field name="schnam" labelOnTop="0"/>
    <field name="simstatus" labelOnTop="0"/>
    <field name="sohlhoehe" labelOnTop="0"/>
    <field name="strasse" labelOnTop="0"/>
    <field name="teilgebiet" labelOnTop="0"/>
    <field name="ueberstauflaeche" labelOnTop="0"/>
    <field name="x" labelOnTop="0"/>
    <field name="xsch" labelOnTop="0"/>
    <field name="y" labelOnTop="0"/>
    <field name="ysch" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="auslasstyp"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="deckelhoehe"/>
    <field reuseLastValue="0" name="druckdicht"/>
    <field reuseLastValue="0" name="durchm"/>
    <field reuseLastValue="0" name="entwart"/>
    <field reuseLastValue="0" name="geom"/>
    <field reuseLastValue="0" name="knotentyp"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="material"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="schachttyp"/>
    <field reuseLastValue="0" name="schnam"/>
    <field reuseLastValue="0" name="simstatus"/>
    <field reuseLastValue="0" name="sohlhoehe"/>
    <field reuseLastValue="0" name="strasse"/>
    <field reuseLastValue="0" name="teilgebiet"/>
    <field reuseLastValue="0" name="ueberstauflaeche"/>
    <field reuseLastValue="0" name="x"/>
    <field reuseLastValue="0" name="xsch"/>
    <field reuseLastValue="0" name="y"/>
    <field reuseLastValue="0" name="ysch"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>0</layerGeometryType>
</qgis>
