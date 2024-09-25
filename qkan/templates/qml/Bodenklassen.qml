<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" maxScale="0" readOnly="0" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|Temporal|Legend|Notes" minScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal limitMode="0" startField="" endField="" enabled="0" accumulate="0" durationField="" startExpression="" durationUnit="min" endExpression="" mode="0" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;bknam&quot;"/>
      </Option>
      <Option type="int" name="embeddedWidgets/count" value="0"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <legend type="default-vector" showLabelLegend="0"/>
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
            <Option type="QString" name="display_format" value="dd.MM.yyyy HH:mm:ss"/>
            <Option type="QString" name="field_format" value="yyyy-MM-dd HH:mm:ss"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="bknam" name="Name"/>
    <alias index="2" field="infiltrationsrateanfang" name="Infiltrationsrate Anfang"/>
    <alias index="3" field="infiltrationsrateende" name="Infiltrationsrate Ende"/>
    <alias index="4" field="infiltrationsratestart" name="Infiltrationsrate Start"/>
    <alias index="5" field="rueckgangskonstante" name="Rückgangskonstante"/>
    <alias index="6" field="regenerationskonstante" name="Regenerationskonstante"/>
    <alias index="7" field="saettigungswassergehalt" name="Sättigungswassergehalt"/>
    <alias index="8" field="kommentar" name="Kommentar"/>
    <alias index="9" field="createdat" name="bearbeitet"/>
  </aliases>
  <defaults>
    <default expression="" field="pk" applyOnUpdate="0"/>
    <default expression="" field="bknam" applyOnUpdate="0"/>
    <default expression="" field="infiltrationsrateanfang" applyOnUpdate="0"/>
    <default expression="" field="infiltrationsrateende" applyOnUpdate="0"/>
    <default expression="" field="infiltrationsratestart" applyOnUpdate="0"/>
    <default expression="" field="rueckgangskonstante" applyOnUpdate="0"/>
    <default expression="" field="regenerationskonstante" applyOnUpdate="0"/>
    <default expression="" field="saettigungswassergehalt" applyOnUpdate="0"/>
    <default expression="" field="kommentar" applyOnUpdate="0"/>
    <default expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')" field="createdat" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="2" notnull_strength="2" exp_strength="0"/>
    <constraint constraints="0" field="bknam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="infiltrationsrateanfang" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="infiltrationsrateende" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="infiltrationsratestart" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="rueckgangskonstante" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="regenerationskonstante" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="saettigungswassergehalt" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="pk"/>
    <constraint desc="" exp="" field="bknam"/>
    <constraint desc="" exp="" field="infiltrationsrateanfang"/>
    <constraint desc="" exp="" field="infiltrationsrateende"/>
    <constraint desc="" exp="" field="infiltrationsratestart"/>
    <constraint desc="" exp="" field="rueckgangskonstante"/>
    <constraint desc="" exp="" field="regenerationskonstante"/>
    <constraint desc="" exp="" field="saettigungswassergehalt"/>
    <constraint desc="" exp="" field="kommentar"/>
    <constraint desc="" exp="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
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
  <editform tolerant="1">C:\Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_bodenklassen.ui</editform>
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
    <attributeEditorField index="1" showLabel="1" name="bknam"/>
    <attributeEditorField index="2" showLabel="1" name="infiltrationsrateanfang"/>
    <attributeEditorField index="3" showLabel="1" name="infiltrationsrateende"/>
    <attributeEditorField index="4" showLabel="1" name="infiltrationsratestart"/>
    <attributeEditorField index="5" showLabel="1" name="rueckgangskonstante"/>
    <attributeEditorField index="6" showLabel="1" name="regenerationskonstante"/>
    <attributeEditorField index="7" showLabel="1" name="saettigungswassergehalt"/>
    <attributeEditorField index="8" showLabel="1" name="kommentar"/>
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
    <field reuseLastValue="0" name="bknam"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="infiltrationsrateanfang"/>
    <field reuseLastValue="0" name="infiltrationsrateende"/>
    <field reuseLastValue="0" name="infiltrationsratestart"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="regenerationskonstante"/>
    <field reuseLastValue="0" name="rueckgangskonstante"/>
    <field reuseLastValue="0" name="saettigungswassergehalt"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"bknam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
