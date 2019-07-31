<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Fields" version="3.6.3-Noosa">
  <fieldConfiguration>
    <field name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="pnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schoben">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schunten">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="pumpentyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="volanf">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="volges">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohle">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="steuersch">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="bool" name="AllowMulti" value="false"/>
            <Option type="bool" name="AllowNull" value="false"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="schnam"/>
            <Option type="QString" name="Layer" value="schaechte20161016203756252"/>
            <Option type="int" name="NofColumns" value="1"/>
            <Option type="bool" name="OrderByValue" value="false"/>
            <Option type="bool" name="UseCompleter" value="false"/>
            <Option type="QString" name="Value" value="schnam"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="einschalthoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ausschalthoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="simstatus">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" name="IsMultiline" value="false"/>
            <Option type="bool" name="UseHtml" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="bool" name="allow_null" value="true"/>
            <Option type="bool" name="calendar_popup" value="true"/>
            <Option type="QString" name="display_format" value="dd.MM.yyyy HH:mm"/>
            <Option type="QString" name="field_format" value="dd.MM.yyyy HH:mm"/>
            <Option type="bool" name="field_iso_format" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" index="0" name=""/>
    <alias field="pnam" index="1" name=""/>
    <alias field="schoben" index="2" name=""/>
    <alias field="schunten" index="3" name=""/>
    <alias field="pumpentyp" index="4" name=""/>
    <alias field="volanf" index="5" name=""/>
    <alias field="volges" index="6" name=""/>
    <alias field="sohle" index="7" name=""/>
    <alias field="steuersch" index="8" name=""/>
    <alias field="einschalthoehe" index="9" name=""/>
    <alias field="ausschalthoehe" index="10" name=""/>
    <alias field="simstatus" index="11" name=""/>
    <alias field="kommentar" index="12" name=""/>
    <alias field="createdat" index="13" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="pnam" expression=""/>
    <default applyOnUpdate="0" field="schoben" expression=""/>
    <default applyOnUpdate="0" field="schunten" expression=""/>
    <default applyOnUpdate="0" field="pumpentyp" expression=""/>
    <default applyOnUpdate="0" field="volanf" expression=""/>
    <default applyOnUpdate="0" field="volges" expression=""/>
    <default applyOnUpdate="0" field="sohle" expression=""/>
    <default applyOnUpdate="0" field="steuersch" expression=""/>
    <default applyOnUpdate="0" field="einschalthoehe" expression=""/>
    <default applyOnUpdate="0" field="ausschalthoehe" expression=""/>
    <default applyOnUpdate="0" field="simstatus" expression="'vorhanden'"/>
    <default applyOnUpdate="0" field="kommentar" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression="now()"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="pnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="schoben" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="schunten" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="pumpentyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="volanf" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="volges" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="sohle" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="steuersch" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="einschalthoehe" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="ausschalthoehe" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="simstatus" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="pnam" exp="" desc=""/>
    <constraint field="schoben" exp="" desc=""/>
    <constraint field="schunten" exp="" desc=""/>
    <constraint field="pumpentyp" exp="" desc=""/>
    <constraint field="volanf" exp="" desc=""/>
    <constraint field="volges" exp="" desc=""/>
    <constraint field="sohle" exp="" desc=""/>
    <constraint field="steuersch" exp="" desc=""/>
    <constraint field="einschalthoehe" exp="" desc=""/>
    <constraint field="ausschalthoehe" exp="" desc=""/>
    <constraint field="simstatus" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
