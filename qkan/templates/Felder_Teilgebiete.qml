<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Fields" version="3.6.3-Noosa">
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="tgnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ewdichte">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="wverbrauch">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="stdmittel">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="fremdwas">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flaeche">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="QString" name="allow_null" value="1"/>
            <Option type="QString" name="calendar_popup" value="1"/>
            <Option type="QString" name="display_format" value="dd.MM.yyyy HH:mm"/>
            <Option type="QString" name="field_format" value="dd.MM.yyyy HH:mm"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" index="0" name=""/>
    <alias field="tgnam" index="1" name=""/>
    <alias field="ewdichte" index="2" name=""/>
    <alias field="wverbrauch" index="3" name=""/>
    <alias field="stdmittel" index="4" name=""/>
    <alias field="fremdwas" index="5" name=""/>
    <alias field="flaeche" index="6" name=""/>
    <alias field="kommentar" index="7" name=""/>
    <alias field="createdat" index="8" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="tgnam" expression=""/>
    <default applyOnUpdate="0" field="ewdichte" expression=""/>
    <default applyOnUpdate="0" field="wverbrauch" expression=""/>
    <default applyOnUpdate="0" field="stdmittel" expression=""/>
    <default applyOnUpdate="0" field="fremdwas" expression=""/>
    <default applyOnUpdate="0" field="flaeche" expression=""/>
    <default applyOnUpdate="0" field="kommentar" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression="now()"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="tgnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="ewdichte" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="wverbrauch" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="stdmittel" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="fremdwas" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="flaeche" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="tgnam" exp="" desc=""/>
    <constraint field="ewdichte" exp="" desc=""/>
    <constraint field="wverbrauch" exp="" desc=""/>
    <constraint field="stdmittel" exp="" desc=""/>
    <constraint field="fremdwas" exp="" desc=""/>
    <constraint field="flaeche" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>2</layerGeometryType>
</qgis>
