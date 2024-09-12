<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyAlgorithm="0" labelsEnabled="1" symbologyReferenceScale="-1" minScale="100000000" simplifyLocal="1" styleCategories="AllStyleCategories" simplifyDrawingHints="0" maxScale="0" simplifyMaxScale="1" version="3.34.7-Prizren" hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal startExpression="to_date(&quot;untersuchtag&quot;)" endExpression="to_date(&quot;untersuchtag&quot;)" enabled="0" durationField="" limitMode="0" startField="" fixedDuration="0" durationUnit="min" accumulate="0" mode="4" endField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <elevation zscale="1" binding="Centroid" clamping="Terrain" extrusionEnabled="0" type="IndividualFeatures" extrusion="0" symbology="Line" zoffset="0" respectLayerSymbol="1" showMarkerSymbolInSurfacePlots="0">
    <data-defined-properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </data-defined-properties>
    <profileLineSymbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{bc392b14-10ff-48a6-a8d5-ea076e3bd34c}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="255,158,23,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.6" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileLineSymbol>
    <profileFillSymbol>
      <symbol is_animated="0" type="fill" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="{41c4e12a-71a1-4849-8633-34c91ff1dd1d}">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,158,23,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="182,113,16,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.2" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileFillSymbol>
    <profileMarkerSymbol>
      <symbol is_animated="0" type="marker" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleMarker" pass="0" id="{7d74216c-f3c3-4e87-9283-de24ab043116}">
          <Option type="Map">
            <Option type="QString" value="0" name="angle"/>
            <Option type="QString" value="square" name="cap_style"/>
            <Option type="QString" value="255,158,23,255" name="color"/>
            <Option type="QString" value="1" name="horizontal_anchor_point"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="diamond" name="name"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="182,113,16,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.2" name="outline_width"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="diameter" name="scale_method"/>
            <Option type="QString" value="3" name="size"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
            <Option type="QString" value="MM" name="size_unit"/>
            <Option type="QString" value="1" name="vertical_anchor_point"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileMarkerSymbol>
  </elevation>
  <renderer-v2 symbollevels="0" type="RuleRenderer" enableorderby="0" forceraster="0" referencescale="-1">
    <rules key="{4c108ca8-1203-477a-9f48-96d4e381b74c}">
      <rule symbol="0" key="{7d940636-afec-4238-8412-8e5bd6db260b}" filter="min(ZD, ZB, ZS) = 1 AND untersuchsch = '60093019' AND untersuchtag = '2019-01-22'" label="Zustandsklasse 1, starker Mangel"/>
      <rule symbol="1" key="{9c39bafb-a521-44a9-a29e-0fb200ff73c2}" filter="min(ZD, ZB, ZS) = 2 AND untersuchsch = '60093019' AND untersuchtag = '2019-01-22'" label="Zustandsklasse 2, mittlerer Mangel"/>
      <rule symbol="2" key="{dbe7c6f4-43a6-47c8-8dd3-f4d395b62016}" filter="min(ZD, ZB, ZS) = 3 AND untersuchsch = '60093019' AND untersuchtag = '2019-01-22'" label="Zustandsklasse 3, leichter Mangel"/>
      <rule symbol="3" key="{857733ab-acb9-405b-aa85-9270d8a95091}" filter="min(ZD, ZB, ZS) = 4 AND untersuchsch = '60093019' AND untersuchtag = '2019-01-22'" label="Zustandsklasse 4, geringfügiger Mangel"/>
      <rule symbol="4" key="{a5aced04-09fd-409a-9f4b-ca71ca17d7bd}" filter="min(ZD, ZB, ZS) = 5 AND untersuchsch = '60093019' AND untersuchtag = '2019-01-22'" label="Zustandsklasse 5, kein Mangel"/>
      <rule symbol="5" key="{06fa0df9-3a60-4a3c-a72c-ca8f10d3ad45}" filter="(min(ZD, ZB, ZS) &lt; 1 OR min(ZD, ZB, ZS) > 5) AND untersuchsch = '60093019' AND untersuchtag = '2019-01-22'"/>
    </rules>
    <symbols>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{3f2947b6-f2b5-4541-abf9-fec74f4e0eb6}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="255,127,0,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.5" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{af73116c-0352-48cd-a0a1-571aba5bf22d}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="255,255,0,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.5" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="2">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{f4811131-853d-4606-be5b-68d9be6c1e03}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="143,207,79,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.5" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="3">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{164c843c-efa1-406a-993e-153110a07ff6}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,175,79,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.5" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="4">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{188cb887-97cf-49ab-bcbb-11f8a18a4631}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,127,255,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.5" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="5">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{6fe62594-f619-47b0-bd2d-8e442f08945d}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="199,199,199,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.26" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
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
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{72903ee8-81eb-4811-8b46-2f4fef7424d4}">
          <Option type="Map">
            <Option type="QString" value="0" name="align_dash_pattern"/>
            <Option type="QString" value="square" name="capstyle"/>
            <Option type="QString" value="5;2" name="customdash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
            <Option type="QString" value="MM" name="customdash_unit"/>
            <Option type="QString" value="0" name="dash_pattern_offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
            <Option type="QString" value="0" name="draw_inside_polygon"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="35,35,35,255" name="line_color"/>
            <Option type="QString" value="solid" name="line_style"/>
            <Option type="QString" value="0.26" name="line_width"/>
            <Option type="QString" value="MM" name="line_width_unit"/>
            <Option type="QString" value="0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0" name="ring_filter"/>
            <Option type="QString" value="0" name="trim_distance_end"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_end_unit"/>
            <Option type="QString" value="0" name="trim_distance_start"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
            <Option type="QString" value="MM" name="trim_distance_start_unit"/>
            <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
            <Option type="QString" value="0" name="use_custom_dash"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontUnderline="0" useSubstitutions="0" forcedBold="0" legendString="Aa" capitalization="0" forcedItalic="0" namedStyle="Standard" fontFamily="Arial" fontItalic="0" allowHtml="0" multilineHeightUnit="Percentage" multilineHeight="1" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" fontSize="0.25" fontWeight="50" textColor="0,0,0,255" fontKerning="1" textOrientation="horizontal" previewBkgrdColor="255,255,255,255" fontWordSpacing="0" textOpacity="1" fontSizeUnit="RenderMetersInMapUnits" isExpression="1" fontStrikeout="0" fieldName="kuerzel+ ' ' + left(coalesce(charakt1, ' ') + ' ', 1) + ' ' + left(coalesce(charakt2, ' ') + ' ', 1)" blendMode="0">
        <families/>
        <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255" bufferSize="1" bufferJoinStyle="128" bufferSizeUnits="MM" bufferDraw="0" bufferOpacity="1" bufferBlendMode="0" bufferNoFill="1"/>
        <text-mask maskSizeUnits="MM" maskSize="0.5" maskType="0" maskedSymbolLayers="" maskOpacity="1" maskEnabled="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskJoinStyle="128"/>
        <background shapeOpacity="1" shapeRadiiY="0" shapeSizeX="0.29999999999999999" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="1" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthUnit="MM" shapeOffsetX="0" shapeFillColor="255,255,255,255" shapeJoinStyle="64" shapeSizeY="0.01" shapeBlendMode="0" shapeSizeUnit="RenderMetersInMapUnits" shapeRadiiUnit="MM" shapeRotationType="0" shapeRotation="0" shapeBorderWidth="0" shapeSVGFile="" shapeType="0" shapeBorderColor="128,128,128,255" shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeType="0" shapeRadiiX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0">
          <symbol is_animated="0" type="marker" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="markerSymbol">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" class="SimpleMarker" pass="0" id="">
              <Option type="Map">
                <Option type="QString" value="0" name="angle"/>
                <Option type="QString" value="square" name="cap_style"/>
                <Option type="QString" value="164,113,88,255" name="color"/>
                <Option type="QString" value="1" name="horizontal_anchor_point"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="circle" name="name"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="35,35,35,255" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0" name="outline_width"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="diameter" name="scale_method"/>
                <Option type="QString" value="2" name="size"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                <Option type="QString" value="MM" name="size_unit"/>
                <Option type="QString" value="1" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol is_animated="0" type="fill" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="fillSymbol">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" class="SimpleFill" pass="0" id="">
              <Option type="Map">
                <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                <Option type="QString" value="255,255,255,255" name="color"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="128,128,128,255" name="outline_color"/>
                <Option type="QString" value="no" name="outline_style"/>
                <Option type="QString" value="0" name="outline_width"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="solid" name="style"/>
              </Option>
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
        <shadow shadowUnder="0" shadowOffsetDist="1" shadowBlendMode="6" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowColor="0,0,0,255" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0" shadowRadius="0" shadowScale="100"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format addDirectionSymbol="0" rightDirectionSymbol=">" formatNumbers="0" decimals="3" plussign="0" multilineAlign="0" placeDirectionSymbol="0" wrapChar="" autoWrapLength="0" useMaxLineLengthForAutoWrap="1" reverseDirectionSymbol="0" leftDirectionSymbol="&lt;"/>
      <placement overlapHandling="AllowOverlapIfRequired" rotationAngle="0" priority="5" dist="0" maxCurvedCharAngleOut="-25" repeatDistance="0" lineAnchorClipping="1" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="9" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" layerType="LineGeometry" distMapUnitScale="3x:0,0,0,0,0,0" placement="2" lineAnchorTextPoint="CenterOfText" geometryGenerator="" repeatDistanceUnits="MM" overrunDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM" maxCurvedCharAngleIn="25" distUnits="MM" centroidWhole="0" quadOffset="4" centroidInside="0" overrunDistanceUnit="MM" polygonPlacementFlags="2" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" lineAnchorType="1" allowDegraded="1" offsetType="0" geometryGeneratorEnabled="0" lineAnchorPercent="1" geometryGeneratorType="PointGeometry" fitInPolygonOnly="0" preserveRotation="1" xOffset="0" rotationUnit="AngleDegrees" yOffset="0"/>
      <rendering labelPerPart="0" fontMinPixelSize="3" obstacleType="1" fontMaxPixelSize="10000" obstacleFactor="1" limitNumLabels="0" scaleMin="1" minFeatureSize="0" obstacle="0" drawLabels="1" scaleVisibility="1" mergeLines="0" unplacedVisibility="0" fontLimitPixelSize="0" zIndex="0" scaleMax="2500" maxNumLabels="2000" upsidedownLabels="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" value="" name="name"/>
          <Option type="Map" name="properties">
            <Option type="Map" name="Color">
              <Option type="bool" value="true" name="active"/>
              <Option type="QString" value="CASE &#xd;&#xa;WHEN min(ZD, ZB, ZS) = 0 THEN '#FF0000'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 1 THEN '#FF7F00'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 2 THEN '#FFFF00'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 3 THEN '#8FCF4F'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 4 THEN '#00AF4F'&#xd;&#xa;WHEN min(ZD, ZB, ZS) = 5 THEN '#0000FF'END" name="expression"/>
              <Option type="int" value="3" name="type"/>
            </Option>
          </Option>
          <Option type="QString" value="collection" name="type"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
          <Option type="int" value="0" name="blendMode"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
          <Option type="bool" value="false" name="drawToAllParts"/>
          <Option type="QString" value="0" name="enabled"/>
          <Option type="QString" value="point_on_exterior" name="labelAnchorPoint"/>
          <Option type="QString" value="&lt;symbol is_animated=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot; frame_rate=&quot;10&quot; force_rhr=&quot;0&quot; name=&quot;symbol&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer enabled=&quot;1&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot; id=&quot;{772ac1c1-97cd-48d7-86ad-41895e415b93}&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;square&quot; name=&quot;capstyle&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;5;2&quot; name=&quot;customdash&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;customdash_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;bevel&quot; name=&quot;joinstyle&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;60,60,60,255&quot; name=&quot;line_color&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;solid&quot; name=&quot;line_style&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0.3&quot; name=&quot;line_width&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;line_width_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;offset&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;offset_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;ring_filter&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;trim_distance_end&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;trim_distance_start&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;use_custom_dash&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
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
  <customproperties>
    <Option type="Map">
      <Option type="QString" value="copy" name="QFieldSync/action"/>
      <Option type="QString" value="{}" name="QFieldSync/attachment_naming"/>
      <Option type="QString" value="offline" name="QFieldSync/cloud_action"/>
      <Option type="QString" value="" name="QFieldSync/geometry_locked_expression"/>
      <Option type="QString" value="{}" name="QFieldSync/photo_naming"/>
      <Option type="QString" value="{}" name="QFieldSync/relationship_maximum_visible"/>
      <Option type="int" value="30" name="QFieldSync/tracking_distance_requirement_minimum_meters"/>
      <Option type="int" value="1" name="QFieldSync/tracking_erroneous_distance_safeguard_maximum_meters"/>
      <Option type="int" value="0" name="QFieldSync/tracking_measurement_type"/>
      <Option type="int" value="30" name="QFieldSync/tracking_time_requirement_interval_seconds"/>
      <Option type="int" value="0" name="QFieldSync/value_map_button_interface_threshold"/>
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;foto_dateiname&quot;"/>
      </Option>
      <Option type="int" value="0" name="embeddedWidgets/count"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory opacity="1" minScaleDenominator="0" enabled="0" labelPlacementMethod="XHeight" maxScaleDenominator="1e+08" barWidth="5" backgroundAlpha="255" backgroundColor="#ffffff" diagramOrientation="Up" penWidth="0" lineSizeScale="3x:0,0,0,0,0,0" direction="0" sizeScale="3x:0,0,0,0,0,0" showAxis="1" scaleDependency="Area" spacingUnitScale="3x:0,0,0,0,0,0" minimumSize="0" penColor="#000000" lineSizeType="MM" penAlpha="255" rotationOffset="270" spacing="5" width="15" spacingUnit="MM" scaleBasedVisibility="0" height="15" sizeType="MM">
      <fontProperties bold="0" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" strikethrough="0" italic="0" underline="0" style=""/>
      <attribute color="#000000" label="" field="" colorOpacity="1"/>
      <axisSymbol>
        <symbol is_animated="0" type="line" alpha="1" clip_to_extent="1" frame_rate="10" force_rhr="0" name="">
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
          <layer enabled="1" locked="0" class="SimpleLine" pass="0" id="{810f52df-0bec-4385-aaa4-f2ee6791429b}">
            <Option type="Map">
              <Option type="QString" value="0" name="align_dash_pattern"/>
              <Option type="QString" value="square" name="capstyle"/>
              <Option type="QString" value="5;2" name="customdash"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale"/>
              <Option type="QString" value="MM" name="customdash_unit"/>
              <Option type="QString" value="0" name="dash_pattern_offset"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale"/>
              <Option type="QString" value="MM" name="dash_pattern_offset_unit"/>
              <Option type="QString" value="0" name="draw_inside_polygon"/>
              <Option type="QString" value="bevel" name="joinstyle"/>
              <Option type="QString" value="35,35,35,255" name="line_color"/>
              <Option type="QString" value="solid" name="line_style"/>
              <Option type="QString" value="0.26" name="line_width"/>
              <Option type="QString" value="MM" name="line_width_unit"/>
              <Option type="QString" value="0" name="offset"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
              <Option type="QString" value="MM" name="offset_unit"/>
              <Option type="QString" value="0" name="ring_filter"/>
              <Option type="QString" value="0" name="trim_distance_end"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale"/>
              <Option type="QString" value="MM" name="trim_distance_end_unit"/>
              <Option type="QString" value="0" name="trim_distance_start"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale"/>
              <Option type="QString" value="MM" name="trim_distance_start_unit"/>
              <Option type="QString" value="0" name="tweak_dash_pattern_on_corners"/>
              <Option type="QString" value="0" name="use_custom_dash"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="width_map_unit_scale"/>
            </Option>
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings obstacle="0" linePlacementFlags="18" placement="2" priority="0" showAll="1" dist="0" zIndex="0">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector" showLabelLegend="0"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="NoFlag" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="untersuchsch">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="id">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="untersuchtag">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="bandnr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="videozaehler">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="timecode">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="langtext">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="kuerzel">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="charakt1">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="charakt2">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="quantnr1">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="quantnr2">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="streckenschaden">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="streckenschaden_lfdnr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="pos_von">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="pos_bis">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="vertikale_lage">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="inspektionslaenge">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="bereich">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="foto_dateiname">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="ordner">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="film_dateiname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="ordner_video">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="filmtyp">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="video_start">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="video_ende">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="ZD">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="ZB">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="ZS">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="createdat">
      <editWidget type="DateTime">
        <config>
          <Option type="Map">
            <Option type="bool" value="true" name="allow_null"/>
            <Option type="bool" value="true" name="calendar_popup"/>
            <Option type="QString" value="dd.MM.yyyy HH:mm:ss" name="display_format"/>
            <Option type="QString" value="yyyy-MM-dd HH:mm:ss" name="field_format"/>
            <Option type="bool" value="false" name="field_iso_format"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="pk" name=""/>
    <alias index="1" field="untersuchsch" name="Name"/>
    <alias index="2" field="id" name="Inspektionsnr"/>
    <alias index="3" field="untersuchtag" name="Inspektionsdatum"/>
    <alias index="4" field="bandnr" name=""/>
    <alias index="5" field="videozaehler" name="Videozähler"/>
    <alias index="6" field="timecode" name="Zeitstempel"/>
    <alias index="7" field="langtext" name=""/>
    <alias index="8" field="kuerzel" name="Kürzel"/>
    <alias index="9" field="charakt1" name=""/>
    <alias index="10" field="charakt2" name=""/>
    <alias index="11" field="quantnr1" name=""/>
    <alias index="12" field="quantnr2" name=""/>
    <alias index="13" field="streckenschaden" name="Streckenschaden"/>
    <alias index="14" field="streckenschaden_lfdnr" name="Streckenschäden Laufnummer"/>
    <alias index="15" field="pos_von" name="Position Anfang"/>
    <alias index="16" field="pos_bis" name="Position Ende"/>
    <alias index="17" field="vertikale_lage" name="Länge vertikal"/>
    <alias index="18" field="inspektionslaenge" name="Inspektionslänge"/>
    <alias index="19" field="bereich" name="Bereich"/>
    <alias index="20" field="foto_dateiname" name="Dateiname Foto"/>
    <alias index="21" field="ordner" name="Ordner"/>
    <alias index="22" field="film_dateiname" name=""/>
    <alias index="23" field="ordner_video" name=""/>
    <alias index="24" field="filmtyp" name=""/>
    <alias index="25" field="video_start" name=""/>
    <alias index="26" field="video_ende" name=""/>
    <alias index="27" field="ZD" name=""/>
    <alias index="28" field="ZB" name=""/>
    <alias index="29" field="ZS" name=""/>
    <alias index="30" field="kommentar" name=""/>
    <alias index="31" field="createdat" name="bearbeitet"/>
  </aliases>
  <splitPolicies>
    <policy policy="Duplicate" field="pk"/>
    <policy policy="Duplicate" field="untersuchsch"/>
    <policy policy="Duplicate" field="id"/>
    <policy policy="Duplicate" field="untersuchtag"/>
    <policy policy="Duplicate" field="bandnr"/>
    <policy policy="Duplicate" field="videozaehler"/>
    <policy policy="Duplicate" field="timecode"/>
    <policy policy="Duplicate" field="langtext"/>
    <policy policy="Duplicate" field="kuerzel"/>
    <policy policy="Duplicate" field="charakt1"/>
    <policy policy="Duplicate" field="charakt2"/>
    <policy policy="Duplicate" field="quantnr1"/>
    <policy policy="Duplicate" field="quantnr2"/>
    <policy policy="Duplicate" field="streckenschaden"/>
    <policy policy="Duplicate" field="streckenschaden_lfdnr"/>
    <policy policy="Duplicate" field="pos_von"/>
    <policy policy="Duplicate" field="pos_bis"/>
    <policy policy="Duplicate" field="vertikale_lage"/>
    <policy policy="Duplicate" field="inspektionslaenge"/>
    <policy policy="Duplicate" field="bereich"/>
    <policy policy="Duplicate" field="foto_dateiname"/>
    <policy policy="Duplicate" field="ordner"/>
    <policy policy="Duplicate" field="film_dateiname"/>
    <policy policy="Duplicate" field="ordner_video"/>
    <policy policy="Duplicate" field="filmtyp"/>
    <policy policy="Duplicate" field="video_start"/>
    <policy policy="Duplicate" field="video_ende"/>
    <policy policy="Duplicate" field="ZD"/>
    <policy policy="Duplicate" field="ZB"/>
    <policy policy="Duplicate" field="ZS"/>
    <policy policy="Duplicate" field="kommentar"/>
    <policy policy="Duplicate" field="createdat"/>
  </splitPolicies>
  <defaults>
    <default applyOnUpdate="0" expression="" field="pk"/>
    <default applyOnUpdate="0" expression="" field="untersuchsch"/>
    <default applyOnUpdate="0" expression="" field="id"/>
    <default applyOnUpdate="0" expression="" field="untersuchtag"/>
    <default applyOnUpdate="0" expression="" field="bandnr"/>
    <default applyOnUpdate="0" expression="" field="videozaehler"/>
    <default applyOnUpdate="0" expression="" field="timecode"/>
    <default applyOnUpdate="0" expression="" field="langtext"/>
    <default applyOnUpdate="0" expression="" field="kuerzel"/>
    <default applyOnUpdate="0" expression="" field="charakt1"/>
    <default applyOnUpdate="0" expression="" field="charakt2"/>
    <default applyOnUpdate="0" expression="" field="quantnr1"/>
    <default applyOnUpdate="0" expression="" field="quantnr2"/>
    <default applyOnUpdate="0" expression="" field="streckenschaden"/>
    <default applyOnUpdate="0" expression="" field="streckenschaden_lfdnr"/>
    <default applyOnUpdate="0" expression="" field="pos_von"/>
    <default applyOnUpdate="0" expression="" field="pos_bis"/>
    <default applyOnUpdate="0" expression="" field="vertikale_lage"/>
    <default applyOnUpdate="0" expression="" field="inspektionslaenge"/>
    <default applyOnUpdate="0" expression="" field="bereich"/>
    <default applyOnUpdate="0" expression="" field="foto_dateiname"/>
    <default applyOnUpdate="0" expression="" field="ordner"/>
    <default applyOnUpdate="0" expression="" field="film_dateiname"/>
    <default applyOnUpdate="0" expression="" field="ordner_video"/>
    <default applyOnUpdate="0" expression="" field="filmtyp"/>
    <default applyOnUpdate="0" expression="" field="video_start"/>
    <default applyOnUpdate="0" expression="" field="video_ende"/>
    <default applyOnUpdate="0" expression="" field="ZD"/>
    <default applyOnUpdate="0" expression="" field="ZB"/>
    <default applyOnUpdate="0" expression="" field="ZS"/>
    <default applyOnUpdate="0" expression="" field="kommentar"/>
    <default applyOnUpdate="0" expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')" field="createdat"/>
  </defaults>
  <constraints>
    <constraint unique_strength="2" notnull_strength="2" exp_strength="0" constraints="3" field="pk"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="untersuchsch"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="id"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="untersuchtag"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="bandnr"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="videozaehler"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="timecode"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="langtext"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="kuerzel"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="charakt1"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="charakt2"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="quantnr1"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="quantnr2"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="streckenschaden"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="streckenschaden_lfdnr"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="pos_von"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="pos_bis"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="vertikale_lage"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="inspektionslaenge"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="bereich"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="foto_dateiname"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="ordner"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="film_dateiname"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="ordner_video"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="filmtyp"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="video_start"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="video_ende"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="ZD"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="ZB"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="ZS"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="kommentar"/>
    <constraint unique_strength="0" notnull_strength="0" exp_strength="0" constraints="0" field="createdat"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="pk" desc=""/>
    <constraint exp="" field="untersuchsch" desc=""/>
    <constraint exp="" field="id" desc=""/>
    <constraint exp="" field="untersuchtag" desc=""/>
    <constraint exp="" field="bandnr" desc=""/>
    <constraint exp="" field="videozaehler" desc=""/>
    <constraint exp="" field="timecode" desc=""/>
    <constraint exp="" field="langtext" desc=""/>
    <constraint exp="" field="kuerzel" desc=""/>
    <constraint exp="" field="charakt1" desc=""/>
    <constraint exp="" field="charakt2" desc=""/>
    <constraint exp="" field="quantnr1" desc=""/>
    <constraint exp="" field="quantnr2" desc=""/>
    <constraint exp="" field="streckenschaden" desc=""/>
    <constraint exp="" field="streckenschaden_lfdnr" desc=""/>
    <constraint exp="" field="pos_von" desc=""/>
    <constraint exp="" field="pos_bis" desc=""/>
    <constraint exp="" field="vertikale_lage" desc=""/>
    <constraint exp="" field="inspektionslaenge" desc=""/>
    <constraint exp="" field="bereich" desc=""/>
    <constraint exp="" field="foto_dateiname" desc=""/>
    <constraint exp="" field="ordner" desc=""/>
    <constraint exp="" field="film_dateiname" desc=""/>
    <constraint exp="" field="ordner_video" desc=""/>
    <constraint exp="" field="filmtyp" desc=""/>
    <constraint exp="" field="video_start" desc=""/>
    <constraint exp="" field="video_ende" desc=""/>
    <constraint exp="" field="ZD" desc=""/>
    <constraint exp="" field="ZB" desc=""/>
    <constraint exp="" field="ZS" desc=""/>
    <constraint exp="" field="kommentar" desc=""/>
    <constraint exp="" field="createdat" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting notificationMessage="" type="5" shortTitle="Bild öffnen" capture="0" icon="" action="[%ordner_bild %]/[%'Band'+substr(foto_dateiname,0,5)%]/[%foto_dateiname%]" name="Bild öffnen" id="{bb35f5ca-7e7f-44b7-bfaa-ffea0d960666}" isEnabledOnlyWhenEditable="0">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting notificationMessage="" type="1" shortTitle="" capture="0" icon="" action="from qgis.utils import iface&#xa;from qgis.core import *&#xa;from qgis.gui import QgsMessageBar&#xd;&#xa;import os&#xa;#iface.messageBar().pushMessage(&quot;Error&quot;, str([%video_offset%]), level=Qgis.Critical)&#xa;try:&#xa;    from qkan.tools.videoplayer import Videoplayer&#xa;    if [%video_offset%] == 0:&#xa;        iface.messageBar().pushMessage(&quot;Error&quot;, &quot;Video offset = 0.00 s, bitte in der Attributtabelle prüfen!&quot;, level=Qgis.Critical)&#xa;    y=QgsProject.instance().readPath(&quot;./&quot;)&#xd;&#xa;&#xd;&#xa;    for root, dirs, files in os.walk('[%ordner_video%]'):&#xd;&#xa;        for file in files:&#xd;&#xa;            if file == '[%film_dateiname%]':&#xd;&#xa;                video=file&#xd;&#xa;                #video='[%ordner_video%]'+'/'+'[%film_dateiname%]'&#xa;                timecode=[%timecode%]&#xa;                time_h=int(timecode/1000000) if timecode>1000000 else 0&#xa;                time_m=(int(timecode/10000) if timecode>10000 else 0 )-(time_h*100)&#xa;                time_s=(int(timecode/100) if timecode>100 else 0 )-(time_h*10000)-(time_m*100)&#xa;&#xa;                time = float(time_h/3600+time_m/60+time_s+[%video_offset%])&#xa;                window = Videoplayer(video=video, time=time)&#xa;                window.show()&#xa;                window.open_file()&#xa;                window.exec_()&#xa;        &#xa;except ImportError:&#xa;    raise Exception(&#xa;        &quot;The QKan main plugin has to be installed for this to work.&quot;&#xa;     )&#xa;" name="Video abspielen" id="{3a3384dc-9a4e-4d34-909c-74537cee71fa}" isEnabledOnlyWhenEditable="0">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting notificationMessage="" type="1" shortTitle="Alle Zustandsdaten" capture="0" icon="" action="from qkan.tools.zeige_untersuchungsdaten import ShowSchachtschaeden&#xd;&#xa;&#xd;&#xa;form = ShowSchachtschaeden('[%untersuchsch%]')&#xd;&#xa;form.show_selected()&#xd;&#xa;del form&#xd;&#xa;" name="Zustandsdaten für alle Schächte anzeigen" id="{7a5bc868-254a-45ab-a059-1ef3bf749701}" isEnabledOnlyWhenEditable="0">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" type="field" hidden="0" name="pk"/>
      <column width="-1" type="field" hidden="0" name="untersuchsch"/>
      <column width="-1" type="field" hidden="0" name="id"/>
      <column width="-1" type="field" hidden="0" name="untersuchtag"/>
      <column width="-1" type="field" hidden="0" name="videozaehler"/>
      <column width="-1" type="field" hidden="0" name="timecode"/>
      <column width="-1" type="field" hidden="0" name="kuerzel"/>
      <column width="-1" type="field" hidden="0" name="charakt1"/>
      <column width="-1" type="field" hidden="0" name="charakt2"/>
      <column width="-1" type="field" hidden="0" name="quantnr1"/>
      <column width="100" type="field" hidden="0" name="quantnr2"/>
      <column width="116" type="field" hidden="0" name="streckenschaden"/>
      <column width="200" type="field" hidden="0" name="pos_von"/>
      <column width="-1" type="field" hidden="0" name="pos_bis"/>
      <column width="-1" type="field" hidden="0" name="bereich"/>
      <column width="100" type="field" hidden="0" name="foto_dateiname"/>
      <column width="501" type="field" hidden="0" name="ordner"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" type="field" hidden="0" name="streckenschaden_lfdnr"/>
      <column width="-1" type="field" hidden="0" name="vertikale_lage"/>
      <column width="-1" type="field" hidden="0" name="inspektionslaenge"/>
      <column width="-1" type="field" hidden="0" name="ZD"/>
      <column width="-1" type="field" hidden="0" name="ZB"/>
      <column width="-1" type="field" hidden="0" name="ZS"/>
      <column width="-1" type="field" hidden="0" name="bandnr"/>
      <column width="-1" type="field" hidden="0" name="kommentar"/>
      <column width="-1" type="field" hidden="0" name="langtext"/>
      <column width="-1" type="field" hidden="0" name="film_dateiname"/>
      <column width="-1" type="field" hidden="0" name="ordner_video"/>
      <column width="-1" type="field" hidden="0" name="filmtyp"/>
      <column width="-1" type="field" hidden="0" name="video_start"/>
      <column width="-1" type="field" hidden="0" name="video_ende"/>
      <column width="-1" type="field" hidden="0" name="createdat"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">C:\Users\nb9255e\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qkan\forms\qkan_untersuchdat_schacht.ui</editform>
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
    <field editable="1" name="bereich"/>
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
    <field editable="1" name="ordner"/>
    <field editable="1" name="ordner_video"/>
    <field editable="1" name="pk"/>
    <field editable="1" name="pos_bis"/>
    <field editable="1" name="pos_von"/>
    <field editable="1" name="quantnr1"/>
    <field editable="1" name="quantnr2"/>
    <field editable="1" name="streckenschaden"/>
    <field editable="1" name="streckenschaden_lfdnr"/>
    <field editable="1" name="timecode"/>
    <field editable="1" name="untersuchsch"/>
    <field editable="1" name="untersuchtag"/>
    <field editable="1" name="vertikale_lage"/>
    <field editable="1" name="video_ende"/>
    <field editable="1" name="video_start"/>
    <field editable="1" name="videozaehler"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="ZB"/>
    <field labelOnTop="0" name="ZD"/>
    <field labelOnTop="0" name="ZS"/>
    <field labelOnTop="0" name="bandnr"/>
    <field labelOnTop="0" name="bereich"/>
    <field labelOnTop="0" name="charakt1"/>
    <field labelOnTop="0" name="charakt2"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="film_dateiname"/>
    <field labelOnTop="0" name="filmtyp"/>
    <field labelOnTop="0" name="foto_dateiname"/>
    <field labelOnTop="0" name="id"/>
    <field labelOnTop="0" name="inspektionslaenge"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="kuerzel"/>
    <field labelOnTop="0" name="langtext"/>
    <field labelOnTop="0" name="ordner"/>
    <field labelOnTop="0" name="ordner_video"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="pos_bis"/>
    <field labelOnTop="0" name="pos_von"/>
    <field labelOnTop="0" name="quantnr1"/>
    <field labelOnTop="0" name="quantnr2"/>
    <field labelOnTop="0" name="streckenschaden"/>
    <field labelOnTop="0" name="streckenschaden_lfdnr"/>
    <field labelOnTop="0" name="timecode"/>
    <field labelOnTop="0" name="untersuchsch"/>
    <field labelOnTop="0" name="untersuchtag"/>
    <field labelOnTop="0" name="vertikale_lage"/>
    <field labelOnTop="0" name="video_ende"/>
    <field labelOnTop="0" name="video_start"/>
    <field labelOnTop="0" name="videozaehler"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="ZB"/>
    <field reuseLastValue="0" name="ZD"/>
    <field reuseLastValue="0" name="ZS"/>
    <field reuseLastValue="0" name="bandnr"/>
    <field reuseLastValue="0" name="bereich"/>
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
    <field reuseLastValue="0" name="ordner"/>
    <field reuseLastValue="0" name="ordner_video"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="pos_bis"/>
    <field reuseLastValue="0" name="pos_von"/>
    <field reuseLastValue="0" name="quantnr1"/>
    <field reuseLastValue="0" name="quantnr2"/>
    <field reuseLastValue="0" name="streckenschaden"/>
    <field reuseLastValue="0" name="streckenschaden_lfdnr"/>
    <field reuseLastValue="0" name="timecode"/>
    <field reuseLastValue="0" name="untersuchsch"/>
    <field reuseLastValue="0" name="untersuchtag"/>
    <field reuseLastValue="0" name="vertikale_lage"/>
    <field reuseLastValue="0" name="video_ende"/>
    <field reuseLastValue="0" name="video_start"/>
    <field reuseLastValue="0" name="videozaehler"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"foto_dateiname"</previewExpression>
  <mapTip enabled="1"></mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
