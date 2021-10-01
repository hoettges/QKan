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
    <field name="elnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="elnam"/>
            <Option name="Layer" type="QString" value="einleit20171004110830029"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="elnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="haltnam"/>
            <Option name="Layer" type="QString" value="haltungen20161016203756230"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
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
    <field name="geom">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="gbuf">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_anbindungeinleit.ui</editform>
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
    <field editable="1" name="elnam"/>
    <field editable="1" name="gbuf"/>
    <field editable="1" name="geom"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="schnam"/>
    <field editable="1" name="teilgebiet"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="elnam"/>
    <field labelOnTop="0" name="gbuf"/>
    <field labelOnTop="0" name="geom"/>
    <field labelOnTop="0" name="haltnam"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="schnam"/>
    <field labelOnTop="0" name="teilgebiet"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
