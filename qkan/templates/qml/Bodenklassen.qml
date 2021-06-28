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
    <field name="bknam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateanfang">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateende">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsratestart">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="rueckgangskonstante">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenerationskonstante">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="saettigungswassergehalt">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="QString" value="0"/>
            <Option name="UseHtml" type="QString" value="0"/>
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
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_bodenklassen.ui</editform>
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
  <attributeEditorForm>
    <attributeEditorField index="1" name="bknam" showLabel="1"/>
    <attributeEditorField index="2" name="infiltrationsrateanfang" showLabel="1"/>
    <attributeEditorField index="3" name="infiltrationsrateende" showLabel="1"/>
    <attributeEditorField index="4" name="infiltrationsratestart" showLabel="1"/>
    <attributeEditorField index="5" name="rueckgangskonstante" showLabel="1"/>
    <attributeEditorField index="6" name="regenerationskonstante" showLabel="1"/>
    <attributeEditorField index="7" name="saettigungswassergehalt" showLabel="1"/>
    <attributeEditorField index="8" name="kommentar" showLabel="1"/>
  </attributeEditorForm>
  <editable>
    <field editable="1" name="bknam"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="infiltrationsrateanfang"/>
    <field editable="1" name="infiltrationsrateende"/>
    <field editable="1" name="infiltrationsratestart"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="regenerationskonstante"/>
    <field editable="1" name="rueckgangskonstante"/>
    <field editable="1" name="saettigungswassergehalt"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="bknam"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="infiltrationsrateanfang"/>
    <field labelOnTop="0" name="infiltrationsrateende"/>
    <field labelOnTop="0" name="infiltrationsratestart"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="regenerationskonstante"/>
    <field labelOnTop="0" name="rueckgangskonstante"/>
    <field labelOnTop="0" name="saettigungswassergehalt"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>4</layerGeometryType>
</qgis>
