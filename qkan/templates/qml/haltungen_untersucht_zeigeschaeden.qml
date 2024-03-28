<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.16-Białowieża" styleCategories="Actions|MapTips">
  <attributeactions>
    <defaultAction value="{7f802d16-fd1e-45ac-9683-a33a61fc674b}" key="Canvas"/>
    <actionsetting id="{7f802d16-fd1e-45ac-9683-a33a61fc674b}" action="from qkan.tools.zeige_haltungsschaeden import ShowHaltungsschaeden&#xd;&#xa;&#xd;&#xa;form = ShowHaltungsschaeden('[%haltnam%]', '[%schoben%]', '[%schunten%]')&#xd;&#xa;form.show()&#xd;&#xa;" notificationMessage="" capture="1" shortTitle="Schadensdaten anzeigen" name="Schadensdaten anzeigen" isEnabledOnlyWhenEditable="0" type="1" icon="">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <mapTip>[% haltnam + ' (' + untersuchtag + ')' %]</mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
