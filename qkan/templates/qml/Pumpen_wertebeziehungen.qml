<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.24.1-Tisler" styleCategories="Forms">
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schoben">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="schnam" name="Key"/>
            <Option type="QString" value="schaechte20161016203756252" name="Layer"/>
            <Option type="QString" value="Knotenpunkte" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/hoettges/Kanalprogramme/k_qkan/k_he8qk/beispiele/itwh_845/muster.sqlite' table=&quot;schaechte&quot; (geom)" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="true" name="UseCompleter"/>
            <Option type="QString" value="schnam" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schunten">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="schnam" name="Key"/>
            <Option type="QString" value="schaechte20161016203756252" name="Layer"/>
            <Option type="QString" value="Knotenpunkte" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/hoettges/Kanalprogramme/k_qkan/k_he8qk/beispiele/itwh_845/muster.sqlite' table=&quot;schaechte&quot; (geom)" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="true" name="UseCompleter"/>
            <Option type="QString" value="schnam" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="hoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="breite">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="laenge">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohleoben">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohleunten">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="deckeloben">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="deckelunten">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="teilgebiet">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="tgnam" name="Key"/>
            <Option type="QString" value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0" name="Layer"/>
            <Option type="QString" value="Teilgebiete" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/hoettges/Kanalprogramme/k_qkan/k_he8qk/beispiele/itwh_845/muster.sqlite' table=&quot;teilgebiete&quot; (geom)" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="true" name="UseCompleter"/>
            <Option type="QString" value="tgnam" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="qzu">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="profilnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="entwart">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="material">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ks">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sonderelement">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="simstatus">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="AllowMulti"/>
            <Option type="bool" value="true" name="AllowNull"/>
            <Option type="QString" value="" name="Description"/>
            <Option type="QString" value="" name="FilterExpression"/>
            <Option type="QString" value="bezeichnung" name="Key"/>
            <Option type="QString" value="simulationsstatus20161201095050780" name="Layer"/>
            <Option type="QString" value="Simulationsstatus" name="LayerName"/>
            <Option type="QString" value="spatialite" name="LayerProviderName"/>
            <Option type="QString" value="dbname='C:/FHAC/hoettges/Kanalprogramme/k_qkan/k_he8qk/beispiele/itwh_845/muster.sqlite' table=&quot;simulationsstatus&quot;" name="LayerSource"/>
            <Option type="int" value="1" name="NofColumns"/>
            <Option type="bool" value="false" name="OrderByValue"/>
            <Option type="bool" value="false" name="UseCompleter"/>
            <Option type="QString" value="bezeichnung" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="bool" value="true" name="allow_null"/>
            <Option type="bool" value="true" name="calendar_popup"/>
            <Option type="QString" value="dd.MM.yyyy HH:mm:ss" name="display_format"/>
            <Option type="QString" value="YYYY-MM-dd HH:mm:ss" name="field_format"/>
            <Option type="bool" value="false" name="field_iso_format"/>
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
  </fieldConfiguration>
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_pumpen.ui</editform>
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
    <field editable="1" name="ausschalthoehe"/>
    <field editable="1" name="breite"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="deckeloben"/>
    <field editable="1" name="deckelunten"/>
    <field editable="1" name="einschalthoehe"/>
    <field editable="1" name="entwart"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="hoehe"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="ks"/>
    <field editable="1" name="laenge"/>
    <field editable="1" name="material"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="pnam"/>
    <field editable="1" name="profilnam"/>
    <field editable="1" name="pumpentyp"/>
    <field editable="1" name="qzu"/>
    <field editable="1" name="schoben"/>
    <field editable="1" name="schunten"/>
    <field editable="1" name="simstatus"/>
    <field editable="1" name="sohle"/>
    <field editable="1" name="sohleoben"/>
    <field editable="1" name="sohleunten"/>
    <field editable="1" name="sonderelement"/>
    <field editable="1" name="steuersch"/>
    <field editable="1" name="teilgebiet"/>
    <field editable="1" name="volanf"/>
    <field editable="1" name="volges"/>
    <field editable="1" name="xschob"/>
    <field editable="1" name="xschun"/>
    <field editable="1" name="yschob"/>
    <field editable="1" name="yschun"/>
  </editable>
  <labelOnTop>
    <field name="ausschalthoehe" labelOnTop="0"/>
    <field name="breite" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="deckeloben" labelOnTop="0"/>
    <field name="deckelunten" labelOnTop="0"/>
    <field name="einschalthoehe" labelOnTop="0"/>
    <field name="entwart" labelOnTop="0"/>
    <field name="haltnam" labelOnTop="0"/>
    <field name="hoehe" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="ks" labelOnTop="0"/>
    <field name="laenge" labelOnTop="0"/>
    <field name="material" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="pnam" labelOnTop="0"/>
    <field name="profilnam" labelOnTop="0"/>
    <field name="pumpentyp" labelOnTop="0"/>
    <field name="qzu" labelOnTop="0"/>
    <field name="schoben" labelOnTop="0"/>
    <field name="schunten" labelOnTop="0"/>
    <field name="simstatus" labelOnTop="0"/>
    <field name="sohle" labelOnTop="0"/>
    <field name="sohleoben" labelOnTop="0"/>
    <field name="sohleunten" labelOnTop="0"/>
    <field name="sonderelement" labelOnTop="0"/>
    <field name="steuersch" labelOnTop="0"/>
    <field name="teilgebiet" labelOnTop="0"/>
    <field name="volanf" labelOnTop="0"/>
    <field name="volges" labelOnTop="0"/>
    <field name="xschob" labelOnTop="0"/>
    <field name="xschun" labelOnTop="0"/>
    <field name="yschob" labelOnTop="0"/>
    <field name="yschun" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="ausschalthoehe"/>
    <field reuseLastValue="0" name="breite"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="deckeloben"/>
    <field reuseLastValue="0" name="deckelunten"/>
    <field reuseLastValue="0" name="einschalthoehe"/>
    <field reuseLastValue="0" name="entwart"/>
    <field reuseLastValue="0" name="haltnam"/>
    <field reuseLastValue="0" name="hoehe"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="ks"/>
    <field reuseLastValue="0" name="laenge"/>
    <field reuseLastValue="0" name="material"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="pnam"/>
    <field reuseLastValue="0" name="profilnam"/>
    <field reuseLastValue="0" name="pumpentyp"/>
    <field reuseLastValue="0" name="qzu"/>
    <field reuseLastValue="0" name="schoben"/>
    <field reuseLastValue="0" name="schunten"/>
    <field reuseLastValue="0" name="simstatus"/>
    <field reuseLastValue="0" name="sohle"/>
    <field reuseLastValue="0" name="sohleoben"/>
    <field reuseLastValue="0" name="sohleunten"/>
    <field reuseLastValue="0" name="sonderelement"/>
    <field reuseLastValue="0" name="steuersch"/>
    <field reuseLastValue="0" name="teilgebiet"/>
    <field reuseLastValue="0" name="volanf"/>
    <field reuseLastValue="0" name="volges"/>
    <field reuseLastValue="0" name="xschob"/>
    <field reuseLastValue="0" name="xschun"/>
    <field reuseLastValue="0" name="yschob"/>
    <field reuseLastValue="0" name="yschun"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
