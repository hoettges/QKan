<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.30.1-'s-Hertogenbosch" styleCategories="Symbology|Temporal">
  <temporal enabled="1" durationField="" fixedDuration="0" endField="" endExpression=" to_datetime( tanf) +  make_interval( 0,0,0,0,0,5,0)" limitMode="0" durationUnit="min" mode="4" startExpression=" to_datetime( tanf)" accumulate="0" startField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 symbollevels="0" graduatedMethod="GraduatedColor" attr="v" referencescale="-1" enableorderby="0" type="graduatedSymbol" forceraster="0">
    <ranges>
      <range label="bis 0,25 m/s" render="true" symbol="0" lower="0.000000000000000" upper="0.250000000000000"/>
      <range label="0,25 - 0,50 m/s" render="true" symbol="1" lower="0.250000000000000" upper="0.500000000000000"/>
      <range label="0,50 - 1,00 m/s" render="true" symbol="2" lower="0.500000000000000" upper="1.000000000000000"/>
      <range label="1,00 - 1,50 m/s" render="true" symbol="3" lower="1.000000000000000" upper="1.500000000000000"/>
      <range label="1,50 - 2,00 m/s" render="true" symbol="4" lower="1.500000000000000" upper="2.000000000000000"/>
      <range label="über 2,00" render="true" symbol="5" lower="2.000000000000000" upper="10.000000000000000"/>
    </ranges>
    <symbols>
      <symbol type="line" frame_rate="10" is_animated="0" name="0" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@0@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="187,249,255,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="line" frame_rate="10" is_animated="0" name="1" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@1@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="135,172,255,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="line" frame_rate="10" is_animated="0" name="2" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@2@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="84,94,255,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="line" frame_rate="10" is_animated="0" name="3" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@3@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="107,49,196,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="line" frame_rate="10" is_animated="0" name="4" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@4@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="181,24,98,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="line" frame_rate="10" is_animated="0" name="5" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@5@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="255,0,0,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol type="line" frame_rate="10" is_animated="0" name="0" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" locked="0" pass="0" id="{c023eac7-f200-47d1-8fbd-99d3188c4b74}" class="ArrowLine">
          <Option type="Map">
            <Option type="QString" name="arrow_start_width" value="2"/>
            <Option type="QString" name="arrow_start_width_unit" value="MM"/>
            <Option type="QString" name="arrow_start_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="arrow_type" value="0"/>
            <Option type="QString" name="arrow_width" value="2"/>
            <Option type="QString" name="arrow_width_unit" value="MM"/>
            <Option type="QString" name="arrow_width_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_length" value="3"/>
            <Option type="QString" name="head_length_unit" value="MM"/>
            <Option type="QString" name="head_length_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_thickness" value="3"/>
            <Option type="QString" name="head_thickness_unit" value="MM"/>
            <Option type="QString" name="head_thickness_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="head_type" value="0"/>
            <Option type="QString" name="is_curved" value="1"/>
            <Option type="QString" name="is_repeated" value="0"/>
            <Option type="QString" name="offset" value="0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="offset_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="ring_filter" value="0"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="arrowHeadLength">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowHeadThickness">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowStartWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
                <Option type="Map" name="arrowWidth">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="v"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="fill" frame_rate="10" is_animated="0" name="@0@0" alpha="1" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" name="name" value=""/>
                <Option name="properties"/>
                <Option type="QString" name="type" value="collection"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" locked="0" pass="0" id="{81924d9d-e59d-4770-b0c2-4810ecc9e23b}" class="SimpleFill">
              <Option type="Map">
                <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="color" value="0,0,255,255"/>
                <Option type="QString" name="joinstyle" value="bevel"/>
                <Option type="QString" name="offset" value="0,0"/>
                <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
                <Option type="QString" name="offset_unit" value="MM"/>
                <Option type="QString" name="outline_color" value="183,72,75,255"/>
                <Option type="QString" name="outline_style" value="solid"/>
                <Option type="QString" name="outline_width" value="0.26"/>
                <Option type="QString" name="outline_width_unit" value="MM"/>
                <Option type="QString" name="style" value="solid"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <Option type="Map">
        <Option type="QString" name="color1" value="187,249,255,255"/>
        <Option type="QString" name="color2" value="255,0,0,255"/>
        <Option type="QString" name="direction" value="ccw"/>
        <Option type="QString" name="discrete" value="0"/>
        <Option type="QString" name="rampType" value="gradient"/>
        <Option type="QString" name="spec" value="rgb"/>
        <Option type="QString" name="stops" value="0.480769;63,63,255,255;rgb;ccw"/>
      </Option>
    </colorramp>
    <classificationMethod id="Custom">
      <symmetricMode enabled="0" astride="0" symmetrypoint="0"/>
      <labelFormat labelprecision="4" trimtrailingzeroes="1" format="%1 - %2"/>
      <parameters>
        <Option/>
      </parameters>
      <extraInformation/>
    </classificationMethod>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>1</layerGeometryType>
</qgis>
