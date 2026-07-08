<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE qgis PUBLIC "http://mrcc.com/qgis.dtd" "SYSTEM">
<qgis styleCategories="AllStyleCategories" maxScale="0" minScale="100000000" labelsEnabled="1" simplifyLocal="1" simplifyAlgorithm="0" readOnly="0" version="3.28.13-Firenze" simplifyDrawingHints="1" symbologyReferenceScale="-1" hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" simplifyMaxScale="1">
<flags>
        <Identifiable>1</Identifiable>
        <Removable>1</Removable>
        <Searchable>1</Searchable>
        <Private>0</Private>
      </flags>
      <temporal durationUnit="min" accumulate="0" mode="4" limitMode="0" startExpression="to_date(&quot;untersuchtag&quot;)" endExpression="to_date(&quot;untersuchtag&quot;)" enabled="0" durationField="" fixedDuration="0" startField="" endField="">
        <fixedRange>
          <start/>
          <end/>
        </fixedRange>
      </temporal>
      <elevation binding="Centroid" extrusionEnabled="0" clamping="Terrain" zoffset="0" showMarkerSymbolInSurfacePlots="0" extrusion="0" symbology="Line" zscale="1" type="IndividualFeatures" respectLayerSymbol="1">
        <data-defined-properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data-defined-properties>
        <profileLineSymbol>
          <symbol alpha="1" is_animated="0" name="" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="255,158,23,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </profileLineSymbol>
        <profileFillSymbol>
          <symbol alpha="1" is_animated="0" name="" clip_to_extent="1" force_rhr="0" type="fill" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleFill" pass="0">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
                <Option value="255,158,23,255" name="color" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="182,113,16,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0.2" name="outline_width" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="solid" name="style" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </profileFillSymbol>
        <profileMarkerSymbol>
          <symbol alpha="1" is_animated="0" name="" clip_to_extent="1" force_rhr="0" type="marker" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,158,23,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="diamond" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="182,113,16,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0.2" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </profileMarkerSymbol>
      </elevation>
      <userNotes value="&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;>&#10;&lt;html>&lt;head>&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; />&lt;style type=&quot;text/css&quot;>&#10;p, li { white-space: pre-wrap; }&#10;&lt;/style>&lt;/head>&lt;body style=&quot; font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:400; font-style:normal;&quot;>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>Zur Anzeige von Videos und Fotos entsprechende Aktion auswählen&lt;/p>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>Zur Filterung der angezeigten Schäden entsprechende Aktion im Layer &amp;quot;Zustand_HA-Leitungen_gesamt&amp;quot; auswählen&lt;/p>&#10;&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;br />&lt;/p>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;a href=&quot;https://qkan.eu&quot;>&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;>Zur QKan-Dokumentation&lt;/span>&lt;/a>&lt;/p>&lt;/body>&lt;/html>"/>
      <renderer-v2 enableorderby="0" forceraster="0" referencescale="-1" type="RuleRenderer" symbollevels="0">
        <rules key="{4c108ca8-1203-477a-9f48-96d4e381b74c}">
          <rule label="Zustandsklasse 0, starker Mangel, Gefahr im Verzug" key="{14f6fa52-828b-4173-9779-a734185c7d50}" filter="min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 0" symbol="0"/>
          <rule label="Zustandsklasse 1, starker Mangel" key="{6ac64b31-87c5-46df-b895-c8f9618ff645}" filter="min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 1" symbol="1"/>
          <rule label="Zustandsklasse 2, mittlerer Mangel" key="{9c39bafb-a521-44a9-a29e-0fb200ff73c2}" filter="min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 2" symbol="2"/>
          <rule label="Zustandsklasse 3, leichter Mangel" key="{dbe7c6f4-43a6-47c8-8dd3-f4d395b62016}" filter="min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 3" symbol="3"/>
          <rule label="Zustandsklasse 4, geringfügiger Mangel" key="{857733ab-acb9-405b-aa85-9270d8a95091}" filter="min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 4" symbol="4"/>
          <rule label="Zustandsklasse 5, kein Mangel" key="{a5aced04-09fd-409a-9f4b-ca71ca17d7bd}" filter="min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 5" symbol="5"/>
          <rule label="nicht ermittelt" checkstate="0" key="{06fa0df9-3a60-4a3c-a72c-ca8f10d3ad45}" filter="ELSE" symbol="6"/>
        </rules>
        <symbols>
          <symbol alpha="1" is_animated="0" name="0" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="227,26,28,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.5" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" is_animated="0" name="1" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="255,127,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.5" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" is_animated="0" name="2" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="255,255,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.5" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" is_animated="0" name="3" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="143,207,79,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.5" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" is_animated="0" name="4" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="0,175,79,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.5" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" is_animated="0" name="5" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="0,127,255,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.5" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" is_animated="0" name="6" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer locked="0" enabled="1" class="SimpleLine" pass="0">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="square" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="199,199,199,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="0.26" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
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
      </renderer-v2>
      <labeling type="simple">
        <settings calloutType="simple">
          <text-style fontLetterSpacing="0" fontItalic="0" capitalization="0" useSubstitutions="0" fontSize="0.25" fontWordSpacing="0" blendMode="0" allowHtml="0" forcedItalic="0" legendString="Aa" namedStyle="Standard" multilineHeightUnit="Percentage" fontSizeUnit="RenderMetersInMapUnits" textOpacity="1" fontUnderline="0" textOrientation="horizontal" fontWeight="50" previewBkgrdColor="255,255,255,255" fontKerning="1" fontFamily="Arial" forcedBold="0" fontStrikeout="0" fieldName="kuerzel+ ' ' + left(coalesce(charakt1, ' ') + ' ', 1) + ' ' + left(coalesce(charakt2, ' ') + ' ', 1) + ' - '+ format_number( station , 2)" multilineHeight="1" isExpression="1" fontSizeMapUnitScale="3x:0,0,0,0,0,0" textColor="0,0,0,255">
            <families/>
            <text-buffer bufferSizeUnits="MM" bufferNoFill="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferOpacity="1" bufferDraw="0" bufferSize="1" bufferColor="255,255,255,255" bufferBlendMode="0" bufferJoinStyle="128"/>
            <text-mask maskSizeUnits="MM" maskedSymbolLayers="" maskJoinStyle="128" maskSize="0.5" maskOpacity="1" maskType="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskEnabled="0"/>
            <background shapeSizeUnit="RenderMetersInMapUnits" shapeSVGFile="" shapeRotation="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeOpacity="1" shapeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeOffsetX="0" shapeFillColor="255,255,255,255" shapeSizeY="0.01" shapeRadiiX="0" shapeRadiiUnit="MM" shapeSizeX="0.29999999999999999" shapeOffsetY="0" shapeRadiiY="0" shapeJoinStyle="64" shapeOffsetUnit="MM" shapeDraw="1" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeBorderWidth="0" shapeBlendMode="0">
              <symbol alpha="1" is_animated="0" name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" name="name" type="QString"/>
                    <Option name="properties"/>
                    <Option value="collection" name="type" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
                  <Option type="Map">
                    <Option value="0" name="angle" type="QString"/>
                    <Option value="square" name="cap_style" type="QString"/>
                    <Option value="164,113,88,255" name="color" type="QString"/>
                    <Option value="1" name="horizontal_anchor_point" type="QString"/>
                    <Option value="bevel" name="joinstyle" type="QString"/>
                    <Option value="circle" name="name" type="QString"/>
                    <Option value="0,0" name="offset" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="35,35,35,255" name="outline_color" type="QString"/>
                    <Option value="solid" name="outline_style" type="QString"/>
                    <Option value="0" name="outline_width" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                    <Option value="MM" name="outline_width_unit" type="QString"/>
                    <Option value="diameter" name="scale_method" type="QString"/>
                    <Option value="2" name="size" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                    <Option value="MM" name="size_unit" type="QString"/>
                    <Option value="1" name="vertical_anchor_point" type="QString"/>
                  </Option>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option value="" name="name" type="QString"/>
                      <Option name="properties"/>
                      <Option value="collection" name="type" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
              <symbol alpha="1" is_animated="0" name="fillSymbol" clip_to_extent="1" force_rhr="0" type="fill" frame_rate="10">
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" name="name" type="QString"/>
                    <Option name="properties"/>
                    <Option value="collection" name="type" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer locked="0" enabled="1" class="SimpleFill" pass="0">
                  <Option type="Map">
                    <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
                    <Option value="255,255,255,255" name="color" type="QString"/>
                    <Option value="bevel" name="joinstyle" type="QString"/>
                    <Option value="0,0" name="offset" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="128,128,128,255" name="outline_color" type="QString"/>
                    <Option value="no" name="outline_style" type="QString"/>
                    <Option value="0" name="outline_width" type="QString"/>
                    <Option value="MM" name="outline_width_unit" type="QString"/>
                    <Option value="solid" name="style" type="QString"/>
                  </Option>
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
            <shadow shadowRadius="0" shadowColor="0,0,0,255" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowOffsetDist="1" shadowDraw="0" shadowRadiusUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowUnder="0" shadowRadiusAlphaOnly="0" shadowScale="100" shadowBlendMode="6" shadowOffsetUnit="MM" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0"/>
            <dd_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format reverseDirectionSymbol="0" addDirectionSymbol="0" rightDirectionSymbol=">" multilineAlign="0" formatNumbers="0" decimals="3" plussign="0" wrapChar="" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1" autoWrapLength="0"/>
          <placement priority="5" placement="2" offsetUnits="MM" overlapHandling="AllowOverlapIfRequired" layerType="LineGeometry" centroidInside="0" polygonPlacementFlags="2" preserveRotation="1" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" overrunDistanceUnit="MM" lineAnchorTextPoint="CenterOfText" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" lineAnchorPercent="1" repeatDistanceUnits="MM" rotationAngle="0" maxCurvedCharAngleIn="25" geometryGeneratorEnabled="0" overrunDistance="0" repeatDistance="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" placementFlags="9" quadOffset="4" dist="0" geometryGenerator="" distMapUnitScale="3x:0,0,0,0,0,0" xOffset="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="0" rotationUnit="AngleDegrees" lineAnchorClipping="1" allowDegraded="1" fitInPolygonOnly="0" distUnits="MM" lineAnchorType="1" centroidWhole="0"/>
          <rendering obstacleFactor="1" mergeLines="0" obstacleType="1" fontMaxPixelSize="10000" drawLabels="1" scaleMax="2500" scaleVisibility="1" upsidedownLabels="0" fontLimitPixelSize="0" obstacle="0" minFeatureSize="0" limitNumLabels="0" scaleMin="1" fontMinPixelSize="3" unplacedVisibility="0" labelPerPart="0" zIndex="0" maxNumLabels="2000"/>
          <dd_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="Color" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="CASE &#13;&#10;WHEN min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 0 THEN '#FF0000'&#13;&#10;WHEN min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 1 THEN '#FF7F00'&#13;&#10;WHEN min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 2 THEN '#FFFF00'&#13;&#10;WHEN min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 3 THEN '#8FCF4F'&#13;&#10;WHEN min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 4 THEN '#00AF4F'&#13;&#10;WHEN min(coalesce(ZD, ZB, ZS), coalesce(ZB, ZS, ZD), coalesce(ZS, ZD, ZB)) = 5 THEN '#0000FF'END" name="expression" type="QString"/>
                  <Option value="3" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
              <Option value="0" name="blendMode" type="int"/>
              <Option name="ddProperties" type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
              <Option value="false" name="drawToAllParts" type="bool"/>
              <Option value="0" name="enabled" type="QString"/>
              <Option value="point_on_exterior" name="labelAnchorPoint" type="QString"/>
              <Option value="&lt;symbol alpha=&quot;1&quot; is_animated=&quot;0&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; frame_rate=&quot;10&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer locked=&quot;0&quot; enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; name=&quot;align_dash_pattern&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;square&quot; name=&quot;capstyle&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;5;2&quot; name=&quot;customdash&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;customdash_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;bevel&quot; name=&quot;joinstyle&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;60,60,60,255&quot; name=&quot;line_color&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;solid&quot; name=&quot;line_style&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0.3&quot; name=&quot;line_width&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;line_width_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;offset&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;offset_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;ring_filter&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;trim_distance_end&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;trim_distance_start&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;use_custom_dash&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
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
      <customproperties>
        <Option type="Map">
          <Option value="copy" name="QFieldSync/action" type="QString"/>
          <Option value="{}" name="QFieldSync/attachment_naming" type="QString"/>
          <Option value="" name="QFieldSync/attribute_editing_locked_expression" type="QString"/>
          <Option value="offline" name="QFieldSync/cloud_action" type="QString"/>
          <Option value="" name="QFieldSync/feature_addition_locked_expression" type="QString"/>
          <Option value="" name="QFieldSync/feature_deletion_locked_expression" type="QString"/>
          <Option value="" name="QFieldSync/geometry_editing_locked_expression" type="QString"/>
          <Option value="{}" name="QFieldSync/photo_naming" type="QString"/>
          <Option value="{}" name="QFieldSync/relationship_maximum_visible" type="QString"/>
          <Option value="30" name="QFieldSync/tracking_distance_requirement_minimum_meters" type="int"/>
          <Option value="1" name="QFieldSync/tracking_erroneous_distance_safeguard_maximum_meters" type="int"/>
          <Option value="0" name="QFieldSync/tracking_measurement_type" type="int"/>
          <Option value="30" name="QFieldSync/tracking_time_requirement_interval_seconds" type="int"/>
          <Option value="0" name="QFieldSync/value_map_button_interface_threshold" type="int"/>
          <Option name="dualview/previewExpressions" type="List">
            <Option value="&quot;langtext&quot;" type="QString"/>
            <Option value="&quot;foto_dateiname&quot;" type="QString"/>
            <Option value="&quot;langtext&quot;" type="QString"/>
          </Option>
          <Option value="0" name="embeddedWidgets/count" type="int"/>
          <Option value="&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;>&#10;&lt;html>&lt;head>&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; />&lt;style type=&quot;text/css&quot;>&#10;p, li { white-space: pre-wrap; }&#10;&lt;/style>&lt;/head>&lt;body style=&quot; font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:400; font-style:normal;&quot;>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>Zur Anzeige von Videos und Fotos entsprechende Aktion auswählen&lt;/p>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>Zur Filterung der angezeigten Schäden entsprechende Aktion im Layer &amp;quot;Zustand_HA-Leitungen_gesamt&amp;quot; auswählen&lt;/p>&#10;&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;br />&lt;/p>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;a href=&quot;https://qkan.eu&quot;>&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;>Zur QKan-Dokumentation&lt;/span>&lt;/a>&lt;/p>&lt;/body>&lt;/html>" name="userNotes" type="QString"/>
          <Option name="variableNames" type="invalid"/>
          <Option name="variableValues" type="invalid"/>
        </Option>
      </customproperties>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerOpacity>1</layerOpacity>
      <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
        <DiagramCategory backgroundAlpha="255" spacingUnitScale="3x:0,0,0,0,0,0" width="15" spacingUnit="MM" minimumSize="0" penColor="#000000" sizeScale="3x:0,0,0,0,0,0" spacing="5" penWidth="0" diagramOrientation="Up" penAlpha="255" showAxis="1" height="15" labelPlacementMethod="XHeight" opacity="1" backgroundColor="#ffffff" sizeType="MM" rotationOffset="270" lineSizeType="MM" scaleBasedVisibility="0" lineSizeScale="3x:0,0,0,0,0,0" enabled="0" maxScaleDenominator="1e+08" scaleDependency="Area" direction="0" barWidth="5" minScaleDenominator="0">
          <fontProperties strikethrough="0" italic="0" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style="" bold="0" underline="0"/>
          <attribute field="" label="" color="#000000" colorOpacity="1"/>
          <axisSymbol>
            <symbol alpha="1" is_animated="0" name="" clip_to_extent="1" force_rhr="0" type="line" frame_rate="10">
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
              <layer locked="0" enabled="1" class="SimpleLine" pass="0">
                <Option type="Map">
                  <Option value="0" name="align_dash_pattern" type="QString"/>
                  <Option value="square" name="capstyle" type="QString"/>
                  <Option value="5;2" name="customdash" type="QString"/>
                  <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                  <Option value="MM" name="customdash_unit" type="QString"/>
                  <Option value="0" name="dash_pattern_offset" type="QString"/>
                  <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                  <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                  <Option value="0" name="draw_inside_polygon" type="QString"/>
                  <Option value="bevel" name="joinstyle" type="QString"/>
                  <Option value="35,35,35,255" name="line_color" type="QString"/>
                  <Option value="solid" name="line_style" type="QString"/>
                  <Option value="0.26" name="line_width" type="QString"/>
                  <Option value="MM" name="line_width_unit" type="QString"/>
                  <Option value="0" name="offset" type="QString"/>
                  <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                  <Option value="MM" name="offset_unit" type="QString"/>
                  <Option value="0" name="ring_filter" type="QString"/>
                  <Option value="0" name="trim_distance_end" type="QString"/>
                  <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                  <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                  <Option value="0" name="trim_distance_start" type="QString"/>
                  <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                  <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                  <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                  <Option value="0" name="use_custom_dash" type="QString"/>
                  <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
                </Option>
                <data_defined_properties>
                  <Option type="Map">
                    <Option value="" name="name" type="QString"/>
                    <Option name="properties"/>
                    <Option value="collection" name="type" type="QString"/>
                  </Option>
                </data_defined_properties>
              </layer>
            </symbol>
          </axisSymbol>
        </DiagramCategory>
      </SingleCategoryDiagramRenderer>
      <DiagramLayerSettings zIndex="0" placement="2" priority="0" dist="0" obstacle="0" showAll="1" linePlacementFlags="18">
        <properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </properties>
      </DiagramLayerSettings>
      <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
        <activeChecks/>
        <checkConfiguration/>
      </geometryOptions>
      <legend showLabelLegend="0" type="default-vector"/>
      <referencedLayers/>
      <fieldConfiguration>
        <field name="pk" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="untersuchleit" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="schoben" configurationFlags="None">
          <editWidget type="ValueRelation">
            <config>
              <Option type="Map">
                <Option value="false" name="AllowMulti" type="bool"/>
                <Option value="true" name="AllowNull" type="bool"/>
                <Option name="Description" type="invalid"/>
                <Option name="FilterExpression" type="invalid"/>
                <Option value="schnam" name="Key" type="QString"/>
                <Option value="anschlussschaechte_40ba3139_67b9_43cf_9c10_1b62ad11f61b" name="Layer" type="QString"/>
                <Option value="HA-Schächte" name="LayerName" type="QString"/>
                <Option value="spatialite" name="LayerProviderName" type="QString"/>
                <Option value="dbname='demo.sqlite' table=&quot;anschlussschaechte&quot; (geom)" name="LayerSource" type="QString"/>
                <Option value="1" name="NofColumns" type="int"/>
                <Option value="true" name="OrderByValue" type="bool"/>
                <Option value="true" name="UseCompleter" type="bool"/>
                <Option value="schnam" name="Value" type="QString"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="schunten" configurationFlags="None">
          <editWidget type="ValueRelation">
            <config>
              <Option type="Map">
                <Option value="false" name="AllowMulti" type="bool"/>
                <Option value="true" name="AllowNull" type="bool"/>
                <Option name="Description" type="invalid"/>
                <Option name="FilterExpression" type="invalid"/>
                <Option value="schnam" name="Key" type="QString"/>
                <Option value="anschlussschaechte_40ba3139_67b9_43cf_9c10_1b62ad11f61b" name="Layer" type="QString"/>
                <Option value="HA-Schächte" name="LayerName" type="QString"/>
                <Option value="spatialite" name="LayerProviderName" type="QString"/>
                <Option value="dbname='demo.sqlite' table=&quot;anschlussschaechte&quot; (geom)" name="LayerSource" type="QString"/>
                <Option value="1" name="NofColumns" type="int"/>
                <Option value="true" name="OrderByValue" type="bool"/>
                <Option value="true" name="UseCompleter" type="bool"/>
                <Option value="schnam" name="Value" type="QString"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="id" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="untersuchtag" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option type="Map">
                <Option value="false" name="IsMultiline" type="bool"/>
                <Option value="false" name="UseHtml" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="bandnr" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="videozaehler" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="inspektionslaenge" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="station" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option type="Map">
                <Option value="false" name="IsMultiline" type="bool"/>
                <Option value="false" name="UseHtml" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="stationtext" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option type="Map">
                <Option value="false" name="IsMultiline" type="bool"/>
                <Option value="false" name="UseHtml" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="timecode" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="video_offset" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="langtext" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="kuerzel" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="charakt1" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="charakt2" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="quantnr1" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="quantnr2" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="streckenschaden" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="streckenschaden_lfdnr" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="pos_von" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="pos_bis" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="foto_dateiname" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="film_dateiname" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="ordner_bild" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="ordner_video" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="filmtyp" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="video_start" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="video_ende" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="bw_bs" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="ZD" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="ZB" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="ZS" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="kommentar" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="createdat" configurationFlags="None">
          <editWidget type="DateTime">
            <config>
              <Option type="Map">
                <Option value="true" name="allow_null" type="bool"/>
                <Option value="true" name="calendar_popup" type="bool"/>
                <Option value="dd.MM.yyyy HH:mm:ss" name="display_format" type="QString"/>
                <Option value="yyyy-MM-dd HH:mm:ss" name="field_format" type="QString"/>
                <Option value="false" name="field_iso_format" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
      </fieldConfiguration>
      <aliases>
        <alias field="pk" index="0" name=""/>
        <alias field="untersuchleit" index="1" name=""/>
        <alias field="schoben" index="2" name="Anfangsschacht"/>
        <alias field="schunten" index="3" name="Endschacht"/>
        <alias field="id" index="4" name="Inspektionsnr"/>
        <alias field="untersuchtag" index="5" name="Inspektionsdatum"/>
        <alias field="bandnr" index="6" name=""/>
        <alias field="videozaehler" index="7" name="Videozähler"/>
        <alias field="inspektionslaenge" index="8" name="Inspektionslänge"/>
        <alias field="station" index="9" name="Station"/>
        <alias field="stationtext" index="10" name="Station Text"/>
        <alias field="timecode" index="11" name="Zeitstempel"/>
        <alias field="video_offset" index="12" name="Video Offset"/>
        <alias field="langtext" index="13" name=""/>
        <alias field="kuerzel" index="14" name="Kürzel"/>
        <alias field="charakt1" index="15" name=""/>
        <alias field="charakt2" index="16" name=""/>
        <alias field="quantnr1" index="17" name=""/>
        <alias field="quantnr2" index="18" name=""/>
        <alias field="streckenschaden" index="19" name="Streckenschaden"/>
        <alias field="streckenschaden_lfdnr" index="20" name="Streckenschaden Laufnummer"/>
        <alias field="pos_von" index="21" name="Position Anfang"/>
        <alias field="pos_bis" index="22" name="Position Ende"/>
        <alias field="foto_dateiname" index="23" name="Dateiname Foto"/>
        <alias field="film_dateiname" index="24" name="Dateiname Film"/>
        <alias field="ordner_bild" index="25" name="Ordner Bild"/>
        <alias field="ordner_video" index="26" name="Ordner Video"/>
        <alias field="filmtyp" index="27" name=""/>
        <alias field="video_start" index="28" name=""/>
        <alias field="video_ende" index="29" name=""/>
        <alias field="bw_bs" index="30" name=""/>
        <alias field="ZD" index="31" name=""/>
        <alias field="ZB" index="32" name=""/>
        <alias field="ZS" index="33" name=""/>
        <alias field="kommentar" index="34" name=""/>
        <alias field="createdat" index="35" name="bearbeitet"/>
      </aliases>
      <defaults>
        <default field="pk" applyOnUpdate="0" expression=""/>
        <default field="untersuchleit" applyOnUpdate="0" expression=""/>
        <default field="schoben" applyOnUpdate="0" expression=""/>
        <default field="schunten" applyOnUpdate="0" expression=""/>
        <default field="id" applyOnUpdate="0" expression=""/>
        <default field="untersuchtag" applyOnUpdate="0" expression=""/>
        <default field="bandnr" applyOnUpdate="0" expression=""/>
        <default field="videozaehler" applyOnUpdate="0" expression=""/>
        <default field="inspektionslaenge" applyOnUpdate="0" expression=""/>
        <default field="station" applyOnUpdate="0" expression=""/>
        <default field="stationtext" applyOnUpdate="0" expression=""/>
        <default field="timecode" applyOnUpdate="0" expression=""/>
        <default field="video_offset" applyOnUpdate="0" expression=""/>
        <default field="langtext" applyOnUpdate="0" expression=""/>
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
        <default field="filmtyp" applyOnUpdate="0" expression=""/>
        <default field="video_start" applyOnUpdate="0" expression=""/>
        <default field="video_ende" applyOnUpdate="0" expression=""/>
        <default field="bw_bs" applyOnUpdate="0" expression=""/>
        <default field="ZD" applyOnUpdate="0" expression=""/>
        <default field="ZB" applyOnUpdate="0" expression=""/>
        <default field="ZS" applyOnUpdate="0" expression=""/>
        <default field="kommentar" applyOnUpdate="0" expression=""/>
        <default field="createdat" applyOnUpdate="0" expression=""/>
      </defaults>
      <constraints>
        <constraint field="pk" exp_strength="0" unique_strength="1" notnull_strength="1" constraints="3"/>
        <constraint field="untersuchleit" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="schoben" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="schunten" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="id" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="untersuchtag" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="bandnr" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="videozaehler" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="inspektionslaenge" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="station" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="stationtext" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="timecode" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="video_offset" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="langtext" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
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
        <constraint field="filmtyp" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="video_start" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="video_ende" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="bw_bs" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="ZD" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="ZB" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="ZS" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="kommentar" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="createdat" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
      </constraints>
      <constraintExpressions>
        <constraint field="pk" exp="" desc=""/>
        <constraint field="untersuchleit" exp="" desc=""/>
        <constraint field="schoben" exp="" desc=""/>
        <constraint field="schunten" exp="" desc=""/>
        <constraint field="id" exp="" desc=""/>
        <constraint field="untersuchtag" exp="" desc=""/>
        <constraint field="bandnr" exp="" desc=""/>
        <constraint field="videozaehler" exp="" desc=""/>
        <constraint field="inspektionslaenge" exp="" desc=""/>
        <constraint field="station" exp="" desc=""/>
        <constraint field="stationtext" exp="" desc=""/>
        <constraint field="timecode" exp="" desc=""/>
        <constraint field="video_offset" exp="" desc=""/>
        <constraint field="langtext" exp="" desc=""/>
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
        <constraint field="filmtyp" exp="" desc=""/>
        <constraint field="video_start" exp="" desc=""/>
        <constraint field="video_ende" exp="" desc=""/>
        <constraint field="bw_bs" exp="" desc=""/>
        <constraint field="ZD" exp="" desc=""/>
        <constraint field="ZB" exp="" desc=""/>
        <constraint field="ZS" exp="" desc=""/>
        <constraint field="kommentar" exp="" desc=""/>
        <constraint field="createdat" exp="" desc=""/>
      </constraintExpressions>
      <expressionfields/>
      <attributeactions>
        <defaultAction value="{bb35f5ca-7e7f-44b7-bfaa-ffea0d960666}" key="Canvas"/>
        <actionsetting id="{bb35f5ca-7e7f-44b7-bfaa-ffea0d960666}" capture="0" isEnabledOnlyWhenEditable="0" name="Bild öffnen" icon="" shortTitle="Bild öffnen" notificationMessage="" action="from qkan.tools.zeige_video import ShowVideo&#13;&#10;from qkan.config import Config&#13;&#10;    &#13;&#10;name=None&#13;&#10;datum=None&#13;&#10;timecode=None&#13;&#10;video_offset= None&#13;&#10;x='[%foto_dateiname%]'&#13;&#10;ShowVideo(name, datum, timecode, video_offset, 'Anschlussleitung', x).show_bild()&#13;&#10;" type="1">
          <actionScope id="Canvas"/>
          <actionScope id="Feature"/>
        </actionsetting>
        <actionsetting id="{3a3384dc-9a4e-4d34-909c-74537cee71fa}" capture="0" isEnabledOnlyWhenEditable="0" name="Video abspielen" icon="" shortTitle="Video abspielen" notificationMessage="" action="from qkan.tools.zeige_video import ShowVideo&#13;&#10;from qkan.config import Config&#13;&#10;    &#13;&#10;name='[%untersuchhal%]'&#13;&#10;datum='[%untersuchtag%]'&#13;&#10;timecode='[%timecode%]'&#13;&#10;video_offset= '[%video_offset%]'&#13;&#10;ShowVideo(name, datum, timecode, video_offset, 'Anschlussleitung', '').show()" type="1">
          <actionScope id="Canvas"/>
          <actionScope id="Feature"/>
        </actionsetting>
      </attributeactions>
      <attributetableconfig sortOrder="1" actionWidgetStyle="dropDown" sortExpression="&quot;foto_dateiname&quot;">
        <columns>
          <column name="pk" hidden="0" width="-1" type="field"/>
          <column name="untersuchleit" hidden="0" width="-1" type="field"/>
          <column name="schoben" hidden="0" width="-1" type="field"/>
          <column name="schunten" hidden="0" width="-1" type="field"/>
          <column name="id" hidden="0" width="-1" type="field"/>
          <column name="untersuchtag" hidden="0" width="-1" type="field"/>
          <column name="bandnr" hidden="0" width="-1" type="field"/>
          <column name="videozaehler" hidden="0" width="-1" type="field"/>
          <column name="inspektionslaenge" hidden="0" width="-1" type="field"/>
          <column name="station" hidden="0" width="-1" type="field"/>
          <column name="stationtext" hidden="0" width="-1" type="field"/>
          <column name="timecode" hidden="0" width="-1" type="field"/>
          <column name="video_offset" hidden="0" width="-1" type="field"/>
          <column name="langtext" hidden="0" width="-1" type="field"/>
          <column name="kuerzel" hidden="0" width="-1" type="field"/>
          <column name="charakt1" hidden="0" width="-1" type="field"/>
          <column name="charakt2" hidden="0" width="-1" type="field"/>
          <column name="quantnr1" hidden="0" width="-1" type="field"/>
          <column name="quantnr2" hidden="0" width="-1" type="field"/>
          <column name="streckenschaden" hidden="0" width="-1" type="field"/>
          <column name="streckenschaden_lfdnr" hidden="0" width="-1" type="field"/>
          <column name="pos_von" hidden="0" width="-1" type="field"/>
          <column name="pos_bis" hidden="0" width="-1" type="field"/>
          <column name="foto_dateiname" hidden="0" width="395" type="field"/>
          <column name="film_dateiname" hidden="0" width="-1" type="field"/>
          <column name="ordner_bild" hidden="0" width="-1" type="field"/>
          <column name="ordner_video" hidden="0" width="-1" type="field"/>
          <column name="filmtyp" hidden="0" width="-1" type="field"/>
          <column name="video_start" hidden="0" width="-1" type="field"/>
          <column name="video_ende" hidden="0" width="-1" type="field"/>
          <column name="ZD" hidden="0" width="-1" type="field"/>
          <column name="ZB" hidden="0" width="-1" type="field"/>
          <column name="ZS" hidden="0" width="-1" type="field"/>
          <column name="kommentar" hidden="0" width="-1" type="field"/>
          <column name="createdat" hidden="0" width="-1" type="field"/>
          <column name="bw_bs" hidden="0" width="-1" type="field"/>
          <column hidden="1" width="-1" type="actions"/>
        </columns>
      </attributetableconfig>
      <conditionalstyles>
        <rowstyles/>
        <fieldstyles/>
      </conditionalstyles>
      <storedexpressions/>
      <editforminit/>
      <editforminitcodesource>0</editforminitcodesource>
      <editforminitfilepath/>
      <featformsuppress>0</featformsuppress>
      <editorlayout>uifilelayout</editorlayout>
      <editable>
        <field name="ZB" editable="1"/>
        <field name="ZD" editable="1"/>
        <field name="ZS" editable="1"/>
        <field name="bandnr" editable="1"/>
        <field name="bw_bs" editable="1"/>
        <field name="charakt1" editable="1"/>
        <field name="charakt2" editable="1"/>
        <field name="createdat" editable="1"/>
        <field name="film_dateiname" editable="1"/>
        <field name="filmtyp" editable="1"/>
        <field name="foto_dateiname" editable="1"/>
        <field name="id" editable="1"/>
        <field name="inspektionslaenge" editable="1"/>
        <field name="kommentar" editable="1"/>
        <field name="kuerzel" editable="1"/>
        <field name="langtext" editable="1"/>
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
        <field name="stationtext" editable="1"/>
        <field name="streckenschaden" editable="1"/>
        <field name="streckenschaden_lfdnr" editable="1"/>
        <field name="timecode" editable="1"/>
        <field name="untersuchhal" editable="1"/>
        <field name="untersuchleit" editable="1"/>
        <field name="untersuchrichtung" editable="1"/>
        <field name="untersuchtag" editable="1"/>
        <field name="video_ende" editable="1"/>
        <field name="video_offset" editable="1"/>
        <field name="video_start" editable="1"/>
        <field name="videozaehler" editable="1"/>
      </editable>
      <labelOnTop>
        <field name="ZB" labelOnTop="0"/>
        <field name="ZD" labelOnTop="0"/>
        <field name="ZS" labelOnTop="0"/>
        <field name="bandnr" labelOnTop="0"/>
        <field name="bw_bs" labelOnTop="0"/>
        <field name="charakt1" labelOnTop="0"/>
        <field name="charakt2" labelOnTop="0"/>
        <field name="createdat" labelOnTop="0"/>
        <field name="film_dateiname" labelOnTop="0"/>
        <field name="filmtyp" labelOnTop="0"/>
        <field name="foto_dateiname" labelOnTop="0"/>
        <field name="id" labelOnTop="0"/>
        <field name="inspektionslaenge" labelOnTop="0"/>
        <field name="kommentar" labelOnTop="0"/>
        <field name="kuerzel" labelOnTop="0"/>
        <field name="langtext" labelOnTop="0"/>
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
        <field name="stationtext" labelOnTop="0"/>
        <field name="streckenschaden" labelOnTop="0"/>
        <field name="streckenschaden_lfdnr" labelOnTop="0"/>
        <field name="timecode" labelOnTop="0"/>
        <field name="untersuchhal" labelOnTop="0"/>
        <field name="untersuchleit" labelOnTop="0"/>
        <field name="untersuchrichtung" labelOnTop="0"/>
        <field name="untersuchtag" labelOnTop="0"/>
        <field name="video_ende" labelOnTop="0"/>
        <field name="video_offset" labelOnTop="0"/>
        <field name="video_start" labelOnTop="0"/>
        <field name="videozaehler" labelOnTop="0"/>
      </labelOnTop>
      <reuseLastValue>
        <field name="ZB" reuseLastValue="0"/>
        <field name="ZD" reuseLastValue="0"/>
        <field name="ZS" reuseLastValue="0"/>
        <field name="bandnr" reuseLastValue="0"/>
        <field name="bw_bs" reuseLastValue="0"/>
        <field name="charakt1" reuseLastValue="0"/>
        <field name="charakt2" reuseLastValue="0"/>
        <field name="createdat" reuseLastValue="0"/>
        <field name="film_dateiname" reuseLastValue="0"/>
        <field name="filmtyp" reuseLastValue="0"/>
        <field name="foto_dateiname" reuseLastValue="0"/>
        <field name="id" reuseLastValue="0"/>
        <field name="inspektionslaenge" reuseLastValue="0"/>
        <field name="kommentar" reuseLastValue="0"/>
        <field name="kuerzel" reuseLastValue="0"/>
        <field name="langtext" reuseLastValue="0"/>
        <field name="ordner_bild" reuseLastValue="0"/>
        <field name="ordner_video" reuseLastValue="0"/>
        <field name="pk" reuseLastValue="0"/>
        <field name="pos_bis" reuseLastValue="0"/>
        <field name="pos_von" reuseLastValue="0"/>
        <field name="quantnr1" reuseLastValue="0"/>
        <field name="quantnr2" reuseLastValue="0"/>
        <field name="richtung" reuseLastValue="0"/>
        <field name="schoben" reuseLastValue="0"/>
        <field name="schunten" reuseLastValue="0"/>
        <field name="station" reuseLastValue="0"/>
        <field name="stationtext" reuseLastValue="0"/>
        <field name="streckenschaden" reuseLastValue="0"/>
        <field name="streckenschaden_lfdnr" reuseLastValue="0"/>
        <field name="timecode" reuseLastValue="0"/>
        <field name="untersuchhal" reuseLastValue="0"/>
        <field name="untersuchleit" reuseLastValue="0"/>
        <field name="untersuchrichtung" reuseLastValue="0"/>
        <field name="untersuchtag" reuseLastValue="0"/>
        <field name="video_ende" reuseLastValue="0"/>
        <field name="video_offset" reuseLastValue="0"/>
        <field name="video_start" reuseLastValue="0"/>
        <field name="videozaehler" reuseLastValue="0"/>
      </reuseLastValue>
      <dataDefinedFieldProperties/>
      <widgets/>
      <previewExpression>"langtext"</previewExpression>
      <mapTip/>
    </qgis>
