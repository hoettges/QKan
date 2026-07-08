<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE qgis PUBLIC "http://mrcc.com/qgis.dtd" "SYSTEM">
<qgis styleCategories="AllStyleCategories" maxScale="0" minScale="100000000" labelsEnabled="0" simplifyLocal="1" simplifyAlgorithm="0" readOnly="0" version="3.28.13-Firenze" simplifyDrawingHints="1" symbologyReferenceScale="-1" hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" simplifyMaxScale="1">
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
                <Option value="141,90,153,255" name="line_color" type="QString"/>
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
                <Option value="141,90,153,255" name="color" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="101,64,109,255" name="outline_color" type="QString"/>
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
                <Option value="141,90,153,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="diamond" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="101,64,109,255" name="outline_color" type="QString"/>
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
      <userNotes value="&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;>&#10;&lt;html>&lt;head>&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; />&lt;style type=&quot;text/css&quot;>&#10;p, li { white-space: pre-wrap; }&#10;&lt;/style>&lt;/head>&lt;body style=&quot; font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:400; font-style:normal;&quot;>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>Filterung nach Inspektionsdatum über das Aktionen-Symbol&lt;/p>&#10;&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;br />&lt;/p>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;a href=&quot;https://qkan.eu&quot;>&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;>Zur QKan-Dokumentation&lt;/span>&lt;/a>&lt;/p>&lt;/body>&lt;/html>"/>
      <renderer-v2 enableorderby="0" forceraster="0" referencescale="-1" type="RuleRenderer" symbollevels="0">
        <rules key="{4c108ca8-1203-477a-9f48-96d4e381b74c}">
          <rule label="Zustandsklasse 0, starker Mangel, Gefahr im Verzug" key="{14f6fa52-828b-4173-9779-a734185c7d50}" filter="min(coalesce(max_ZD, max_ZB, max_ZS), coalesce(max_ZB, max_ZS, max_ZD), coalesce(max_ZS, max_ZD, max_ZB)) = 0" symbol="0"/>
          <rule label="Zustandsklasse 1, starker Mangel" key="{6ac64b31-87c5-46df-b895-c8f9618ff645}" filter="min(coalesce(max_ZD, max_ZB, max_ZS), coalesce(max_ZB, max_ZS, max_ZD), coalesce(max_ZS, max_ZD, max_ZB)) = 1" symbol="1"/>
          <rule label="Zustandsklasse 2, mittlerer Mangel" key="{9c39bafb-a521-44a9-a29e-0fb200ff73c2}" filter="min(coalesce(max_ZD, max_ZB, max_ZS), coalesce(max_ZB, max_ZS, max_ZD), coalesce(max_ZS, max_ZD, max_ZB)) = 2" symbol="2"/>
          <rule label="Zustandsklasse 3, leichter Mangel" key="{dbe7c6f4-43a6-47c8-8dd3-f4d395b62016}" filter="min(coalesce(max_ZD, max_ZB, max_ZS), coalesce(max_ZB, max_ZS, max_ZD), coalesce(max_ZS, max_ZD, max_ZB)) = 3" symbol="3"/>
          <rule label="Zustandsklasse 4, geringfügiger Mangel" key="{857733ab-acb9-405b-aa85-9270d8a95091}" filter="min(coalesce(max_ZD, max_ZB, max_ZS), coalesce(max_ZB, max_ZS, max_ZD), coalesce(max_ZS, max_ZD, max_ZB)) = 4" symbol="4"/>
          <rule label="Zustandsklasse 5, kein Mangel" key="{a5aced04-09fd-409a-9f4b-ca71ca17d7bd}" filter="min(coalesce(max_ZD, max_ZB, max_ZS), coalesce(max_ZB, max_ZS, max_ZD), coalesce(max_ZS, max_ZD, max_ZB)) = 5" symbol="5"/>
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
                <Option value="255,21,21,255" name="line_color" type="QString"/>
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
                <Option value="203,203,203,255" name="line_color" type="QString"/>
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
            <Option value="haltnam || ' (' || untersuchtag || ')'" type="QString"/>
          </Option>
          <Option value="0" name="embeddedWidgets/count" type="int"/>
          <Option value="&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;>&#10;&lt;html>&lt;head>&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; />&lt;style type=&quot;text/css&quot;>&#10;p, li { white-space: pre-wrap; }&#10;&lt;/style>&lt;/head>&lt;body style=&quot; font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:400; font-style:normal;&quot;>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>Filterung nach Inspektionsdatum über das Aktionen-Symbol&lt;/p>&#10;&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;br />&lt;/p>&#10;&lt;p style=&quot; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;&quot;>&lt;a href=&quot;https://qkan.eu&quot;>&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;>Zur QKan-Dokumentation&lt;/span>&lt;/a>&lt;/p>&lt;/body>&lt;/html>" name="userNotes" type="QString"/>
          <Option name="variableNames" type="invalid"/>
          <Option name="variableValues" type="invalid"/>
        </Option>
      </customproperties>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerOpacity>1</layerOpacity>
      <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
        <DiagramCategory backgroundAlpha="255" spacingUnitScale="3x:0,0,0,0,0,0" width="15" spacingUnit="MM" minimumSize="0" penColor="#000000" sizeScale="3x:0,0,0,0,0,0" spacing="5" penWidth="0" diagramOrientation="Up" penAlpha="255" showAxis="1" height="15" labelPlacementMethod="XHeight" opacity="1" backgroundColor="#ffffff" sizeType="MM" rotationOffset="270" lineSizeType="MM" scaleBasedVisibility="0" lineSizeScale="3x:0,0,0,0,0,0" enabled="0" maxScaleDenominator="1e+08" scaleDependency="Area" direction="0" barWidth="5" minScaleDenominator="0">
          <fontProperties strikethrough="0" italic="0" description="MS Shell Dlg 2,7.8,-1,5,50,0,0,0,0,0" style="" bold="0" underline="0"/>
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
        <field name="haltnam" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="bezugspunkt" configurationFlags="None">
          <editWidget type="ValueMap">
            <config>
              <Option type="Map">
                <Option name="map" type="List">
                  <Option type="Map">
                    <Option value="Rohranfang" name="Rohranfang" type="QString"/>
                  </Option>
                  <Option type="Map">
                    <Option value="Gerinnemittelpunkt" name="Gerinnemittelpunkt" type="QString"/>
                  </Option>
                </Option>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="schoben" configurationFlags="None">
          <editWidget type="ValueRelation">
            <config>
              <Option type="Map">
                <Option value="false" name="AllowMulti" type="bool"/>
                <Option value="true" name="AllowNull" type="bool"/>
                <Option value="" name="Description" type="QString"/>
                <Option value="" name="FilterExpression" type="QString"/>
                <Option value="schnam" name="Key" type="QString"/>
                <Option value="schaechte20161220162259105" name="Layer" type="QString"/>
                <Option value="Schächte" name="LayerName" type="QString"/>
                <Option value="spatialite" name="LayerProviderName" type="QString"/>
                <Option value="dbname='demo.sqlite' table=&quot;schaechte&quot; (geop) sql=schachttyp = 'Schacht'" name="LayerSource" type="QString"/>
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
                <Option value="" name="Description" type="QString"/>
                <Option value="" name="FilterExpression" type="QString"/>
                <Option value="schnam" name="Key" type="QString"/>
                <Option value="schaechte20161220162259105" name="Layer" type="QString"/>
                <Option value="Schächte" name="LayerName" type="QString"/>
                <Option value="spatialite" name="LayerProviderName" type="QString"/>
                <Option value="dbname='demo.sqlite' table=&quot;schaechte&quot; (geop) sql=schachttyp = 'Schacht'" name="LayerSource" type="QString"/>
                <Option value="1" name="NofColumns" type="int"/>
                <Option value="true" name="OrderByValue" type="bool"/>
                <Option value="true" name="UseCompleter" type="bool"/>
                <Option value="schnam" name="Value" type="QString"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="hoehe" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="breite" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="laenge" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="baujahr" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
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
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="untersucher" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="untersuchrichtung" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="wetter" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option type="Map">
                <Option value="false" name="IsMultiline" type="bool"/>
                <Option value="false" name="UseHtml" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="bewertungsart" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option type="Map">
                <Option value="false" name="IsMultiline" type="bool"/>
                <Option value="false" name="UseHtml" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="bewertungstag" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="strasse" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option type="Map">
                <Option value="false" name="IsMultiline" type="bool"/>
                <Option value="false" name="UseHtml" type="bool"/>
              </Option>
            </config>
          </editWidget>
        </field>
        <field name="datenart" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="auftragsbezeichnung" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="max_ZD" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="max_ZB" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="max_ZS" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="xschob" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="yschob" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="xschun" configurationFlags="None">
          <editWidget type="TextEdit">
            <config>
              <Option/>
            </config>
          </editWidget>
        </field>
        <field name="yschun" configurationFlags="None">
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
        <alias field="haltnam" index="1" name="Name"/>
        <alias field="bezugspunkt" index="2" name="Bezugspunkt"/>
        <alias field="schoben" index="3" name="Anfangsschacht"/>
        <alias field="schunten" index="4" name="Endschacht"/>
        <alias field="hoehe" index="5" name="Profilhöhe"/>
        <alias field="breite" index="6" name="Profilbreite"/>
        <alias field="laenge" index="7" name="Haltungslänge"/>
        <alias field="baujahr" index="8" name="Baujahr"/>
        <alias field="id" index="9" name="Inspektionsnr"/>
        <alias field="untersuchtag" index="10" name="Inspektionsdatum"/>
        <alias field="untersucher" index="11" name="durchgeführt vom"/>
        <alias field="untersuchrichtung" index="12" name=""/>
        <alias field="wetter" index="13" name="Wetter"/>
        <alias field="bewertungsart" index="14" name="Bewertungsart"/>
        <alias field="bewertungstag" index="15" name="Bewertungstag"/>
        <alias field="strasse" index="16" name=""/>
        <alias field="datenart" index="17" name=""/>
        <alias field="auftragsbezeichnung" index="18" name=""/>
        <alias field="max_ZD" index="19" name=""/>
        <alias field="max_ZB" index="20" name=""/>
        <alias field="max_ZS" index="21" name=""/>
        <alias field="xschob" index="22" name=""/>
        <alias field="yschob" index="23" name=""/>
        <alias field="xschun" index="24" name=""/>
        <alias field="yschun" index="25" name=""/>
        <alias field="kommentar" index="26" name="Kommentar"/>
        <alias field="createdat" index="27" name="bearbeitet"/>
      </aliases>
      <defaults>
        <default field="pk" applyOnUpdate="0" expression=""/>
        <default field="haltnam" applyOnUpdate="0" expression=""/>
        <default field="bezugspunkt" applyOnUpdate="0" expression=""/>
        <default field="schoben" applyOnUpdate="0" expression=""/>
        <default field="schunten" applyOnUpdate="0" expression=""/>
        <default field="hoehe" applyOnUpdate="0" expression=""/>
        <default field="breite" applyOnUpdate="0" expression=""/>
        <default field="laenge" applyOnUpdate="0" expression=""/>
        <default field="baujahr" applyOnUpdate="0" expression=""/>
        <default field="id" applyOnUpdate="0" expression=""/>
        <default field="untersuchtag" applyOnUpdate="0" expression=""/>
        <default field="untersucher" applyOnUpdate="0" expression=""/>
        <default field="untersuchrichtung" applyOnUpdate="0" expression=""/>
        <default field="wetter" applyOnUpdate="0" expression=""/>
        <default field="bewertungsart" applyOnUpdate="0" expression=""/>
        <default field="bewertungstag" applyOnUpdate="0" expression=""/>
        <default field="strasse" applyOnUpdate="0" expression=""/>
        <default field="datenart" applyOnUpdate="0" expression=""/>
        <default field="auftragsbezeichnung" applyOnUpdate="0" expression=""/>
        <default field="max_ZD" applyOnUpdate="0" expression=""/>
        <default field="max_ZB" applyOnUpdate="0" expression=""/>
        <default field="max_ZS" applyOnUpdate="0" expression=""/>
        <default field="xschob" applyOnUpdate="0" expression=""/>
        <default field="yschob" applyOnUpdate="0" expression=""/>
        <default field="xschun" applyOnUpdate="0" expression=""/>
        <default field="yschun" applyOnUpdate="0" expression=""/>
        <default field="kommentar" applyOnUpdate="0" expression=""/>
        <default field="createdat" applyOnUpdate="0" expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')"/>
      </defaults>
      <constraints>
        <constraint field="pk" exp_strength="0" unique_strength="2" notnull_strength="2" constraints="3"/>
        <constraint field="haltnam" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="bezugspunkt" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="schoben" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="schunten" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="hoehe" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="breite" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="laenge" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="baujahr" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="id" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="untersuchtag" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="untersucher" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="untersuchrichtung" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="wetter" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="bewertungsart" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="bewertungstag" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="strasse" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="datenart" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="auftragsbezeichnung" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="max_ZD" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="max_ZB" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="max_ZS" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="xschob" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="yschob" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="xschun" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="yschun" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="kommentar" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
        <constraint field="createdat" exp_strength="0" unique_strength="0" notnull_strength="0" constraints="0"/>
      </constraints>
      <constraintExpressions>
        <constraint field="pk" exp="" desc=""/>
        <constraint field="haltnam" exp="" desc=""/>
        <constraint field="bezugspunkt" exp="" desc=""/>
        <constraint field="schoben" exp="" desc=""/>
        <constraint field="schunten" exp="" desc=""/>
        <constraint field="hoehe" exp="" desc=""/>
        <constraint field="breite" exp="" desc=""/>
        <constraint field="laenge" exp="" desc=""/>
        <constraint field="baujahr" exp="" desc=""/>
        <constraint field="id" exp="" desc=""/>
        <constraint field="untersuchtag" exp="" desc=""/>
        <constraint field="untersucher" exp="" desc=""/>
        <constraint field="untersuchrichtung" exp="" desc=""/>
        <constraint field="wetter" exp="" desc=""/>
        <constraint field="bewertungsart" exp="" desc=""/>
        <constraint field="bewertungstag" exp="" desc=""/>
        <constraint field="strasse" exp="" desc=""/>
        <constraint field="datenart" exp="" desc=""/>
        <constraint field="auftragsbezeichnung" exp="" desc=""/>
        <constraint field="max_ZD" exp="" desc=""/>
        <constraint field="max_ZB" exp="" desc=""/>
        <constraint field="max_ZS" exp="" desc=""/>
        <constraint field="xschob" exp="" desc=""/>
        <constraint field="yschob" exp="" desc=""/>
        <constraint field="xschun" exp="" desc=""/>
        <constraint field="yschun" exp="" desc=""/>
        <constraint field="kommentar" exp="" desc=""/>
        <constraint field="createdat" exp="" desc=""/>
      </constraintExpressions>
      <expressionfields/>
      <attributeactions>
        <defaultAction value="{7f802d16-fd1e-45ac-9683-a33a61fc674b}" key="Canvas"/>
        <actionsetting id="{7f802d16-fd1e-45ac-9683-a33a61fc674b}" capture="1" isEnabledOnlyWhenEditable="0" name="Aktuelle Zustandsdaten für alle Haltungen anzeigen" icon="" shortTitle="Aktuelle Zustandsdaten" notificationMessage="" action="from qkan.tools.zeige_untersuchungsdaten import ShowHaltungsschaeden&#13;&#10;form = ShowHaltungsschaeden(id = 1)&#13;&#10;del form&#13;&#10;" type="1">
          <actionScope id="Canvas"/>
          <actionScope id="Feature"/>
        </actionsetting>
        <actionsetting id="{89c4a6ee-1b24-4219-996f-61aaebcc49ac}" capture="1" isEnabledOnlyWhenEditable="0" name="Aktuelle Zustandsdaten zu Haltung anzeigen" icon="" shortTitle="Aktuelle Zustandsdaten zu Haltung" notificationMessage="" action="from qkan.tools.zeige_untersuchungsdaten import ShowHaltungsschaeden&#13;&#10;form = ShowHaltungsschaeden(haltnam = '[%haltnam%]', id = 1)&#13;&#10;del form&#13;&#10;" type="1">
          <actionScope id="Canvas"/>
          <actionScope id="Feature"/>
        </actionsetting>
        <actionsetting id="{df45edbe-ca08-43ef-85cf-7e9ae15140b0}" capture="1" isEnabledOnlyWhenEditable="0" name="Alle Zustandsdaten für alle Haltungen anzeigen" icon="" shortTitle="Alle Zustandsdaten" notificationMessage="" action="from qkan.tools.zeige_untersuchungsdaten import ShowHaltungsschaeden&#13;&#10;form = ShowHaltungsschaeden()&#13;&#10;del form&#13;&#10;" type="1">
          <actionScope id="Canvas"/>
          <actionScope id="Feature"/>
        </actionsetting>
        <actionsetting id="{9a8adc00-698b-4b5b-af2b-fbfa3b93d012}" capture="1" isEnabledOnlyWhenEditable="0" name="Zustandsdaten zu Haltung und Untersuchungsdatum anzeigen" icon="" shortTitle="Zustandsdaten zu Haltung und Untersuchungsdatum" notificationMessage="" action="from qkan.tools.zeige_untersuchungsdaten import ShowHaltungsschaeden&#13;&#10;form = ShowHaltungsschaeden(haltnam = '[%haltnam%]', untersuchtag = '[%untersuchtag%]')&#13;&#10;del form&#13;&#10;" type="1">
          <actionScope id="Canvas"/>
          <actionScope id="Feature"/>
        </actionsetting>
      </attributeactions>
      <attributetableconfig sortOrder="1" actionWidgetStyle="dropDown" sortExpression="&quot;haltnam&quot;">
        <columns>
          <column name="pk" hidden="0" width="-1" type="field"/>
          <column name="haltnam" hidden="0" width="-1" type="field"/>
          <column name="bezugspunkt" hidden="0" width="151" type="field"/>
          <column name="schoben" hidden="0" width="-1" type="field"/>
          <column name="schunten" hidden="0" width="-1" type="field"/>
          <column name="hoehe" hidden="0" width="-1" type="field"/>
          <column name="breite" hidden="0" width="-1" type="field"/>
          <column name="laenge" hidden="0" width="-1" type="field"/>
          <column name="baujahr" hidden="0" width="-1" type="field"/>
          <column name="id" hidden="0" width="119" type="field"/>
          <column name="untersuchtag" hidden="0" width="100" type="field"/>
          <column name="untersucher" hidden="0" width="142" type="field"/>
          <column name="untersuchrichtung" hidden="0" width="146" type="field"/>
          <column name="wetter" hidden="0" width="-1" type="field"/>
          <column name="bewertungsart" hidden="0" width="-1" type="field"/>
          <column name="bewertungstag" hidden="0" width="-1" type="field"/>
          <column name="strasse" hidden="0" width="-1" type="field"/>
          <column name="datenart" hidden="0" width="-1" type="field"/>
          <column name="auftragsbezeichnung" hidden="0" width="166" type="field"/>
          <column name="max_ZD" hidden="0" width="-1" type="field"/>
          <column name="max_ZB" hidden="0" width="-1" type="field"/>
          <column name="max_ZS" hidden="0" width="-1" type="field"/>
          <column name="xschob" hidden="0" width="-1" type="field"/>
          <column name="yschob" hidden="0" width="100" type="field"/>
          <column name="xschun" hidden="0" width="100" type="field"/>
          <column name="yschun" hidden="0" width="100" type="field"/>
          <column name="kommentar" hidden="0" width="100" type="field"/>
          <column name="createdat" hidden="0" width="-1" type="field"/>
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
        <field name="auftragsbezeichnung" editable="1"/>
        <field name="baujahr" editable="1"/>
        <field name="bewertungsart" editable="1"/>
        <field name="bewertungstag" editable="1"/>
        <field name="bezugspunkt" editable="1"/>
        <field name="breite" editable="1"/>
        <field name="createdat" editable="1"/>
        <field name="datenart" editable="1"/>
        <field name="haltnam" editable="1"/>
        <field name="hoehe" editable="1"/>
        <field name="id" editable="1"/>
        <field name="kommentar" editable="1"/>
        <field name="laenge" editable="1"/>
        <field name="max_ZB" editable="1"/>
        <field name="max_ZD" editable="1"/>
        <field name="max_ZS" editable="1"/>
        <field name="pk" editable="1"/>
        <field name="schoben" editable="1"/>
        <field name="schunten" editable="1"/>
        <field name="strasse" editable="1"/>
        <field name="umbenennung_haltung — Tabelle2_Field4" editable="0"/>
        <field name="umbennenung — Tabelle1_schnam_1" editable="0"/>
        <field name="untersucher" editable="1"/>
        <field name="untersuchrichtung" editable="1"/>
        <field name="untersuchtag" editable="1"/>
        <field name="wetter" editable="1"/>
        <field name="xschob" editable="1"/>
        <field name="xschun" editable="1"/>
        <field name="yschob" editable="1"/>
        <field name="yschun" editable="1"/>
      </editable>
      <labelOnTop>
        <field name="auftragsbezeichnung" labelOnTop="0"/>
        <field name="baujahr" labelOnTop="0"/>
        <field name="bewertungsart" labelOnTop="0"/>
        <field name="bewertungstag" labelOnTop="0"/>
        <field name="bezugspunkt" labelOnTop="0"/>
        <field name="breite" labelOnTop="0"/>
        <field name="createdat" labelOnTop="0"/>
        <field name="datenart" labelOnTop="0"/>
        <field name="haltnam" labelOnTop="0"/>
        <field name="hoehe" labelOnTop="0"/>
        <field name="id" labelOnTop="0"/>
        <field name="kommentar" labelOnTop="0"/>
        <field name="laenge" labelOnTop="0"/>
        <field name="max_ZB" labelOnTop="0"/>
        <field name="max_ZD" labelOnTop="0"/>
        <field name="max_ZS" labelOnTop="0"/>
        <field name="pk" labelOnTop="0"/>
        <field name="schoben" labelOnTop="0"/>
        <field name="schunten" labelOnTop="0"/>
        <field name="strasse" labelOnTop="0"/>
        <field name="umbenennung_haltung — Tabelle2_Field4" labelOnTop="0"/>
        <field name="umbennenung — Tabelle1_schnam_1" labelOnTop="0"/>
        <field name="untersucher" labelOnTop="0"/>
        <field name="untersuchrichtung" labelOnTop="0"/>
        <field name="untersuchtag" labelOnTop="0"/>
        <field name="wetter" labelOnTop="0"/>
        <field name="xschob" labelOnTop="0"/>
        <field name="xschun" labelOnTop="0"/>
        <field name="yschob" labelOnTop="0"/>
        <field name="yschun" labelOnTop="0"/>
      </labelOnTop>
      <reuseLastValue>
        <field name="auftragsbezeichnung" reuseLastValue="0"/>
        <field name="baujahr" reuseLastValue="0"/>
        <field name="bewertungsart" reuseLastValue="0"/>
        <field name="bewertungstag" reuseLastValue="0"/>
        <field name="bezugspunkt" reuseLastValue="1"/>
        <field name="breite" reuseLastValue="0"/>
        <field name="createdat" reuseLastValue="0"/>
        <field name="datenart" reuseLastValue="0"/>
        <field name="haltnam" reuseLastValue="0"/>
        <field name="hoehe" reuseLastValue="0"/>
        <field name="id" reuseLastValue="0"/>
        <field name="kommentar" reuseLastValue="0"/>
        <field name="laenge" reuseLastValue="0"/>
        <field name="max_ZB" reuseLastValue="0"/>
        <field name="max_ZD" reuseLastValue="0"/>
        <field name="max_ZS" reuseLastValue="0"/>
        <field name="pk" reuseLastValue="0"/>
        <field name="schoben" reuseLastValue="0"/>
        <field name="schunten" reuseLastValue="0"/>
        <field name="strasse" reuseLastValue="0"/>
        <field name="umbenennung_haltung — Tabelle2_Field4" reuseLastValue="0"/>
        <field name="umbennenung — Tabelle1_schnam_1" reuseLastValue="0"/>
        <field name="untersucher" reuseLastValue="0"/>
        <field name="untersuchrichtung" reuseLastValue="0"/>
        <field name="untersuchtag" reuseLastValue="0"/>
        <field name="wetter" reuseLastValue="0"/>
        <field name="xschob" reuseLastValue="0"/>
        <field name="xschun" reuseLastValue="0"/>
        <field name="yschob" reuseLastValue="0"/>
        <field name="yschun" reuseLastValue="0"/>
      </reuseLastValue>
      <dataDefinedFieldProperties/>
      <widgets/>
      <previewExpression>haltnam || ' (' || untersuchtag || ')'</previewExpression>
      <mapTip>[% haltnam || ' (' || untersuchtag || ')' %]</mapTip>
    </qgis>
