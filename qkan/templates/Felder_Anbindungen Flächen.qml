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
    <field name="flnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="haltnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="0"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="haltnam"/>
            <Option type="QString" name="Layer" value="haltungen20161016203756230"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="0"/>
            <Option type="QString" name="Value" value="haltnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="tezgnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="1"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="flnam"/>
            <Option type="QString" name="Layer" value="tezg20171204105753202"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="0"/>
            <Option type="QString" name="Value" value="flnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="teilgebiet">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="0"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="tgnam"/>
            <Option type="QString" name="Layer" value="teilgebiete20170214092005309"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="0"/>
            <Option type="QString" name="Value" value="tgnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="abflusstyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="speicherzahl">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="speicherkonst">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="fliesszeitkanal">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="fliesszeitflaeche">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="geom">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="gbuf">
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
    <alias field="flnam" index="1" name=""/>
    <alias field="haltnam" index="2" name=""/>
    <alias field="tezgnam" index="3" name=""/>
    <alias field="teilgebiet" index="4" name=""/>
    <alias field="abflusstyp" index="5" name=""/>
    <alias field="speicherzahl" index="6" name=""/>
    <alias field="speicherkonst" index="7" name=""/>
    <alias field="fliesszeitkanal" index="8" name=""/>
    <alias field="fliesszeitflaeche" index="9" name=""/>
    <alias field="geom" index="10" name=""/>
    <alias field="gbuf" index="11" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="flnam" expression=""/>
    <default applyOnUpdate="0" field="haltnam" expression=""/>
    <default applyOnUpdate="0" field="tezgnam" expression=""/>
    <default applyOnUpdate="0" field="teilgebiet" expression=""/>
    <default applyOnUpdate="0" field="abflusstyp" expression=""/>
    <default applyOnUpdate="0" field="speicherzahl" expression=""/>
    <default applyOnUpdate="0" field="speicherkonst" expression=""/>
    <default applyOnUpdate="0" field="fliesszeitkanal" expression=""/>
    <default applyOnUpdate="0" field="fliesszeitflaeche" expression=""/>
    <default applyOnUpdate="0" field="geom" expression=""/>
    <default applyOnUpdate="0" field="gbuf" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="flnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="haltnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="tezgnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="teilgebiet" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="abflusstyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="speicherzahl" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="speicherkonst" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="fliesszeitkanal" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="fliesszeitflaeche" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="geom" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="gbuf" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="flnam" exp="" desc=""/>
    <constraint field="haltnam" exp="" desc=""/>
    <constraint field="tezgnam" exp="" desc=""/>
    <constraint field="teilgebiet" exp="" desc=""/>
    <constraint field="abflusstyp" exp="" desc=""/>
    <constraint field="speicherzahl" exp="" desc=""/>
    <constraint field="speicherkonst" exp="" desc=""/>
    <constraint field="fliesszeitkanal" exp="" desc=""/>
    <constraint field="fliesszeitflaeche" exp="" desc=""/>
    <constraint field="geom" exp="" desc=""/>
    <constraint field="gbuf" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
