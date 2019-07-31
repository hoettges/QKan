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
    <field name="bezeichnung">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="he_nr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mu_nr">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kp_nr">
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
    <alias field="pk" index="0" name=""/>
    <alias field="bezeichnung" index="1" name=""/>
    <alias field="he_nr" index="2" name=""/>
    <alias field="mu_nr" index="3" name=""/>
    <alias field="kp_nr" index="4" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="bezeichnung" expression=""/>
    <default applyOnUpdate="0" field="he_nr" expression=""/>
    <default applyOnUpdate="0" field="mu_nr" expression=""/>
    <default applyOnUpdate="0" field="kp_nr" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="bezeichnung" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="he_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="mu_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kp_nr" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="bezeichnung" exp="" desc=""/>
    <constraint field="he_nr" exp="" desc=""/>
    <constraint field="mu_nr" exp="" desc=""/>
    <constraint field="kp_nr" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>4</layerGeometryType>
</qgis>
