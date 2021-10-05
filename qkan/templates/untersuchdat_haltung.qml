<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" labelsEnabled="1" simplifyDrawingTol="1" simplifyMaxScale="1" simplifyDrawingHints="1" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" styleCategories="Symbology|Labeling|Fields|Forms|Actions|AttributeTable|Rendering" minScale="100000000" version="3.16.5-Hannover" simplifyLocal="1">
  <renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0">
    <symbols>
      <symbol clip_to_extent="1" force_rhr="0" type="line" name="0" alpha="1">
        <layer locked="0" class="SimpleLine" enabled="1" pass="0">
          <prop v="0" k="align_dash_pattern"/>
          <prop v="square" k="capstyle"/>
          <prop v="5;2" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
          <prop v="0" k="dash_pattern_offset"/>
          <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
          <prop v="MM" k="dash_pattern_offset_unit"/>
          <prop v="0" k="draw_inside_polygon"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="255,127,0,255" k="line_color"/>
          <prop v="solid" k="line_style"/>
          <prop v="0.26" k="line_width"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="tweak_dash_pattern_on_corners"/>
          <prop v="0" k="use_custom_dash"/>
          <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" useSubstitutions="0" fontStrikeout="0" capitalization="0" previewBkgrdColor="255,255,255,255" fontSize="9" isExpression="1" fontWordSpacing="0" blendMode="0" fontItalic="0" textOpacity="1" fontKerning="1" fontWeight="50" fontFamily="MS Shell Dlg 2" allowHtml="0" textColor="0,0,0,255" fontSizeUnit="Point" fieldName="&quot;kuerzel&quot;+ ' '+if( &quot;charakt1&quot; &lt;> 'not found',&quot;charakt1&quot;,'') + ' '+ if( &quot;charakt2&quot; &lt;> 'not found',&quot;charakt2&quot;,'')" fontLetterSpacing="0" fontUnderline="0" multilineHeight="1" textOrientation="horizontal" namedStyle="Standard">
        <text-buffer bufferOpacity="1" bufferBlendMode="0" bufferColor="255,255,255,255" bufferSize="1" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1" bufferSizeUnits="MM" bufferDraw="0"/>
        <text-mask maskSizeUnits="MM" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskedSymbolLayers="" maskJoinStyle="128" maskType="0" maskSize="0" maskEnabled="0" maskOpacity="1"/>
        <background shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeRadiiUnit="MM" shapeDraw="0" shapeSizeType="0" shapeOffsetUnit="MM" shapeSVGFile="" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeOpacity="1" shapeOffsetX="0" shapeRadiiX="0" shapeRotation="0" shapeSizeY="0" shapeBlendMode="0" shapeRotationType="0" shapeOffsetY="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="0" shapeType="0" shapeBorderColor="128,128,128,255" shapeSizeUnit="MM" shapeRadiiY="0" shapeSizeX="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM">
          <symbol clip_to_extent="1" force_rhr="0" type="marker" name="markerSymbol" alpha="1">
            <layer locked="0" class="SimpleMarker" enabled="1" pass="0">
              <prop v="0" k="angle"/>
              <prop v="164,113,88,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="circle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="diameter" k="scale_method"/>
              <prop v="2" k="size"/>
              <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
              <prop v="MM" k="size_unit"/>
              <prop v="1" k="vertical_anchor_point"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetDist="1" shadowBlendMode="6" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowOpacity="0" shadowRadius="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowUnder="0" shadowDraw="0" shadowColor="0,0,0,255"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format leftDirectionSymbol="&lt;" useMaxLineLengthForAutoWrap="1" plussign="0" decimals="3" formatNumbers="0" wrapChar="" addDirectionSymbol="0" multilineAlign="0" rightDirectionSymbol=">" autoWrapLength="0" reverseDirectionSymbol="0" placeDirectionSymbol="0"/>
      <placement repeatDistanceUnits="MM" dist="0" preserveRotation="1" repeatDistance="0" centroidWhole="0" geometryGeneratorEnabled="0" distUnits="MM" rotationAngle="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" distMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="0" placement="2" xOffset="0" overrunDistanceUnit="MM" geometryGenerator="" geometryGeneratorType="PointGeometry" offsetUnits="MM" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" priority="5" quadOffset="4" polygonPlacementFlags="2" maxCurvedCharAngleIn="25" lineAnchorPercent="0" yOffset="0" offsetType="0" overrunDistance="0" layerType="LineGeometry" maxCurvedCharAngleOut="-25" fitInPolygonOnly="0" placementFlags="10" centroidInside="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0"/>
      <rendering fontLimitPixelSize="0" obstacle="1" labelPerPart="0" limitNumLabels="0" zIndex="0" obstacleType="1" fontMaxPixelSize="10000" obstacleFactor="1" scaleMin="1" fontMinPixelSize="3" displayAll="0" upsidedownLabels="0" maxNumLabels="2000" mergeLines="0" scaleMax="2500" minFeatureSize="0" drawLabels="1" scaleVisibility="1"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" value="" name="name"/>
          <Option name="properties"/>
          <Option type="QString" value="collection" name="type"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
          <Option type="bool" value="false" name="drawToAllParts"/>
          <Option type="QString" value="0" name="enabled"/>
          <Option type="QString" value="point_on_exterior" name="labelAnchorPoint"/>
          <Option type="QString" value="&lt;symbol clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; name=&quot;symbol&quot; alpha=&quot;1&quot;>&lt;layer locked=&quot;0&quot; class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
          <Option type="double" value="0" name="minLength"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale"/>
          <Option type="QString" value="MM" name="minLengthUnit"/>
          <Option type="double" value="0" name="offsetFromAnchor"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale"/>
          <Option type="QString" value="MM" name="offsetFromAnchorUnit"/>
          <Option type="double" value="0" name="offsetFromLabel"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale"/>
          <Option type="QString" value="MM" name="offsetFromLabelUnit"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <fieldConfiguration>
    <field configurationFlags="None" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="untersuchhal">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="untersuchrichtung">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="schoben">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="schunten">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="videozaehler">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="inspektionslaenge">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="station">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="timecode">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="video_offset">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kuerzel">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="charakt1">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="charakt2">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="quantnr1">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="quantnr2">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="streckenschaden">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="streckenschaden_lfdnr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="pos_von">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="pos_bis">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="foto_dateiname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="film_dateiname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="ordner_bild">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="ordner_video">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="richtung">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="bool" value="true" name="allow_null"/>
            <Option type="bool" value="true" name="calendar_popup"/>
            <Option type="QString" value="dd.MM.yyyy HH:mm" name="display_format"/>
            <Option type="QString" value="dd.MM.yyyy HH:mm" name="field_format"/>
            <Option type="bool" value="false" name="field_iso_format"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pk" name="" index="0"/>
    <alias field="untersuchhal" name="" index="1"/>
    <alias field="untersuchrichtung" name="" index="2"/>
    <alias field="schoben" name="" index="3"/>
    <alias field="schunten" name="" index="4"/>
    <alias field="id" name="" index="5"/>
    <alias field="videozaehler" name="" index="6"/>
    <alias field="inspektionslaenge" name="" index="7"/>
    <alias field="station" name="" index="8"/>
    <alias field="timecode" name="" index="9"/>
    <alias field="video_offset" name="" index="10"/>
    <alias field="kuerzel" name="" index="11"/>
    <alias field="charakt1" name="" index="12"/>
    <alias field="charakt2" name="" index="13"/>
    <alias field="quantnr1" name="" index="14"/>
    <alias field="quantnr2" name="" index="15"/>
    <alias field="streckenschaden" name="" index="16"/>
    <alias field="streckenschaden_lfdnr" name="" index="17"/>
    <alias field="pos_von" name="" index="18"/>
    <alias field="pos_bis" name="" index="19"/>
    <alias field="foto_dateiname" name="" index="20"/>
    <alias field="film_dateiname" name="" index="21"/>
    <alias field="ordner_bild" name="" index="22"/>
    <alias field="ordner_video" name="" index="23"/>
    <alias field="richtung" name="" index="24"/>
    <alias field="createdat" name="" index="25"/>
  </aliases>
  <defaults>
    <default field="pk" applyOnUpdate="0" expression=""/>
    <default field="untersuchhal" applyOnUpdate="0" expression=""/>
    <default field="untersuchrichtung" applyOnUpdate="0" expression=""/>
    <default field="schoben" applyOnUpdate="0" expression=""/>
    <default field="schunten" applyOnUpdate="0" expression=""/>
    <default field="id" applyOnUpdate="0" expression=""/>
    <default field="videozaehler" applyOnUpdate="0" expression=""/>
    <default field="inspektionslaenge" applyOnUpdate="0" expression=""/>
    <default field="station" applyOnUpdate="0" expression=""/>
    <default field="timecode" applyOnUpdate="0" expression=""/>
    <default field="video_offset" applyOnUpdate="0" expression=""/>
    <default field="kuerzel" applyOnUpdate="0" expression=""/>
    <default field="charakt1" applyOnUpdate="0" expression=""/>
    <default field="charakt2" applyOnUpdate="0" expression=""/>
    <default field="quantnr1" applyOnUpdate="0" expression=""/>
    <default field="quantnr2" applyOnUpdate="0" expression=""/>
    <default field="streckenschaden" applyOnUpdate="0" expression=""/>
    <default field="streckenschaden_lfdnr" applyOnUpdate="0" expression=""/>
    <default field="pos_von" applyOnUpdate="0" expression=""/>
    <default field="pos_bis" applyOnUpdate="0" expression=""/>
    <default field="foto_dateiname" applyOnUpdate="0" expression=""/>
    <default field="film_dateiname" applyOnUpdate="0" expression=""/>
    <default field="ordner_bild" applyOnUpdate="0" expression=""/>
    <default field="ordner_video" applyOnUpdate="0" expression=""/>
    <default field="richtung" applyOnUpdate="0" expression=""/>
    <default field="createdat" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint field="pk" exp_strength="0" unique_strength="1" notnull_strength="1" constraints="3"/>
    <constraint field="untersuchhal" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="untersuchrichtung" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="schoben" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="schunten" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="id" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="videozaehler" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="inspektionslaenge" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="station" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="timecode" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="video_offset" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="kuerzel" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="charakt1" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="charakt2" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="quantnr1" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="quantnr2" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="streckenschaden" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="streckenschaden_lfdnr" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="pos_von" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="pos_bis" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="foto_dateiname" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="film_dateiname" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="ordner_bild" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="ordner_video" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="richtung" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
    <constraint field="createdat" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" exp="" desc=""/>
    <constraint field="untersuchhal" exp="" desc=""/>
    <constraint field="untersuchrichtung" exp="" desc=""/>
    <constraint field="schoben" exp="" desc=""/>
    <constraint field="schunten" exp="" desc=""/>
    <constraint field="id" exp="" desc=""/>
    <constraint field="videozaehler" exp="" desc=""/>
    <constraint field="inspektionslaenge" exp="" desc=""/>
    <constraint field="station" exp="" desc=""/>
    <constraint field="timecode" exp="" desc=""/>
    <constraint field="video_offset" exp="" desc=""/>
    <constraint field="kuerzel" exp="" desc=""/>
    <constraint field="charakt1" exp="" desc=""/>
    <constraint field="charakt2" exp="" desc=""/>
    <constraint field="quantnr1" exp="" desc=""/>
    <constraint field="quantnr2" exp="" desc=""/>
    <constraint field="streckenschaden" exp="" desc=""/>
    <constraint field="streckenschaden_lfdnr" exp="" desc=""/>
    <constraint field="pos_von" exp="" desc=""/>
    <constraint field="pos_bis" exp="" desc=""/>
    <constraint field="foto_dateiname" exp="" desc=""/>
    <constraint field="film_dateiname" exp="" desc=""/>
    <constraint field="ordner_bild" exp="" desc=""/>
    <constraint field="ordner_video" exp="" desc=""/>
    <constraint field="richtung" exp="" desc=""/>
    <constraint field="createdat" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{11dbd1d6-2c4a-42fe-a25f-d736a63d844a}"/>
    <actionsetting icon="" action="[%ordner_bild %]/[%'Band'+substr(foto_dateiname,0,5)%]/[%foto_dateiname%]" capture="0" notificationMessage="" id="{69f0cd70-8fe8-47d9-80db-3115173291ef}" type="5" name="Bild öffnen" shortTitle="Bild öffnen" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting icon="" action="from qgis.utils import iface&#xd;&#xa;from qgis.core import *&#xd;&#xa;from qgis.gui import QgsMessageBar&#xd;&#xa;#iface.messageBar().pushMessage(&quot;Error&quot;, str([%video_offset%]), level=Qgis.Critical)&#xa;try:&#xa;    from qkan.tools.videoplayer import Videoplayer&#xd;&#xa;    if [%video_offset%] == 0:&#xd;&#xa;        iface.messageBar().pushMessage(&quot;Error&quot;, &quot;Video offset = 0.00 s, bitte in der Attributtabelle prüfen!&quot;, level=Qgis.Critical)&#xd;&#xa;    y=QgsProject.instance().readPath(&quot;./&quot;)&#xa;    video='[%ordner_video%]'+'/'+'[%film_dateiname%]'&#xa;    timecode=[%timecode%]&#xa;    time_h=int(timecode/1000000) if timecode>1000000 else 0&#xa;    time_m=(int(timecode/10000) if timecode>10000 else 0 )-(time_h*100)&#xa;    time_s=(int(timecode/100) if timecode>100 else 0 )-(time_h*10000)-(time_m*100)&#xa;&#xa;    time = float(time_h/3600+time_m/60+time_s+[%video_offset%])&#xa;    window = Videoplayer(video=video, time=time)&#xa;    window.show()&#xa;    window.open_file()&#xa;    window.exec_()&#xa;        &#xa;except ImportError:&#xa;    raise Exception(&#xa;        &quot;The QKan main plugin has to be installed for this to work.&quot;&#xa;     )&#xa;" capture="0" notificationMessage="" id="{ceea4ddf-279c-4e33-8743-0ed569aa1b20}" type="1" name="Video abspielen" shortTitle="" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;video_offset&quot;" actionWidgetStyle="dropDown" sortOrder="1">
    <columns>
      <column hidden="0" type="field" name="pk" width="-1"/>
      <column hidden="0" type="field" name="untersuchhal" width="-1"/>
      <column hidden="0" type="field" name="untersuchrichtung" width="-1"/>
      <column hidden="0" type="field" name="schoben" width="-1"/>
      <column hidden="0" type="field" name="schunten" width="-1"/>
      <column hidden="0" type="field" name="id" width="-1"/>
      <column hidden="0" type="field" name="videozaehler" width="-1"/>
      <column hidden="0" type="field" name="inspektionslaenge" width="-1"/>
      <column hidden="0" type="field" name="station" width="-1"/>
      <column hidden="0" type="field" name="timecode" width="-1"/>
      <column hidden="0" type="field" name="kuerzel" width="-1"/>
      <column hidden="0" type="field" name="charakt1" width="-1"/>
      <column hidden="0" type="field" name="charakt2" width="-1"/>
      <column hidden="0" type="field" name="quantnr1" width="-1"/>
      <column hidden="0" type="field" name="quantnr2" width="-1"/>
      <column hidden="0" type="field" name="streckenschaden" width="-1"/>
      <column hidden="0" type="field" name="pos_von" width="-1"/>
      <column hidden="0" type="field" name="pos_bis" width="-1"/>
      <column hidden="0" type="field" name="foto_dateiname" width="-1"/>
      <column hidden="0" type="field" name="film_dateiname" width="410"/>
      <column hidden="0" type="field" name="ordner_bild" width="274"/>
      <column hidden="0" type="field" name="ordner_video" width="482"/>
      <column hidden="0" type="field" name="richtung" width="-1"/>
      <column hidden="1" type="actions" width="-1"/>
      <column hidden="0" type="field" name="video_offset" width="-1"/>
      <column hidden="0" type="field" name="streckenschaden_lfdnr" width="-1"/>
      <column hidden="0" type="field" name="createdat" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/Nora/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/untersuchdat_haltung.ui</editform>
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
    <field name="charakt1" editable="1"/>
    <field name="charakt2" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="film_dateiname" editable="1"/>
    <field name="foto_dateiname" editable="1"/>
    <field name="id" editable="1"/>
    <field name="inspektionslaenge" editable="1"/>
    <field name="kuerzel" editable="1"/>
    <field name="ordner_bild" editable="1"/>
    <field name="ordner_video" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="pos_bis" editable="1"/>
    <field name="pos_von" editable="1"/>
    <field name="quantnr1" editable="1"/>
    <field name="quantnr2" editable="1"/>
    <field name="richtung" editable="1"/>
    <field name="schoben" editable="1"/>
    <field name="schunten" editable="1"/>
    <field name="station" editable="1"/>
    <field name="streckenschaden" editable="1"/>
    <field name="streckenschaden_lfdnr" editable="1"/>
    <field name="timecode" editable="1"/>
    <field name="untersuchhal" editable="1"/>
    <field name="untersuchrichtung" editable="1"/>
    <field name="video_offset" editable="1"/>
    <field name="videozaehler" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="charakt1" labelOnTop="0"/>
    <field name="charakt2" labelOnTop="0"/>
    <field name="createdat" labelOnTop="0"/>
    <field name="film_dateiname" labelOnTop="0"/>
    <field name="foto_dateiname" labelOnTop="0"/>
    <field name="id" labelOnTop="0"/>
    <field name="inspektionslaenge" labelOnTop="0"/>
    <field name="kuerzel" labelOnTop="0"/>
    <field name="ordner_bild" labelOnTop="0"/>
    <field name="ordner_video" labelOnTop="0"/>
    <field name="pk" labelOnTop="0"/>
    <field name="pos_bis" labelOnTop="0"/>
    <field name="pos_von" labelOnTop="0"/>
    <field name="quantnr1" labelOnTop="0"/>
    <field name="quantnr2" labelOnTop="0"/>
    <field name="richtung" labelOnTop="0"/>
    <field name="schoben" labelOnTop="0"/>
    <field name="schunten" labelOnTop="0"/>
    <field name="station" labelOnTop="0"/>
    <field name="streckenschaden" labelOnTop="0"/>
    <field name="streckenschaden_lfdnr" labelOnTop="0"/>
    <field name="timecode" labelOnTop="0"/>
    <field name="untersuchhal" labelOnTop="0"/>
    <field name="untersuchrichtung" labelOnTop="0"/>
    <field name="video_offset" labelOnTop="0"/>
    <field name="videozaehler" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
