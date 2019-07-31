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
    <field name="wnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schoben">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="0"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="schnam"/>
            <Option type="QString" name="Layer" value="schaechte20161016203756252"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schunten">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="0"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="schnam"/>
            <Option type="QString" name="Layer" value="schaechte20161016203756252"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="wehrtyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schwellenhoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kammerhoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="laenge">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="uebeiwert">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="aussentyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="aussenwsp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="simstatus">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="0"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="bezeichnung"/>
            <Option type="QString" name="Layer" value="simulationsstatus20161201095050780"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="1"/>
            <Option type="QString" name="Value" value="bezeichnung"/>
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
    <alias field="wnam" index="1" name=""/>
    <alias field="schoben" index="2" name=""/>
    <alias field="schunten" index="3" name=""/>
    <alias field="wehrtyp" index="4" name=""/>
    <alias field="schwellenhoehe" index="5" name=""/>
    <alias field="kammerhoehe" index="6" name=""/>
    <alias field="laenge" index="7" name=""/>
    <alias field="uebeiwert" index="8" name=""/>
    <alias field="aussentyp" index="9" name=""/>
    <alias field="aussenwsp" index="10" name=""/>
    <alias field="simstatus" index="11" name=""/>
    <alias field="kommentar" index="12" name=""/>
    <alias field="createdat" index="13" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="wnam" expression=""/>
    <default applyOnUpdate="0" field="schoben" expression=""/>
    <default applyOnUpdate="0" field="schunten" expression=""/>
    <default applyOnUpdate="0" field="wehrtyp" expression=""/>
    <default applyOnUpdate="0" field="schwellenhoehe" expression=""/>
    <default applyOnUpdate="0" field="kammerhoehe" expression=""/>
    <default applyOnUpdate="0" field="laenge" expression=""/>
    <default applyOnUpdate="0" field="uebeiwert" expression=""/>
    <default applyOnUpdate="0" field="aussentyp" expression=""/>
    <default applyOnUpdate="0" field="aussenwsp" expression=""/>
    <default applyOnUpdate="0" field="simstatus" expression="'vorhanden'"/>
    <default applyOnUpdate="0" field="kommentar" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression="now()"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="wnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="schoben" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="schunten" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="wehrtyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="schwellenhoehe" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kammerhoehe" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="laenge" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="uebeiwert" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="aussentyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="aussenwsp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="simstatus" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="wnam" exp="" desc=""/>
    <constraint field="schoben" exp="" desc=""/>
    <constraint field="schunten" exp="" desc=""/>
    <constraint field="wehrtyp" exp="" desc=""/>
    <constraint field="schwellenhoehe" exp="" desc=""/>
    <constraint field="kammerhoehe" exp="" desc=""/>
    <constraint field="laenge" exp="" desc=""/>
    <constraint field="uebeiwert" exp="" desc=""/>
    <constraint field="aussentyp" exp="" desc=""/>
    <constraint field="aussenwsp" exp="" desc=""/>
    <constraint field="simstatus" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
