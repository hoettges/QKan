<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Forms" version="3.18.3-Zürich">
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="gebnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="false"/>
            <Option name="UseHtml" type="QString" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="false"/>
            <Option name="AllowNull" type="QString" value="false"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="schnam"/>
            <Option name="Layer" type="QString" value="schaechte20161220162259105"/>
            <Option name="NofColumns" type="QString" value="1"/>
            <Option name="OrderByValue" type="QString" value="false"/>
            <Option name="UseCompleter" type="QString" value="false"/>
            <Option name="Value" type="QString" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="hoeheob">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="hoeheun">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fliessweg">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="false"/>
            <Option name="UseHtml" type="QString" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="basisabfluss">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="cn">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="false"/>
            <Option name="UseHtml" type="QString" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenschreiber">
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
            <Option name="AllowMulti" type="QString" value="false"/>
            <Option name="AllowNull" type="QString" value="false"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="tgnam"/>
            <Option name="Layer" type="QString" value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0"/>
            <Option name="NofColumns" type="QString" value="1"/>
            <Option name="OrderByValue" type="QString" value="false"/>
            <Option name="UseCompleter" type="QString" value="false"/>
            <Option name="Value" type="QString" value="tgnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/qkan_aussengebiete.ui</editform>
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
    <field editable="1" name="basisabfluss"/>
    <field editable="1" name="cn"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="fliessweg"/>
    <field editable="1" name="gebnam"/>
    <field editable="1" name="hoeheob"/>
    <field editable="1" name="hoeheun"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="regenschreiber"/>
    <field editable="1" name="schnam"/>
    <field editable="1" name="teilgebiet"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="basisabfluss"/>
    <field labelOnTop="0" name="cn"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="fliessweg"/>
    <field labelOnTop="0" name="gebnam"/>
    <field labelOnTop="0" name="hoeheob"/>
    <field labelOnTop="0" name="hoeheun"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="regenschreiber"/>
    <field labelOnTop="0" name="schnam"/>
    <field labelOnTop="0" name="teilgebiet"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>2</layerGeometryType>
</qgis>
