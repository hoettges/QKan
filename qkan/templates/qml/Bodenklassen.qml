<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" maxScale="0" styleCategories="AllStyleCategories" version="3.20.1-Odense" minScale="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal endField="" endExpression="" mode="0" startExpression="" durationUnit="min" enabled="0" fixedDuration="0" durationField="" accumulate="0" startField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="0" type="QString" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="bknam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateanfang" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateende" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsratestart" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="rueckgangskonstante" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenerationskonstante" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="saettigungswassergehalt" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option value="1" type="QString" name="allow_null"/>
            <Option value="1" type="QString" name="calendar_popup"/>
            <Option value="yyyy.MM.dd HH:mm:ss" type="QString" name="display_format"/>
            <Option value="YYYY.MM.dd HH:mm:ss" type="QString" name="field_format"/>
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
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="bknam" expression=""/>
    <default applyOnUpdate="0" field="infiltrationsrateanfang" expression=""/>
    <default applyOnUpdate="0" field="infiltrationsrateende" expression=""/>
    <default applyOnUpdate="0" field="infiltrationsratestart" expression=""/>
    <default applyOnUpdate="0" field="rueckgangskonstante" expression=""/>
    <default applyOnUpdate="0" field="regenerationskonstante" expression=""/>
    <default applyOnUpdate="0" field="saettigungswassergehalt" expression=""/>
    <default applyOnUpdate="0" field="kommentar" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression=""/>
  </defaults>
  <constraints>
    <constraint notnull_strength="1" unique_strength="1" exp_strength="0" field="pk" constraints="3"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="bknam" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="infiltrationsrateanfang" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="infiltrationsrateende" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="infiltrationsratestart" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="rueckgangskonstante" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="regenerationskonstante" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="saettigungswassergehalt" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="kommentar" constraints="0"/>
    <constraint notnull_strength="0" unique_strength="0" exp_strength="0" field="createdat" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="bknam"/>
    <constraint exp="" desc="" field="infiltrationsrateanfang"/>
    <constraint exp="" desc="" field="infiltrationsrateende"/>
    <constraint exp="" desc="" field="infiltrationsratestart"/>
    <constraint exp="" desc="" field="rueckgangskonstante"/>
    <constraint exp="" desc="" field="regenerationskonstante"/>
    <constraint exp="" desc="" field="saettigungswassergehalt"/>
    <constraint exp="" desc="" field="kommentar"/>
    <constraint exp="" desc="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" hidden="0" name="pk" width="-1"/>
      <column type="field" hidden="0" name="bknam" width="-1"/>
      <column type="field" hidden="0" name="infiltrationsrateanfang" width="-1"/>
      <column type="field" hidden="0" name="infiltrationsrateende" width="-1"/>
      <column type="field" hidden="0" name="infiltrationsratestart" width="-1"/>
      <column type="field" hidden="0" name="rueckgangskonstante" width="-1"/>
      <column type="field" hidden="0" name="regenerationskonstante" width="-1"/>
      <column type="field" hidden="0" name="saettigungswassergehalt" width="-1"/>
      <column type="field" hidden="0" name="kommentar" width="-1"/>
      <column type="field" hidden="0" name="createdat" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
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
    <attributeEditorField showLabel="1" index="1" name="bknam"/>
    <attributeEditorField showLabel="1" index="2" name="infiltrationsrateanfang"/>
    <attributeEditorField showLabel="1" index="3" name="infiltrationsrateende"/>
    <attributeEditorField showLabel="1" index="4" name="infiltrationsratestart"/>
    <attributeEditorField showLabel="1" index="5" name="rueckgangskonstante"/>
    <attributeEditorField showLabel="1" index="6" name="regenerationskonstante"/>
    <attributeEditorField showLabel="1" index="7" name="saettigungswassergehalt"/>
    <attributeEditorField showLabel="1" index="8" name="kommentar"/>
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
  <reuseLastValue>
    <field name="bknam" reuseLastValue="0"/>
    <field name="createdat" reuseLastValue="0"/>
    <field name="infiltrationsrateanfang" reuseLastValue="0"/>
    <field name="infiltrationsrateende" reuseLastValue="0"/>
    <field name="infiltrationsratestart" reuseLastValue="0"/>
    <field name="kommentar" reuseLastValue="0"/>
    <field name="pk" reuseLastValue="0"/>
    <field name="regenerationskonstante" reuseLastValue="0"/>
    <field name="rueckgangskonstante" reuseLastValue="0"/>
    <field name="saettigungswassergehalt" reuseLastValue="0"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"bknam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
