<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="1" symbologyReferenceScale="-1" hasScaleBasedVisibilityFlag="0" version="3.34.7-Prizren" minScale="100000000" maxScale="0" simplifyDrawingHints="1" simplifyAlgorithm="0" simplifyMaxScale="1" simplifyLocal="1" simplifyDrawingTol="1" styleCategories="AllStyleCategories" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal durationUnit="min" startExpression="to_date(&quot;untersuchtag&quot;)" enabled="0" endField="" mode="4" accumulate="0" limitMode="0" endExpression="to_date(&quot;untersuchtag&quot;)" durationField="" startField="" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <elevation zoffset="0" extrusionEnabled="0" binding="Centroid" respectLayerSymbol="1" clamping="Terrain" extrusion="0" symbology="Line" zscale="1" type="IndividualFeatures" showMarkerSymbolInSurfacePlots="0">
    <data-defined-properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </data-defined-properties>
    <profileLineSymbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{a27cf661-c752-4ce9-a5e9-bce0a1b714dc}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="141,90,153,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.6" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileLineSymbol>
    <profileFillSymbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="fill" is_animated="0" alpha="1" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleFill" enabled="1" id="{ab8177ef-6b66-4f80-b427-66664a4c405a}" locked="0" pass="0">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
            <Option value="141,90,153,255" type="QString" name="color"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="101,64,109,255" type="QString" name="outline_color"/>
            <Option value="solid" type="QString" name="outline_style"/>
            <Option value="0.2" type="QString" name="outline_width"/>
            <Option value="MM" type="QString" name="outline_width_unit"/>
            <Option value="solid" type="QString" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileFillSymbol>
    <profileMarkerSymbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="marker" is_animated="0" alpha="1" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleMarker" enabled="1" id="{693502ef-92fb-4642-81d3-ea5c362f92d7}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="angle"/>
            <Option value="square" type="QString" name="cap_style"/>
            <Option value="141,90,153,255" type="QString" name="color"/>
            <Option value="1" type="QString" name="horizontal_anchor_point"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="diamond" type="QString" name="name"/>
            <Option value="0,0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="101,64,109,255" type="QString" name="outline_color"/>
            <Option value="solid" type="QString" name="outline_style"/>
            <Option value="0.2" type="QString" name="outline_width"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
            <Option value="MM" type="QString" name="outline_width_unit"/>
            <Option value="diameter" type="QString" name="scale_method"/>
            <Option value="3" type="QString" name="size"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
            <Option value="MM" type="QString" name="size_unit"/>
            <Option value="1" type="QString" name="vertical_anchor_point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileMarkerSymbol>
  </elevation>
  <renderer-v2 referencescale="-1" forceraster="0" symbollevels="0" enableorderby="0" type="RuleRenderer">
    <rules key="{4c108ca8-1203-477a-9f48-96d4e381b74c}">
      <rule label="Zustandsklasse 1, starker Mangel" key="{7d940636-afec-4238-8412-8e5bd6db260b}" symbol="0" filter="min(ZD, ZB, ZS) = 1"/>
      <rule label="Zustandsklasse 2, mittlerer Mangel" key="{9c39bafb-a521-44a9-a29e-0fb200ff73c2}" symbol="1" filter="min(ZD, ZB, ZS) = 2"/>
      <rule label="Zustandsklasse 3, leichter Mangel" key="{dbe7c6f4-43a6-47c8-8dd3-f4d395b62016}" symbol="2" filter="min(ZD, ZB, ZS) = 3"/>
      <rule label="Zustandsklasse 4, geringfügiger Mangel" key="{857733ab-acb9-405b-aa85-9270d8a95091}" symbol="3" filter="min(ZD, ZB, ZS) = 4"/>
      <rule label="Zustandsklasse 5, kein Mangel" key="{a5aced04-09fd-409a-9f4b-ca71ca17d7bd}" symbol="4" filter="min(ZD, ZB, ZS) = 5"/>
      <rule key="{06fa0df9-3a60-4a3c-a72c-ca8f10d3ad45}" symbol="5" filter="(min(ZD, ZB, ZS) &lt; 1 OR min(ZD, ZB, ZS) > 5)"/>
    </rules>
    <symbols>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{06aac535-1fef-4411-88fb-b7e6456444d4}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="255,127,0,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.5" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="1">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{fe423451-84e0-4a79-925b-2e4d7795b7a3}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="255,255,0,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.5" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="2">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{08181f49-6eb5-456a-af7a-86ab0d1cb0eb}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="143,207,79,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.5" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="3">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{b4c357b4-a6ac-410b-9ca7-3034d6ad3a1f}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,175,79,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.5" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="4">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{71ab860f-96cf-41f5-a1f7-fec0abaa92e9}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,127,255,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.5" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="5">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{fbe41f94-f588-4c2b-a100-b0306f60384d}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="199,199,199,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.26" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" enabled="1" id="{593b969b-6e67-442d-884a-b1df1599106f}" locked="0" pass="0">
          <Option type="Map">
            <Option value="0" type="QString" name="align_dash_pattern"/>
            <Option value="square" type="QString" name="capstyle"/>
            <Option value="5;2" type="QString" name="customdash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
            <Option value="MM" type="QString" name="customdash_unit"/>
            <Option value="0" type="QString" name="dash_pattern_offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
            <Option value="0" type="QString" name="draw_inside_polygon"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="35,35,35,255" type="QString" name="line_color"/>
            <Option value="solid" type="QString" name="line_style"/>
            <Option value="0.26" type="QString" name="line_width"/>
            <Option value="MM" type="QString" name="line_width_unit"/>
            <Option value="0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="0" type="QString" name="ring_filter"/>
            <Option value="0" type="QString" name="trim_distance_end"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_end_unit"/>
            <Option value="0" type="QString" name="trim_distance_start"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
            <Option value="MM" type="QString" name="trim_distance_start_unit"/>
            <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
            <Option value="0" type="QString" name="use_custom_dash"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontKerning="1" forcedItalic="0" fontLetterSpacing="0" textOpacity="1" previewBkgrdColor="255,255,255,255" fontWeight="50" fontUnderline="0" fontFamily="Arial" blendMode="0" textColor="0,0,0,255" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontItalic="0" allowHtml="0" legendString="Aa" fontStrikeout="0" namedStyle="Standard" multilineHeightUnit="Percentage" fontSizeUnit="RenderMetersInMapUnits" fieldName="kuerzel+ ' ' + left(coalesce(charakt1, ' ') + ' ', 1) + ' ' + left(coalesce(charakt2, ' ') + ' ', 1) + ' - '+ format_number( station , 2)" multilineHeight="1" capitalization="0" textOrientation="horizontal" fontSize="0.25" fontWordSpacing="0" isExpression="1" useSubstitutions="0" forcedBold="0">
        <families/>
        <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferDraw="0" bufferColor="255,255,255,255" bufferJoinStyle="128" bufferNoFill="1" bufferOpacity="1" bufferSize="1" bufferBlendMode="0" bufferSizeUnits="MM"/>
        <text-mask maskJoinStyle="128" maskSizeUnits="MM" maskOpacity="1" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskEnabled="0" maskSize="0.5" maskedSymbolLayers="" maskType="0"/>
        <background shapeRotationType="0" shapeSizeX="0.29999999999999999" shapeFillColor="255,255,255,255" shapeBorderWidth="0" shapeBorderColor="128,128,128,255" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeType="0" shapeDraw="1" shapeRadiiX="0" shapeSVGFile="" shapeJoinStyle="64" shapeRotation="0" shapeRadiiUnit="MM" shapeSizeType="0" shapeRadiiY="0" shapeSizeUnit="RenderMetersInMapUnits" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeBlendMode="0" shapeSizeY="0.01" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeOffsetUnit="MM" shapeOpacity="1">
          <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="marker" is_animated="0" alpha="1" name="markerSymbol">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" enabled="1" id="" locked="0" pass="0">
              <Option type="Map">
                <Option value="0" type="QString" name="angle"/>
                <Option value="square" type="QString" name="cap_style"/>
                <Option value="164,113,88,255" type="QString" name="color"/>
                <Option value="1" type="QString" name="horizontal_anchor_point"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="circle" type="QString" name="name"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="35,35,35,255" type="QString" name="outline_color"/>
                <Option value="solid" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="outline_width_map_unit_scale"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="diameter" type="QString" name="scale_method"/>
                <Option value="2" type="QString" name="size"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="size_map_unit_scale"/>
                <Option value="MM" type="QString" name="size_unit"/>
                <Option value="1" type="QString" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="fill" is_animated="0" alpha="1" name="fillSymbol">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleFill" enabled="1" id="" locked="0" pass="0">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
                <Option value="255,255,255,255" type="QString" name="color"/>
                <Option value="bevel" type="QString" name="joinstyle"/>
                <Option value="0,0" type="QString" name="offset"/>
                <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
                <Option value="MM" type="QString" name="offset_unit"/>
                <Option value="128,128,128,255" type="QString" name="outline_color"/>
                <Option value="no" type="QString" name="outline_style"/>
                <Option value="0" type="QString" name="outline_width"/>
                <Option value="MM" type="QString" name="outline_width_unit"/>
                <Option value="solid" type="QString" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" type="QString" name="name"/>
                  <Option name="properties"/>
                  <Option value="collection" type="QString" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowDraw="0" shadowUnder="0" shadowOffsetGlobal="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetAngle="135" shadowOffsetUnit="MM" shadowRadius="0" shadowScale="100" shadowOpacity="0" shadowBlendMode="6" shadowColor="0,0,0,255" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowOffsetDist="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" formatNumbers="0" useMaxLineLengthForAutoWrap="1" multilineAlign="0" leftDirectionSymbol="&lt;" autoWrapLength="0" plussign="0" addDirectionSymbol="0" reverseDirectionSymbol="0" wrapChar="" decimals="3" rightDirectionSymbol=">"/>
      <placement quadOffset="4" geometryGeneratorEnabled="0" overrunDistance="0" centroidWhole="0" lineAnchorType="1" fitInPolygonOnly="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" offsetUnits="MM" distUnits="MM" centroidInside="0" lineAnchorTextPoint="CenterOfText" offsetType="0" geometryGeneratorType="PointGeometry" repeatDistanceUnits="MM" placement="2" priority="5" overrunDistanceUnit="MM" preserveRotation="1" dist="0" yOffset="0" rotationAngle="0" geometryGenerator="" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleOut="-25" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" overlapHandling="AllowOverlapIfRequired" xOffset="0" rotationUnit="AngleDegrees" distMapUnitScale="3x:0,0,0,0,0,0" lineAnchorClipping="1" lineAnchorPercent="1" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" polygonPlacementFlags="2" layerType="LineGeometry" allowDegraded="1" repeatDistance="0"/>
      <rendering fontLimitPixelSize="0" minFeatureSize="0" zIndex="0" drawLabels="1" upsidedownLabels="0" maxNumLabels="2000" scaleMin="1" scaleVisibility="1" obstacleType="1" mergeLines="0" fontMaxPixelSize="10000" labelPerPart="0" limitNumLabels="0" fontMinPixelSize="3" scaleMax="2500" obstacleFactor="1" obstacle="0" unplacedVisibility="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" type="QString" name="name"/>
          <Option type="Map" name="properties">
            <Option type="Map" name="Color">
              <Option value="true" type="bool" name="active"/>
              <Option value="CASE &#xd;&#xa;WHEN min(ZD, ZB, ZS) = 0 THEN '#FF0000'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 1 THEN '#FF7F00'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 2 THEN '#FFFF00'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 3 THEN '#8FCF4F'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 4 THEN '#00AF4F'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 5 THEN '#0000FF'END" type="QString" name="expression"/>
              <Option value="3" type="int" name="type"/>
            </Option>
          </Option>
          <Option value="collection" type="QString" name="type"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" type="QString" name="anchorPoint"/>
          <Option value="0" type="int" name="blendMode"/>
          <Option type="Map" name="ddProperties">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
          <Option value="false" type="bool" name="drawToAllParts"/>
          <Option value="0" type="QString" name="enabled"/>
          <Option value="point_on_exterior" type="QString" name="labelAnchorPoint"/>
          <Option value="&lt;symbol clip_to_extent=&quot;1&quot; frame_rate=&quot;10&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; is_animated=&quot;0&quot; alpha=&quot;1&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; id=&quot;{b18b42e0-bfd4-4b23-9ad3-7870ff7a6339}&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option value=&quot;square&quot; type=&quot;QString&quot; name=&quot;capstyle&quot;/>&lt;Option value=&quot;5;2&quot; type=&quot;QString&quot; name=&quot;customdash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;customdash_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option value=&quot;bevel&quot; type=&quot;QString&quot; name=&quot;joinstyle&quot;/>&lt;Option value=&quot;60,60,60,255&quot; type=&quot;QString&quot; name=&quot;line_color&quot;/>&lt;Option value=&quot;solid&quot; type=&quot;QString&quot; name=&quot;line_style&quot;/>&lt;Option value=&quot;0.3&quot; type=&quot;QString&quot; name=&quot;line_width&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;line_width_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;offset&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;offset_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;ring_filter&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option value=&quot;MM&quot; type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option value=&quot;0&quot; type=&quot;QString&quot; name=&quot;use_custom_dash&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; type=&quot;QString&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; type=&quot;QString&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" type="QString" name="lineSymbol"/>
          <Option value="0" type="double" name="minLength"/>
          <Option value="3x:0,0,0,0,0,0" type="QString" name="minLengthMapUnitScale"/>
          <Option value="MM" type="QString" name="minLengthUnit"/>
          <Option value="0" type="double" name="offsetFromAnchor"/>
          <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromAnchorMapUnitScale"/>
          <Option value="MM" type="QString" name="offsetFromAnchorUnit"/>
          <Option value="0" type="double" name="offsetFromLabel"/>
          <Option value="3x:0,0,0,0,0,0" type="QString" name="offsetFromLabelMapUnitScale"/>
          <Option value="MM" type="QString" name="offsetFromLabelUnit"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <Option type="Map">
      <Option value="copy" type="QString" name="QFieldSync/action"/>
      <Option value="{}" type="QString" name="QFieldSync/attachment_naming"/>
      <Option value="offline" type="QString" name="QFieldSync/cloud_action"/>
      <Option value="" type="QString" name="QFieldSync/geometry_locked_expression"/>
      <Option value="{}" type="QString" name="QFieldSync/photo_naming"/>
      <Option value="{}" type="QString" name="QFieldSync/relationship_maximum_visible"/>
      <Option value="30" type="int" name="QFieldSync/tracking_distance_requirement_minimum_meters"/>
      <Option value="1" type="int" name="QFieldSync/tracking_erroneous_distance_safeguard_maximum_meters"/>
      <Option value="0" type="int" name="QFieldSync/tracking_measurement_type"/>
      <Option value="30" type="int" name="QFieldSync/tracking_time_requirement_interval_seconds"/>
      <Option value="0" type="int" name="QFieldSync/value_map_button_interface_threshold"/>
      <Option type="List" name="dualview/previewExpressions">
        <Option value="&quot;foto_dateiname&quot;" type="QString"/>
      </Option>
      <Option value="0" type="int" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory scaleBasedVisibility="0" lineSizeScale="3x:0,0,0,0,0,0" backgroundAlpha="255" labelPlacementMethod="XHeight" spacing="5" width="15" diagramOrientation="Up" backgroundColor="#ffffff" penColor="#000000" maxScaleDenominator="1e+08" height="15" spacingUnitScale="3x:0,0,0,0,0,0" spacingUnit="MM" direction="0" sizeScale="3x:0,0,0,0,0,0" opacity="1" lineSizeType="MM" minimumSize="0" penWidth="0" sizeType="MM" barWidth="5" minScaleDenominator="0" enabled="0" rotationOffset="270" showAxis="1" penAlpha="255" scaleDependency="Area">
      <fontProperties italic="0" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style="" strikethrough="0" underline="0" bold="0"/>
      <attribute field="" color="#000000" label="" colorOpacity="1"/>
      <axisSymbol>
        <symbol clip_to_extent="1" frame_rate="10" force_rhr="0" type="line" is_animated="0" alpha="1" name="">
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
          <layer class="SimpleLine" enabled="1" id="{26d5e29c-70a1-4856-8db2-a9cb610e286d}" locked="0" pass="0">
            <Option type="Map">
              <Option value="0" type="QString" name="align_dash_pattern"/>
              <Option value="square" type="QString" name="capstyle"/>
              <Option value="5;2" type="QString" name="customdash"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="customdash_map_unit_scale"/>
              <Option value="MM" type="QString" name="customdash_unit"/>
              <Option value="0" type="QString" name="dash_pattern_offset"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="dash_pattern_offset_map_unit_scale"/>
              <Option value="MM" type="QString" name="dash_pattern_offset_unit"/>
              <Option value="0" type="QString" name="draw_inside_polygon"/>
              <Option value="bevel" type="QString" name="joinstyle"/>
              <Option value="35,35,35,255" type="QString" name="line_color"/>
              <Option value="solid" type="QString" name="line_style"/>
              <Option value="0.26" type="QString" name="line_width"/>
              <Option value="MM" type="QString" name="line_width_unit"/>
              <Option value="0" type="QString" name="offset"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
              <Option value="MM" type="QString" name="offset_unit"/>
              <Option value="0" type="QString" name="ring_filter"/>
              <Option value="0" type="QString" name="trim_distance_end"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_end_map_unit_scale"/>
              <Option value="MM" type="QString" name="trim_distance_end_unit"/>
              <Option value="0" type="QString" name="trim_distance_start"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="trim_distance_start_map_unit_scale"/>
              <Option value="MM" type="QString" name="trim_distance_start_unit"/>
              <Option value="0" type="QString" name="tweak_dash_pattern_on_corners"/>
              <Option value="0" type="QString" name="use_custom_dash"/>
              <Option value="3x:0,0,0,0,0,0" type="QString" name="width_map_unit_scale"/>
            </Option>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings dist="0" showAll="1" obstacle="0" linePlacementFlags="18" zIndex="0" placement="2" priority="0">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration/>
  <aliases/>
  <splitPolicies/>
  <defaults/>
  <constraints/>
  <constraintExpressions/>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{b8a6ef63-40f5-4eb6-8b35-d05b36b01f7d}" key="Canvas"/>
    <actionsetting icon="" notificationMessage="" capture="0" id="{bb35f5ca-7e7f-44b7-bfaa-ffea0d960666}" shortTitle="Bild öffnen" action="[%ordner_bild %]/[%'Band'+substr(foto_dateiname,0,5)%]/[%foto_dateiname%]" isEnabledOnlyWhenEditable="0" type="5" name="Bild öffnen">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting icon="" notificationMessage="" capture="0" id="{3a3384dc-9a4e-4d34-909c-74537cee71fa}" shortTitle="" action="from qgis.utils import iface&#xa;from qgis.core import *&#xa;from qgis.gui import QgsMessageBar&#xd;&#xa;import os&#xa;#iface.messageBar().pushMessage(&quot;Error&quot;, str([%video_offset%]), level=Qgis.Critical)&#xa;try:&#xd;&#xa;    from qkan.tools.videoplayer import Videoplayer&#xd;&#xa;    if [%video_offset%] == 0:&#xd;&#xa;        iface.messageBar().pushMessage(&quot;Error&quot;, &quot;Video offset = 0.00 s, bitte in der Attributtabelle prüfen!&quot;, level=Qgis.Critical)&#xd;&#xa;    y=QgsProject.instance().readPath(&quot;./&quot;)&#xd;&#xa;&#xd;&#xa;    file == '[%film_dateiname%]':&#xd;&#xa;    video=file&#xd;&#xa;    #video='[%ordner_video%]'+'/'+'[%film_dateiname%]'&#xd;&#xa;    timecode=[%timecode%]&#xd;&#xa;    time_h=int(timecode/1000000) if timecode>1000000 else 0&#xd;&#xa;    time_m=(int(timecode/10000) if timecode>10000 else 0 )-(time_h*100)&#xd;&#xa;    time_s=(int(timecode/100) if timecode>100 else 0 )-(time_h*10000)-(time_m*100)&#xd;&#xa;&#xd;&#xa;    time = float(time_h/3600+time_m/60+time_s+[%video_offset%])&#xd;&#xa;    window = Videoplayer(video=video, time=time)&#xd;&#xa;    window.show()&#xd;&#xa;    window.open_file()&#xd;&#xa;    window.exec_()&#xa;        &#xa;except ImportError:&#xa;    raise Exception(&#xa;        &quot;The QKan main plugin has to be installed for this to work.&quot;&#xa;     )&#xa;" isEnabledOnlyWhenEditable="0" type="1" name="Video abspielen">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting icon="" notificationMessage="" capture="0" id="{b8a6ef63-40f5-4eb6-8b35-d05b36b01f7d}" shortTitle="Alle Zustandsdaten" action="from qkan.tools.zeige_haltungsschaeden import ShowHausanschlussschaeden&#xd;&#xa;&#xd;&#xa;form = ShowHausanschlussschaeden('[%untersuchleit%]')&#xd;&#xa;form.show()&#xd;&#xa;" isEnabledOnlyWhenEditable="0" type="1" name="Zustandsdaten für alle Hausanschussleitungen anzeigen">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="&quot;video_offset&quot;" sortOrder="1">
    <columns>
      <column hidden="1" width="-1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:/Users/nb9255e/Users/hoettges/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qkan/forms/qkan_untersuchdat_anschlussleitung.ui</editform>
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
    <field editable="1" name="ZB"/>
    <field editable="1" name="ZD"/>
    <field editable="1" name="ZS"/>
    <field editable="1" name="bandnr"/>
    <field editable="1" name="charakt1"/>
    <field editable="1" name="charakt2"/>
    <field editable="1" name="createdat"/>
    <field editable="1" name="film_dateiname"/>
    <field editable="1" name="filmtyp"/>
    <field editable="1" name="foto_dateiname"/>
    <field editable="1" name="id"/>
    <field editable="1" name="inspektionslaenge"/>
    <field editable="1" name="kommentar"/>
    <field editable="1" name="kuerzel"/>
    <field editable="1" name="langtext"/>
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
    <field editable="1" name="stationtext"/>
    <field editable="1" name="streckenschaden"/>
    <field editable="1" name="streckenschaden_lfdnr"/>
    <field editable="1" name="timecode"/>
    <field editable="1" name="untersuchhal"/>
    <field editable="1" name="untersuchleit"/>
    <field editable="1" name="untersuchrichtung"/>
    <field editable="1" name="untersuchtag"/>
    <field editable="1" name="video_ende"/>
    <field editable="1" name="video_offset"/>
    <field editable="1" name="video_start"/>
    <field editable="1" name="videozaehler"/>
  </editable>
  <labelOnTop>
    <field name="ZB" labelOnTop="0"/>
    <field name="ZD" labelOnTop="0"/>
    <field name="ZS" labelOnTop="0"/>
    <field name="bandnr" labelOnTop="0"/>
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
    <field reuseLastValue="0" name="ZB"/>
    <field reuseLastValue="0" name="ZD"/>
    <field reuseLastValue="0" name="ZS"/>
    <field reuseLastValue="0" name="bandnr"/>
    <field reuseLastValue="0" name="charakt1"/>
    <field reuseLastValue="0" name="charakt2"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="film_dateiname"/>
    <field reuseLastValue="0" name="filmtyp"/>
    <field reuseLastValue="0" name="foto_dateiname"/>
    <field reuseLastValue="0" name="id"/>
    <field reuseLastValue="0" name="inspektionslaenge"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="kuerzel"/>
    <field reuseLastValue="0" name="langtext"/>
    <field reuseLastValue="0" name="ordner_bild"/>
    <field reuseLastValue="0" name="ordner_video"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="pos_bis"/>
    <field reuseLastValue="0" name="pos_von"/>
    <field reuseLastValue="0" name="quantnr1"/>
    <field reuseLastValue="0" name="quantnr2"/>
    <field reuseLastValue="0" name="richtung"/>
    <field reuseLastValue="0" name="schoben"/>
    <field reuseLastValue="0" name="schunten"/>
    <field reuseLastValue="0" name="station"/>
    <field reuseLastValue="0" name="stationtext"/>
    <field reuseLastValue="0" name="streckenschaden"/>
    <field reuseLastValue="0" name="streckenschaden_lfdnr"/>
    <field reuseLastValue="0" name="timecode"/>
    <field reuseLastValue="0" name="untersuchhal"/>
    <field reuseLastValue="0" name="untersuchleit"/>
    <field reuseLastValue="0" name="untersuchrichtung"/>
    <field reuseLastValue="0" name="untersuchtag"/>
    <field reuseLastValue="0" name="video_ende"/>
    <field reuseLastValue="0" name="video_offset"/>
    <field reuseLastValue="0" name="video_start"/>
    <field reuseLastValue="0" name="videozaehler"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"foto_dateiname"</previewExpression>
  <mapTip enabled="1"></mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
