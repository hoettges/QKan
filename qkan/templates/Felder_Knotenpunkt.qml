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
    <field name="schnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="xsch">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ysch">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="sohlhoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="deckelhoehe">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="durchm">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="druckdicht">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="ueberstauflaeche">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="entwart">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option type="QString" name="AllowMulti" value="0"/>
            <Option type="QString" name="AllowNull" value="0"/>
            <Option type="QString" name="FilterExpression" value=""/>
            <Option type="QString" name="Key" value="bezeichnung"/>
            <Option type="QString" name="Layer" value="entwaesserungsarten20161018090806784"/>
            <Option type="QString" name="OrderByValue" value="0"/>
            <Option type="QString" name="UseCompleter" value="0"/>
            <Option type="QString" name="Value" value="bezeichnung"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="strasse">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
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
    <field name="knotentyp">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option type="Map" name="map">
              <Option type="QString" name="Anfangsschacht" value="Anfangsschacht"/>
              <Option type="QString" name="Einzelschacht" value="Einzelschacht"/>
              <Option type="QString" name="Endschacht" value="Endschacht"/>
              <Option type="QString" name="Hochpunkt" value="Hochpunkt"/>
              <Option type="QString" name="Normalschacht" value="Normalschacht"/>
              <Option type="QString" name="Tiefpunkt" value="Tiefpunkt"/>
              <Option type="QString" name="Verzweigung" value="Verzweigung"/>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="auslasstyp">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="schachttyp">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option type="Map" name="map">
              <Option type="QString" name="Auslass" value="Auslass"/>
              <Option type="QString" name="Schacht" value="Schacht"/>
              <Option type="QString" name="Speicher" value="Speicher"/>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="istspeicher">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" name="IsMultiline" value="0"/>
            <Option type="QString" name="UseHtml" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="istauslass">
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
            <Option type="QString" name="UseCompleter" value="0"/>
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
    <field name="geop">
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
    <alias field="schnam" index="1" name=""/>
    <alias field="xsch" index="2" name=""/>
    <alias field="ysch" index="3" name=""/>
    <alias field="sohlhoehe" index="4" name=""/>
    <alias field="deckelhoehe" index="5" name=""/>
    <alias field="durchm" index="6" name=""/>
    <alias field="druckdicht" index="7" name=""/>
    <alias field="ueberstauflaeche" index="8" name=""/>
    <alias field="entwart" index="9" name=""/>
    <alias field="strasse" index="10" name=""/>
    <alias field="teilgebiet" index="11" name=""/>
    <alias field="knotentyp" index="12" name=""/>
    <alias field="auslasstyp" index="13" name=""/>
    <alias field="schachttyp" index="14" name=""/>
    <alias field="istspeicher" index="15" name=""/>
    <alias field="istauslass" index="16" name=""/>
    <alias field="simstatus" index="17" name=""/>
    <alias field="kommentar" index="18" name=""/>
    <alias field="createdat" index="19" name=""/>
    <alias field="geop" index="20" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="pk" expression=""/>
    <default applyOnUpdate="0" field="schnam" expression=""/>
    <default applyOnUpdate="0" field="xsch" expression=""/>
    <default applyOnUpdate="0" field="ysch" expression=""/>
    <default applyOnUpdate="0" field="sohlhoehe" expression=""/>
    <default applyOnUpdate="0" field="deckelhoehe" expression=""/>
    <default applyOnUpdate="0" field="durchm" expression=""/>
    <default applyOnUpdate="0" field="druckdicht" expression=""/>
    <default applyOnUpdate="0" field="ueberstauflaeche" expression=""/>
    <default applyOnUpdate="0" field="entwart" expression=""/>
    <default applyOnUpdate="0" field="strasse" expression=""/>
    <default applyOnUpdate="0" field="teilgebiet" expression=""/>
    <default applyOnUpdate="0" field="knotentyp" expression="'Normalschacht'"/>
    <default applyOnUpdate="0" field="auslasstyp" expression=""/>
    <default applyOnUpdate="0" field="schachttyp" expression="'Schacht'"/>
    <default applyOnUpdate="0" field="istspeicher" expression=""/>
    <default applyOnUpdate="0" field="istauslass" expression=""/>
    <default applyOnUpdate="0" field="simstatus" expression="'vorhanden'"/>
    <default applyOnUpdate="0" field="kommentar" expression=""/>
    <default applyOnUpdate="0" field="createdat" expression="now()"/>
    <default applyOnUpdate="0" field="geop" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="pk" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="schnam" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="xsch" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="ysch" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="sohlhoehe" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="deckelhoehe" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="durchm" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="druckdicht" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="ueberstauflaeche" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="entwart" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="strasse" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="teilgebiet" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="knotentyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="auslasstyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="schachttyp" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="istspeicher" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="istauslass" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="simstatus" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="kommentar" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="createdat" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="geop" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="schnam" exp="" desc=""/>
    <constraint field="xsch" exp="" desc=""/>
    <constraint field="ysch" exp="" desc=""/>
    <constraint field="sohlhoehe" exp="" desc=""/>
    <constraint field="deckelhoehe" exp="" desc=""/>
    <constraint field="durchm" exp="" desc=""/>
    <constraint field="druckdicht" exp="" desc=""/>
    <constraint field="ueberstauflaeche" exp="" desc=""/>
    <constraint field="entwart" exp="" desc=""/>
    <constraint field="strasse" exp="" desc=""/>
    <constraint field="teilgebiet" exp="" desc=""/>
    <constraint field="knotentyp" exp="" desc=""/>
    <constraint field="auslasstyp" exp="" desc=""/>
    <constraint field="schachttyp" exp="" desc=""/>
    <constraint field="istspeicher" exp="" desc=""/>
    <constraint field="istauslass" exp="" desc=""/>
    <constraint field="simstatus" exp="" desc=""/>
    <constraint field="kommentar" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
    <constraint field="geop" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>2</layerGeometryType>
</qgis>
