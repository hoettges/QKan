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
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="flnam"/>
            <Option name="Layer" type="QString" value="Flächen_2449ac97_6c2e_49df_96bc_5b9cc1d96e2c"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="flnam"/>
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
    <field name="tezgnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="flnam"/>
            <Option name="Layer" type="QString" value="Haltungsflächen_38cc9a58_a57d_487e_bbac_6000457b0748"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="flnam"/>
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
    <field name="abflusstyp">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option name="AllowMulti" type="QString" value="0"/>
            <Option name="AllowNull" type="QString" value="1"/>
            <Option name="FilterExpression" type="QString" value=""/>
            <Option name="Key" type="QString" value="abflusstyp"/>
            <Option name="Layer" type="QString" value="abflusstypen_b1368d23_11b7_4b53_86a9_44feb5d66c5f"/>
            <Option name="OrderByValue" type="QString" value="0"/>
            <Option name="UseCompleter" type="QString" value="1"/>
            <Option name="Value" type="QString" value="abflusstyp"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="speicherzahl">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="speicherkonst">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="fliesszeitkanal">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="fliesszeitflaeche">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
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
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_anbindungflaechen.ui</editform>
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
    <field editable="1" name="abflusstyp"/>
    <field editable="1" name="fliesszeitflaeche"/>
    <field editable="1" name="fliesszeitkanal"/>
    <field editable="1" name="flnam"/>
    <field editable="1" name="gbuf"/>
    <field editable="1" name="geom"/>
    <field editable="1" name="haltnam"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="schnam"/>
    <field editable="1" name="speicherkonst"/>
    <field editable="1" name="speicherzahl"/>
    <field editable="1" name="teilgebiet"/>
    <field editable="1" name="tezgnam"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abflusstyp"/>
    <field labelOnTop="0" name="fliesszeitflaeche"/>
    <field labelOnTop="0" name="fliesszeitkanal"/>
    <field labelOnTop="0" name="flnam"/>
    <field labelOnTop="0" name="gbuf"/>
    <field labelOnTop="0" name="geom"/>
    <field labelOnTop="0" name="haltnam"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="schnam"/>
    <field labelOnTop="0" name="speicherkonst"/>
    <field labelOnTop="0" name="speicherzahl"/>
    <field labelOnTop="0" name="teilgebiet"/>
    <field labelOnTop="0" name="tezgnam"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
