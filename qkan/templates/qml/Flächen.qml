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
    <field name="flnam">
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
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="bool" value="false"/>
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Description" type="QString" value=""/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="haltnam"/>
            <Option name="Layer" type="QString" value="haltungen_Kopie20161016203906444"/>
            <Option name="LayerName" type="QString" value="Haltungslinien"/>
            <Option name="LayerProviderName" type="QString" value="spatialite"/>
            <Option name="LayerSource" type="QString" value="dbname='C:/Users/hoettges/Documents/QKan/qgis/projekt.sqlite' table=&quot;haltungen&quot; (geom)"/>
            <Option name="NofColumns" type="int" value="1"/>
            <Option name="OrderByValue" type="bool" value="false"/>
            <Option name="UseCompleter" type="bool" value="true"/>
            <Option name="Value" type="QString" value="haltnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schnam">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="neigkl">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="neigung">
      <editWidget type="TextEdit">
        <config>
          <Option/>
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
    <field name="regenschreiber">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="abflussparameter">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="apnam"/>
            <Option name="Layer" type="QString" value="Abflussparameter_KP_e16f4a36_8f43_4398_a67c_53cbd2e8d3e9"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="apnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="aufteilen">
      <editWidget type="CheckBox">
        <config>
          <Option type="Map">
            <Option name="CheckedState" type="QString" value="ja"/>
            <Option name="UncheckedState" type="QString" value=""/>
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
  </fieldConfiguration>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_flaechen.ui</editform>
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
    <field editable="1" name="abflussparameter"/>
    <field editable="1" name="aufteilen"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="flnam"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="neigkl"/>
    <field editable="1" name="neigung"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="regenschreiber"/>
    <field editable="1" name="schnam"/>
    <field editable="1" name="teilgebiet"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abflussparameter"/>
    <field labelOnTop="0" name="aufteilen"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="flnam"/>
    <field labelOnTop="0" name="haltnam"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="neigkl"/>
    <field labelOnTop="0" name="neigung"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="regenschreiber"/>
    <field labelOnTop="0" name="schnam"/>
    <field labelOnTop="0" name="teilgebiet"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>2</layerGeometryType>
</qgis>
