<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" minScale="0" maxScale="0" readOnly="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal durationField="" enabled="0" startField="" fixedDuration="0" startExpression="" endExpression="" mode="0" accumulate="0" durationUnit="min" limitMode="0" endField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="0" name="embeddedWidgets/count" type="QString"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector" showLabelLegend="0"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="pk" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="bknam" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateanfang" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsrateende" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="infiltrationsratestart" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="rueckgangskonstante" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="regenerationskonstante" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="saettigungswassergehalt" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" name="IsMultiline" type="QString"/>
            <Option value="0" name="UseHtml" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option value="1" name="allow_null" type="QString"/>
            <Option value="1" name="calendar_popup" type="QString"/>
            <Option value="dd.MM.yyyy HH:mm:ss" name="display_format" type="QString"/>
            <Option value="YYYY-MM-dd HH:mm:ss" name="field_format" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" name="" index="0"/>
    <alias field="bknam" name="Name" index="1"/>
    <alias field="infiltrationsrateanfang" name="Infiltrationsrate Anfang" index="2"/>
    <alias field="infiltrationsrateende" name="Infiltrationsrate Ende" index="3"/>
    <alias field="infiltrationsratestart" name="Infiltrationsrate Start" index="4"/>
    <alias field="rueckgangskonstante" name="Rückgangskonstante" index="5"/>
    <alias field="regenerationskonstante" name="Regenerationskonstante" index="6"/>
    <alias field="saettigungswassergehalt" name="Sättigungswassergehalt" index="7"/>
    <alias field="kommentar" name="Kommentar" index="8"/>
    <alias field="createdat" name="bearbeitet" index="9"/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="bknam" applyOnUpdate="0" expression=""/>
    <default field="infiltrationsrateanfang" applyOnUpdate="0" expression=""/>
    <default field="infiltrationsrateende" applyOnUpdate="0" expression=""/>
    <default field="infiltrationsratestart" applyOnUpdate="0" expression=""/>
    <default field="rueckgangskonstante" applyOnUpdate="0" expression=""/>
    <default field="regenerationskonstante" applyOnUpdate="0" expression=""/>
    <default field="saettigungswassergehalt" applyOnUpdate="0" expression=""/>
    <default field="kommentar" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint field="bknam" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="infiltrationsrateanfang" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="infiltrationsrateende" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="infiltrationsratestart" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="rueckgangskonstante" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="regenerationskonstante" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="saettigungswassergehalt" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="kommentar" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="createdat" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="bknam" exp="" desc=""/>
    <constraint field="infiltrationsrateanfang" exp="" desc=""/>
    <constraint field="infiltrationsrateende" exp="" desc=""/>
    <constraint field="infiltrationsratestart" exp="" desc=""/>
    <constraint field="rueckgangskonstante" exp="" desc=""/>
    <constraint field="regenerationskonstante" exp="" desc=""/>
    <constraint field="saettigungswassergehalt" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column name="pk" type="field" hidden="0" width="-1"/>
      <column name="bknam" type="field" hidden="0" width="-1"/>
      <column name="infiltrationsrateanfang" type="field" hidden="0" width="-1"/>
      <column name="infiltrationsrateende" type="field" hidden="0" width="-1"/>
      <column name="infiltrationsratestart" type="field" hidden="0" width="-1"/>
      <column name="rueckgangskonstante" type="field" hidden="0" width="-1"/>
      <column name="regenerationskonstante" type="field" hidden="0" width="-1"/>
      <column name="saettigungswassergehalt" type="field" hidden="0" width="-1"/>
      <column name="kommentar" type="field" hidden="0" width="-1"/>
      <column name="createdat" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users\hoettges\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_bodenklassen.ui</editform>
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
    <attributeEditorField showLabel="1" name="bknam" index="1"/>
    <attributeEditorField showLabel="1" name="infiltrationsrateanfang" index="2"/>
    <attributeEditorField showLabel="1" name="infiltrationsrateende" index="3"/>
    <attributeEditorField showLabel="1" name="infiltrationsratestart" index="4"/>
    <attributeEditorField showLabel="1" name="rueckgangskonstante" index="5"/>
    <attributeEditorField showLabel="1" name="regenerationskonstante" index="6"/>
    <attributeEditorField showLabel="1" name="saettigungswassergehalt" index="7"/>
    <attributeEditorField showLabel="1" name="kommentar" index="8"/>
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
