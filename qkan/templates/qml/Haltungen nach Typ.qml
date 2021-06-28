<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Forms" version="3.18.3-Zürich">
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schoben">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="schnam"/>
            <Option name="Layer" type="QString" value="schaechte20161016203756252"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schunten">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="schnam"/>
            <Option name="Layer" type="QString" value="schaechte20161016203756252"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="hoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="breite">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="laenge">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohleoben">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohleunten">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="deckeloben">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="deckelunten">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="teilgebiet">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="tgnam"/>
            <Option name="Layer" type="QString" value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="tgnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="qzu">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="profilnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="profilnam"/>
            <Option name="Layer" type="QString" value="profile20161018090721921"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="profilnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="entwart">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="bezeichnung"/>
            <Option name="Layer" type="QString" value="entwaesserungsarten20161018090806784"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="rohrtyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ks">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="simstatus">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="bezeichnung"/>
            <Option name="Layer" type="QString" value="simulationsstatus20161201095050780"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option name="allow_null" type="QString" value="1"/>
            <Option name="calendar_popup" type="QString" value="1"/>
            <Option name="display_format" type="QString" value="yyyy.MM.dd HH:mm:ss"/>
            <Option name="field_format" type="QString" value="YYYY.MM.dd HH:mm:ss"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="xschob">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="yschob">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="xschun">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="yschun">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_haltungen.ui</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS-Formulare können eine Python-Funktion haben, die beim Öffnen des Formulars gestartet wird.

Hier kann dem Formular Extra-Logik hinzugefügt werden.

Der Name der Funktion wird im Feld "Python-Init-Function" angegeben.
Ein Beispiel:
"""
from PyQt4.QtGui import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>uifilelayout</editorlayout>
  <editable>
    <field editable="1" name="breite"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="deckeloben"/>
    <field editable="1" name="deckelunten"/>
    <field editable="1" name="entwart"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="hoehe"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="ks"/>
    <field editable="1" name="laenge"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="profilnam"/>
    <field editable="1" name="qzu"/>
    <field editable="1" name="rohrtyp"/>
    <field editable="1" name="schoben"/>
    <field editable="1" name="schunten"/>
    <field editable="1" name="simstatus"/>
    <field editable="1" name="sohleoben"/>
    <field editable="1" name="sohleunten"/>
    <field editable="1" name="teilgebiet"/>
    <field editable="1" name="xschob"/>
    <field editable="1" name="xschun"/>
    <field editable="1" name="yschob"/>
    <field editable="1" name="yschun"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="breite"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="deckeloben"/>
    <field labelOnTop="0" name="deckelunten"/>
    <field labelOnTop="0" name="entwart"/>
    <field labelOnTop="0" name="haltnam"/>
    <field labelOnTop="0" name="hoehe"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="ks"/>
    <field labelOnTop="0" name="laenge"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="profilnam"/>
    <field labelOnTop="0" name="qzu"/>
    <field labelOnTop="0" name="rohrtyp"/>
    <field labelOnTop="0" name="schoben"/>
    <field labelOnTop="0" name="schunten"/>
    <field labelOnTop="0" name="simstatus"/>
    <field labelOnTop="0" name="sohleoben"/>
    <field labelOnTop="0" name="sohleunten"/>
    <field labelOnTop="0" name="teilgebiet"/>
    <field labelOnTop="0" name="xschob"/>
    <field labelOnTop="0" name="xschun"/>
    <field labelOnTop="0" name="yschob"/>
    <field labelOnTop="0" name="yschun"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
