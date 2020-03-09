INSERT into schaechte (
    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche)
VALUES (
    'J1', 96, 96 + 4, 0)

INSERT into schaechte (
    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche)
VALUES (
    'J3', 93, 93 + 4, 0)

INSERT into schaechte (
    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche)
VALUES (
    'J2', 90, 90 + 4, 0)

INSERT into schaechte (
    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche)
VALUES (
    'J4', 88, 88 + 4, 0)

UPDATE schaechte SET (
    xsch, ysch, geom, geop) =
(   7289.720, 6573.209, CastToMultiPolygon(MakePolygon(MakeCircle(7289.720, 6573.209, 1.0, 25832))), MakePoint(7289.720,6573.209,25832))
WHERE schnam = 'J1'

UPDATE schaechte SET (
    xsch, ysch, geom, geop) =
(   3302.181, 6635.514, CastToMultiPolygon(MakePolygon(MakeCircle(3302.181, 6635.514, 1.0, 25832))), MakePoint(3302.181,6635.514,25832))
WHERE schnam = 'J3'

UPDATE schaechte SET (
    xsch, ysch, geom, geop) =
(   7289.720, 1121.495, CastToMultiPolygon(MakePolygon(MakeCircle(7289.720, 1121.495, 1.0, 25832))), MakePoint(7289.720,1121.495,25832))
WHERE schnam = 'J2'

UPDATE schaechte SET (
    xsch, ysch, geom, geop) =
(   3302.181, 1121.495, CastToMultiPolygon(MakePolygon(MakeCircle(3302.181, 1121.495, 1.0, 25832))), MakePoint(3302.181,1121.495,25832))
WHERE schnam = 'J4'

UPDATE schaechte SET (
    xsch, ysch, geom, geop) =
(   -264.798, 1121.495, CastToMultiPolygon(MakePolygon(MakeCircle(-264.798, 1121.495, 1.0, 25832))), MakePoint(-264.798,1121.495,25832))
WHERE schnam = 'Out1'

