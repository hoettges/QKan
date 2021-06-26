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
    <field name="profilnam" configurationFlags="None">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="1"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="profilnam"/>
            <Option type="QString" name="Layer" value="profile20161018090721921"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="profilnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="wspiegel" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="wbreite" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="profilnam" name=""/>
    <alias index="2" field="wspiegel" name=""/>
    <alias index="3" field="wbreite" name=""/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="profilnam" applyOnUpdate="0" expression="''"/>
    <default field="wspiegel" applyOnUpdate="0" expression=""/>
    <default field="wbreite" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint field="profilnam" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="wspiegel" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint field="wbreite" constraints="0" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="profilnam" desc=""/>
    <constraint exp="" field="wspiegel" desc=""/>
    <constraint exp="" field="wbreite" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="profilnam"/>
      <column width="-1" type="field" hidden="0" name="wspiegel"/>
      <column width="-1" type="field" hidden="0" name="wbreite"/>
      <column width="-1" type="actions" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/hoettges/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\qkan\forms\qkan_profildaten.ui</editform>
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
    <field name="pk" editable="1"/>
    <field name="profilnam" editable="1"/>
    <field name="wbreite" editable="1"/>
    <field name="wspiegel" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="pk" labelOnTop="0"/>
    <field name="profilnam" labelOnTop="0"/>
    <field name="wbreite" labelOnTop="0"/>
    <field name="wspiegel" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>COALESCE("pk", '&lt;NULL>')</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
