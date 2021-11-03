<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" hasScaleBasedVisibilityFlag="0" labelsEnabled="1" simplifyMaxScale="1" simplifyAlgorithm="0" simplifyLocal="1" styleCategories="Symbology|Labeling|Fields|Forms|Actions|AttributeTable|Rendering" simplifyDrawingHints="1" version="3.16.5-Hannover" maxScale="0" minScale="100000000">
  <renderer-v2 symbollevels="0" forceraster="0" enableorderby="0" type="singleSymbol">
    <symbols>
      <symbol clip_to_extent="1" name="0" alpha="1" force_rhr="0" type="line">
        <layer enabled="1" class="SimpleLine" pass="0" locked="0">
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
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
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
      <text-style multilineHeight="1" fontStrikeout="0" fieldName="&quot;kuerzel&quot;+ ' '+if( &quot;charakt1&quot; &lt;> 'not found',&quot;charakt1&quot;,'') + ' '+ if( &quot;charakt2&quot; &lt;> 'not found',&quot;charakt2&quot;,'')" textOrientation="horizontal" isExpression="1" textColor="0,0,0,255" fontLetterSpacing="0" fontSizeUnit="Point" fontUnderline="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" useSubstitutions="0" textOpacity="1" allowHtml="0" capitalization="0" fontKerning="1" fontWeight="50" blendMode="0" fontFamily="MS Shell Dlg 2" fontSize="9" namedStyle="Standard" previewBkgrdColor="255,255,255,255" fontWordSpacing="0" fontItalic="0">
        <text-buffer bufferSize="1" bufferJoinStyle="128" bufferDraw="0" bufferNoFill="1" bufferOpacity="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="255,255,255,255"/>
        <text-mask maskedSymbolLayers="" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskSize="0" maskSizeUnits="MM" maskEnabled="0" maskType="0" maskJoinStyle="128"/>
        <background shapeSizeY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeRotation="0" shapeSizeType="0" shapeOffsetUnit="MM" shapeJoinStyle="64" shapeRotationType="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeOffsetX="0" shapeSVGFile="" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeFillColor="255,255,255,255" shapeType="0" shapeDraw="0" shapeBorderColor="128,128,128,255" shapeOpacity="1" shapeRadiiX="0" shapeOffsetY="0" shapeBorderWidthUnit="MM" shapeSizeUnit="MM">
          <symbol clip_to_extent="1" name="markerSymbol" alpha="1" force_rhr="0" type="marker">
            <layer enabled="1" class="SimpleMarker" pass="0" locked="0">
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowOffsetDist="1" shadowRadiusUnit="MM" shadowOffsetAngle="135" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM" shadowOffsetGlobal="1" shadowOpacity="0" shadowRadiusAlphaOnly="0" shadowRadius="0" shadowDraw="0" shadowColor="0,0,0,255" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowBlendMode="6" shadowUnder="0"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format addDirectionSymbol="0" decimals="3" formatNumbers="0" plussign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" placeDirectionSymbol="0" rightDirectionSymbol=">" reverseDirectionSymbol="0" wrapChar=""/>
      <placement repeatDistanceUnits="MM" quadOffset="4" placement="2" geometryGenerator="" repeatDistance="0" dist="0" maxCurvedCharAngleIn="25" polygonPlacementFlags="2" offsetUnits="MM" centroidWhole="0" preserveRotation="1" rotationAngle="0" priority="5" centroidInside="0" overrunDistanceUnit="MM" fitInPolygonOnly="0" xOffset="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" lineAnchorType="0" distUnits="MM" layerType="LineGeometry" placementFlags="10" geometryGeneratorEnabled="0" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorType="PointGeometry" overrunDistance="0" lineAnchorPercent="0" maxCurvedCharAngleOut="-25" yOffset="0"/>
      <rendering minFeatureSize="0" scaleMax="2500" obstacleType="1" fontLimitPixelSize="0" fontMinPixelSize="3" drawLabels="1" scaleVisibility="1" obstacleFactor="1" upsidedownLabels="0" obstacle="1" fontMaxPixelSize="10000" mergeLines="0" labelPerPart="0" scaleMin="1" displayAll="0" maxNumLabels="2000" zIndex="0" limitNumLabels="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
          <Option name="ddProperties" type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
          <Option value="false" name="drawToAllParts" type="bool"/>
          <Option value="0" name="enabled" type="QString"/>
          <Option value="point_on_exterior" name="labelAnchorPoint" type="QString"/>
          <Option value="&lt;symbol clip_to_extent=&quot;1&quot; name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot;>&lt;layer enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
          <Option value="0" name="minLength" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
          <Option value="MM" name="minLengthUnit" type="QString"/>
          <Option value="0" name="offsetFromAnchor" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
          <Option value="0" name="offsetFromLabel" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
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
          <Option/>
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
    <alias field="kuerzel" name="" index="10"/>
    <alias field="charakt1" name="" index="11"/>
    <alias field="charakt2" name="" index="12"/>
    <alias field="quantnr1" name="" index="13"/>
    <alias field="quantnr2" name="" index="14"/>
    <alias field="streckenschaden" name="" index="15"/>
    <alias field="pos_von" name="" index="16"/>
    <alias field="pos_bis" name="" index="17"/>
    <alias field="foto_dateiname" name="" index="18"/>
    <alias field="film_dateiname" name="" index="19"/>
    <alias field="ordner_bild" name="" index="20"/>
    <alias field="ordner_video" name="" index="21"/>
    <alias field="richtung" name="" index="22"/>
  </aliases>
  <defaults>
    <default field="pk" expression="" applyOnUpdate="0"/>
    <default field="untersuchhal" expression="" applyOnUpdate="0"/>
    <default field="untersuchrichtung" expression="" applyOnUpdate="0"/>
    <default field="schoben" expression="" applyOnUpdate="0"/>
    <default field="schunten" expression="" applyOnUpdate="0"/>
    <default field="id" expression="" applyOnUpdate="0"/>
    <default field="videozaehler" expression="" applyOnUpdate="0"/>
    <default field="inspektionslaenge" expression="" applyOnUpdate="0"/>
    <default field="station" expression="" applyOnUpdate="0"/>
    <default field="timecode" expression="" applyOnUpdate="0"/>
    <default field="kuerzel" expression="" applyOnUpdate="0"/>
    <default field="charakt1" expression="" applyOnUpdate="0"/>
    <default field="charakt2" expression="" applyOnUpdate="0"/>
    <default field="quantnr1" expression="" applyOnUpdate="0"/>
    <default field="quantnr2" expression="" applyOnUpdate="0"/>
    <default field="streckenschaden" expression="" applyOnUpdate="0"/>
    <default field="pos_von" expression="" applyOnUpdate="0"/>
    <default field="pos_bis" expression="" applyOnUpdate="0"/>
    <default field="foto_dateiname" expression="" applyOnUpdate="0"/>
    <default field="film_dateiname" expression="" applyOnUpdate="0"/>
    <default field="ordner_bild" expression="" applyOnUpdate="0"/>
    <default field="ordner_video" expression="" applyOnUpdate="0"/>
    <default field="richtung" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="pk" constraints="3" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint field="untersuchhal" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="untersuchrichtung" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="schoben" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="schunten" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="id" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="videozaehler" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="inspektionslaenge" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="station" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="timecode" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="kuerzel" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="charakt1" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="charakt2" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="quantnr1" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="quantnr2" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="streckenschaden" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="pos_von" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="pos_bis" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="foto_dateiname" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="film_dateiname" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="ordner_bild" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="ordner_video" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="richtung" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pk" desc="" exp=""/>
    <constraint field="untersuchhal" desc="" exp=""/>
    <constraint field="untersuchrichtung" desc="" exp=""/>
    <constraint field="schoben" desc="" exp=""/>
    <constraint field="schunten" desc="" exp=""/>
    <constraint field="id" desc="" exp=""/>
    <constraint field="videozaehler" desc="" exp=""/>
    <constraint field="inspektionslaenge" desc="" exp=""/>
    <constraint field="station" desc="" exp=""/>
    <constraint field="timecode" desc="" exp=""/>
    <constraint field="kuerzel" desc="" exp=""/>
    <constraint field="charakt1" desc="" exp=""/>
    <constraint field="charakt2" desc="" exp=""/>
    <constraint field="quantnr1" desc="" exp=""/>
    <constraint field="quantnr2" desc="" exp=""/>
    <constraint field="streckenschaden" desc="" exp=""/>
    <constraint field="pos_von" desc="" exp=""/>
    <constraint field="pos_bis" desc="" exp=""/>
    <constraint field="foto_dateiname" desc="" exp=""/>
    <constraint field="film_dateiname" desc="" exp=""/>
    <constraint field="ordner_bild" desc="" exp=""/>
    <constraint field="ordner_video" desc="" exp=""/>
    <constraint field="richtung" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
    <actionsetting id="{32cc3ef8-bf98-491c-b858-fd503a299ecf}" action="[%ordner_bild %]/[%'Band'+substr(foto_dateiname,0,5)%]/[%foto_dateiname%]" name="Bild öffnen" shortTitle="Bild öffnen" icon="" capture="0" type="5" notificationMessage="" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting id="{929e78c5-1679-42ff-9495-01ed9fd59e44}" action="from qgis.core import Qgis&#xd;&#xa;try:&#xd;&#xa;    #if offset== NULL:&#xd;&#xa;     #   iface.messageBar().pushMessage(&quot;Error&quot;, &quot;Video offset[s] in der Attributtabelle ergänzen!&quot;, level=Qgis.Critical)&#xd;&#xa;    from qkan.tools.videoplayer import Videoplayer&#xd;&#xa;    #window = Videoplayer(video=[%ordner_video+'/'+film_dateiname%],foto_path=[%ordner_bild%]+'/'+bild+'.jpg')&#xd;&#xa;    #window = Videoplayer(video=y+'/'+'0175050805 von 4567918 nach 4567919 - Gruissem.mpg',foto_path=y+'/'+bild+'.jpg')&#xd;&#xa;    y=QgsProject.instance().readPath(&quot;./&quot;)&#xd;&#xa;    video='[%ordner_video%]'+'/'+'0175050805 von 4567918 nach 4567919 - Gruissem.mpg'&#xd;&#xa;    timecode=[%timecode%]&#xd;&#xa;    time_h=int(timecode/1000000) if timecode>1000000 else 0&#xd;&#xa;    time_m=(int(timecode/10000) if timecode>10000 else 0 )-(time_h*100)&#xd;&#xa;    time_s=(int(timecode/100) if timecode>100 else 0 )-(time_h*10000)-(time_m*100)&#xd;&#xa;&#xd;&#xa;    time = float(time_h/3600+time_m/60+time_s)&#xd;&#xa;    window = Videoplayer(video=video, time=time)&#xd;&#xa;    window.show()&#xd;&#xa;    window.open_file()&#xd;&#xa;    window.exec_()&#xd;&#xa;    &#xd;&#xa;except ImportError:&#xd;&#xa;    raise Exception(&#xd;&#xa;        &quot;The QKan main plugin has to be installed for this to work.&quot;&#xd;&#xa;     )&#xd;&#xa;" name="Video abspielen" shortTitle="" icon="" capture="0" type="1" notificationMessage="" isEnabledOnlyWhenEditable="0">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig sortOrder="1" actionWidgetStyle="dropDown" sortExpression="&quot;videozaehler&quot;">
    <columns>
      <column name="pk" type="field" hidden="0" width="-1"/>
      <column name="untersuchhal" type="field" hidden="0" width="-1"/>
      <column name="untersuchrichtung" type="field" hidden="0" width="-1"/>
      <column name="schoben" type="field" hidden="0" width="-1"/>
      <column name="schunten" type="field" hidden="0" width="-1"/>
      <column name="id" type="field" hidden="0" width="-1"/>
      <column name="videozaehler" type="field" hidden="0" width="-1"/>
      <column name="inspektionslaenge" type="field" hidden="0" width="-1"/>
      <column name="station" type="field" hidden="0" width="-1"/>
      <column name="timecode" type="field" hidden="0" width="-1"/>
      <column name="kuerzel" type="field" hidden="0" width="-1"/>
      <column name="charakt1" type="field" hidden="0" width="-1"/>
      <column name="charakt2" type="field" hidden="0" width="-1"/>
      <column name="quantnr1" type="field" hidden="0" width="-1"/>
      <column name="quantnr2" type="field" hidden="0" width="-1"/>
      <column name="streckenschaden" type="field" hidden="0" width="-1"/>
      <column name="pos_von" type="field" hidden="0" width="-1"/>
      <column name="pos_bis" type="field" hidden="0" width="-1"/>
      <column name="foto_dateiname" type="field" hidden="0" width="-1"/>
      <column name="film_dateiname" type="field" hidden="0" width="410"/>
      <column name="ordner_bild" type="field" hidden="0" width="-1"/>
      <column name="ordner_video" type="field" hidden="0" width="310"/>
      <column name="richtung" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
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
    <field editable="1" name="charakt1"/>
    <field editable="1" name="charakt2"/>
    <field editable="1" name="film_dateiname"/>
    <field editable="1" name="foto_dateiname"/>
    <field editable="1" name="id"/>
    <field editable="1" name="inspektionslaenge"/>
    <field editable="1" name="kuerzel"/>
    <field editable="1" name="ordner_bild"/>
    <field editable="1" name="ordner_video"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="pos_bis"/>
    <field editable="1" name="pos_von"/>
    <field editable="1" name="quantnr1"/>
    <field editable="1" name="quantnr2"/>
    <field editable="1" name="richtung"/>
    <field editable="1" name="schoben"/>
    <field editable="1" name="schunten"/>
    <field editable="1" name="station"/>
    <field editable="1" name="streckenschaden"/>
    <field editable="1" name="timecode"/>
    <field editable="1" name="untersuchhal"/>
    <field editable="1" name="untersuchrichtung"/>
    <field editable="1" name="videozaehler"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="charakt1"/>
    <field labelOnTop="0" name="charakt2"/>
    <field labelOnTop="0" name="film_dateiname"/>
    <field labelOnTop="0" name="foto_dateiname"/>
    <field labelOnTop="0" name="id"/>
    <field labelOnTop="0" name="inspektionslaenge"/>
    <field labelOnTop="0" name="kuerzel"/>
    <field labelOnTop="0" name="ordner_bild"/>
    <field labelOnTop="0" name="ordner_video"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="pos_bis"/>
    <field labelOnTop="0" name="pos_von"/>
    <field labelOnTop="0" name="quantnr1"/>
    <field labelOnTop="0" name="quantnr2"/>
    <field labelOnTop="0" name="richtung"/>
    <field labelOnTop="0" name="schoben"/>
    <field labelOnTop="0" name="schunten"/>
    <field labelOnTop="0" name="station"/>
    <field labelOnTop="0" name="streckenschaden"/>
    <field labelOnTop="0" name="timecode"/>
    <field labelOnTop="0" name="untersuchhal"/>
    <field labelOnTop="0" name="untersuchrichtung"/>
    <field labelOnTop="0" name="videozaehler"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
