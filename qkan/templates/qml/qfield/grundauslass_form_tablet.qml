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
    <field name="haltnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schoben">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="false"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="schnam"/>
            <Option name="Layer" type="QString" value="schaechte20161016203756252"/>
            <Option name="LayerName" type="QString" value="Knotenpunkte"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Hoettges/QKan/Uebung/qfield/Modell_02.sqlite' table=&quot;schaechte&quot; (geom)"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="false"/>
            <Option name="Value" type="QString" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schunten">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="false"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="schnam"/>
            <Option name="Layer" type="QString" value="schaechte20161016203756252"/>
            <Option name="LayerName" type="QString" value="Knotenpunkte"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/User/Desktop/Hiwi Hoettges/QKan/Uebung/qfield/Modell_02.sqlite' table=&quot;schaechte&quot; (geom)"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="false"/>
            <Option name="Value" type="QString" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="hoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="breite">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="laenge">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohleoben">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="sohleunten">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="teilgebiet">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="profilnam">
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
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="strasse">
      <editWidget type="TextEdit">
        <config>
          <Option/>
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
    <field name="ks">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltungstyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
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
            <Option name="UseCompleter" type="bool" value="false"/>
            <Option name="Value" type="QString" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="xschob">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="yschob">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="xschun">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="yschun">
      <editWidget type="Hidden">
        <config>
          <Option/>
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
  <editform tolerant="1">C:/Users/User/Desktop/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/qkan_grundseitenauslass.ui</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS-Formulare können eine Python-Funktion haben,, die aufgerufen wird, wenn sich das Formular öffnet

Diese Funktion kann verwendet werden um dem Formular Extralogik hinzuzufügen.

Der Name der Funktion wird im Feld "Python Init-Function" angegeben
Ein Beispiel folgt:
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
        <attributeEditorField name="haltnam" showLabel="1" index="1"/>
        <attributeEditorField name="profilnam" showLabel="1" index="10"/>
        <attributeEditorField name="material" showLabel="1" index="13"/>
      </attributeEditorContainer>
      <attributeEditorContainer groupBox="1" columnCount="1" name="Geometrie" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
        <attributeEditorField name="hoehe" showLabel="1" index="4"/>
        <attributeEditorField name="breite" showLabel="1" index="5"/>
        <attributeEditorField name="laenge" showLabel="1" index="6"/>
      </attributeEditorContainer>
      <attributeEditorContainer groupBox="1" columnCount="1" name="sonstiges" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
        <attributeEditorField name="teilgebiet" showLabel="1" index="9"/>
        <attributeEditorField name="entwart" showLabel="1" index="11"/>
        <attributeEditorField name="strasse" showLabel="1" index="12"/>
        <attributeEditorField name="ks" showLabel="1" index="14"/>
        <attributeEditorField name="haltungstyp" showLabel="1" index="15"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer groupBox="0" columnCount="1" name="Anfangsschacht" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorField name="schoben" showLabel="1" index="2"/>
      <attributeEditorField name="sohleoben" showLabel="1" index="7"/>
    </attributeEditorContainer>
    <attributeEditorContainer groupBox="0" columnCount="1" name="Endschacht" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorField name="schunten" showLabel="1" index="3"/>
      <attributeEditorField name="sohleunten" showLabel="1" index="8"/>
    </attributeEditorContainer>
    <attributeEditorContainer groupBox="0" columnCount="1" name="Sonstige Daten" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorField name="createdat" showLabel="1" index="22"/>
      <attributeEditorField name="simstatus" showLabel="1" index="16"/>
    </attributeEditorContainer>
    <attributeEditorContainer groupBox="0" columnCount="1" name="Kommentar" visibilityExpression="" showLabel="1" visibilityExpressionEnabled="0">
      <attributeEditorField name="kommentar" showLabel="1" index="21"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field name="breite" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="deckeloben" editable="1"/>
    <field name="deckelunten" editable="1"/>
    <field name="entwart" editable="1"/>
    <field name="haltnam" editable="1"/>
    <field name="haltungstyp" editable="1"/>
    <field name="hoehe" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="ks" editable="1"/>
    <field name="laenge" editable="1"/>
    <field name="material" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="profilnam" editable="1"/>
    <field name="qzu" editable="1"/>
    <field name="schoben" editable="1"/>
    <field name="schunten" editable="1"/>
    <field name="simstatus" editable="1"/>
    <field name="sohleoben" editable="1"/>
    <field name="sohleunten" editable="1"/>
    <field name="strasse" editable="1"/>
    <field name="teilgebiet" editable="1"/>
    <field name="xschob" editable="1"/>
    <field name="xschun" editable="1"/>
    <field name="yschob" editable="1"/>
    <field name="yschun" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="breite" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="deckeloben" labelOnTop="0"/>
    <field name="deckelunten" labelOnTop="0"/>
    <field name="entwart" labelOnTop="0"/>
    <field name="haltnam" labelOnTop="0"/>
    <field name="haltungstyp" labelOnTop="0"/>
    <field name="hoehe" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="ks" labelOnTop="0"/>
    <field name="laenge" labelOnTop="0"/>
    <field name="material" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="profilnam" labelOnTop="0"/>
    <field name="qzu" labelOnTop="0"/>
    <field name="schoben" labelOnTop="0"/>
    <field name="schunten" labelOnTop="0"/>
    <field name="simstatus" labelOnTop="0"/>
    <field name="sohleoben" labelOnTop="0"/>
    <field name="sohleunten" labelOnTop="0"/>
    <field name="strasse" labelOnTop="0"/>
    <field name="teilgebiet" labelOnTop="0"/>
    <field name="xschob" labelOnTop="0"/>
    <field name="xschun" labelOnTop="0"/>
    <field name="yschob" labelOnTop="0"/>
    <field name="yschun" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="breite"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="entwart"/>
    <field reuseLastValue="0" name="haltnam"/>
    <field reuseLastValue="0" name="haltungstyp"/>
    <field reuseLastValue="0" name="hoehe"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="ks"/>
    <field reuseLastValue="0" name="laenge"/>
    <field reuseLastValue="0" name="material"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="profilnam"/>
    <field reuseLastValue="0" name="schoben"/>
    <field reuseLastValue="0" name="schunten"/>
    <field reuseLastValue="0" name="simstatus"/>
    <field reuseLastValue="0" name="sohleoben"/>
    <field reuseLastValue="0" name="sohleunten"/>
    <field reuseLastValue="0" name="strasse"/>
    <field reuseLastValue="0" name="teilgebiet"/>
    <field reuseLastValue="0" name="xschob"/>
    <field reuseLastValue="0" name="xschun"/>
    <field reuseLastValue="0" name="yschob"/>
    <field reuseLastValue="0" name="yschun"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
