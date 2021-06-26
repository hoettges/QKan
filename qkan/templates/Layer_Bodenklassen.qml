<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" maxScale="0" minScale="1e+08" version="3.18.3-Zürich" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|MapTips|AttributeTable|Rendering" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="bknam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateanfang" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateende" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsratestart" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="rueckgangskonstante" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenerationskonstante" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="saettigungswassergehalt" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="QString" name="allow_null" value="1"/>
            <Option type="QString" name="calendar_popup" value="1"/>
            <Option type="QString" name="display_format" value="yyyy.MM.dd HH:mm:ss"/>
            <Option type="QString" name="field_format" value="YYYY.MM.dd HH:mm:ss"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="bknam" name=""/>
    <alias index="2" field="infiltrationsrateanfang" name=""/>
    <alias index="3" field="infiltrationsrateende" name=""/>
    <alias index="4" field="infiltrationsratestart" name=""/>
    <alias index="5" field="rueckgangskonstante" name=""/>
    <alias index="6" field="regenerationskonstante" name=""/>
    <alias index="7" field="saettigungswassergehalt" name=""/>
    <alias index="8" field="kommentar" name=""/>
    <alias index="9" field="createdat" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="bknam" applyOnUpdate="0" expression="''"/>
    <default field="infiltrationsrateanfang" applyOnUpdate="0" expression=""/>
    <default field="infiltrationsrateende" applyOnUpdate="0" expression=""/>
    <default field="infiltrationsratestart" applyOnUpdate="0" expression=""/>
    <default field="rueckgangskonstante" applyOnUpdate="0" expression=""/>
    <default field="regenerationskonstante" applyOnUpdate="0" expression=""/>
    <default field="saettigungswassergehalt" applyOnUpdate="0" expression=""/>
    <default field="kommentar" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=" format_date( now(), 'yyyy.MM.dd HH:mm:ss')"/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint field="bknam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="infiltrationsrateanfang" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="infiltrationsrateende" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="infiltrationsratestart" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="rueckgangskonstante" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="regenerationskonstante" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="saettigungswassergehalt" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="kommentar" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="createdat" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="bknam" desc=""/>
    <constraint exp="" field="infiltrationsrateanfang" desc=""/>
    <constraint exp="" field="infiltrationsrateende" desc=""/>
    <constraint exp="" field="infiltrationsratestart" desc=""/>
    <constraint exp="" field="rueckgangskonstante" desc=""/>
    <constraint exp="" field="regenerationskonstante" desc=""/>
    <constraint exp="" field="saettigungswassergehalt" desc=""/>
    <constraint exp="" field="kommentar" desc=""/>
    <constraint exp="" field="createdat" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="bknam"/>
      <column width="-1" type="field" hidden="0" name="infiltrationsrateanfang"/>
      <column width="-1" type="field" hidden="0" name="infiltrationsrateende"/>
      <column width="-1" type="field" hidden="0" name="infiltrationsratestart"/>
      <column width="-1" type="field" hidden="0" name="rueckgangskonstante"/>
      <column width="-1" type="field" hidden="0" name="regenerationskonstante"/>
      <column width="-1" type="field" hidden="0" name="saettigungswassergehalt"/>
      <column width="-1" type="field" hidden="0" name="kommentar"/>
      <column width="-1" type="field" hidden="0" name="createdat"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
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
    <field name="bknam" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="infiltrationsrateanfang" editable="1"/>
    <field name="infiltrationsrateende" editable="1"/>
    <field name="infiltrationsratestart" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="regenerationskonstante" editable="1"/>
    <field name="rueckgangskonstante" editable="1"/>
    <field name="saettigungswassergehalt" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="bknam" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="infiltrationsrateanfang" labelOnTop="0"/>
    <field name="infiltrationsrateende" labelOnTop="0"/>
    <field name="infiltrationsratestart" labelOnTop="0"/>
    <field name="kommentar" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="regenerationskonstante" labelOnTop="0"/>
    <field name="rueckgangskonstante" labelOnTop="0"/>
    <field name="saettigungswassergehalt" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>COALESCE( "bknam", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
