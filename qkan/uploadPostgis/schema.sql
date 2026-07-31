-- Anmerkungen:
-- Tabellen, die im Projekt Jülich fehlen:
--  - fotos
--  - videos
--  - sel_schaechte
--  - sel_haltungen
--  - sel_flaechen

-- Schema qkan erstellen






-- database_create_notizen: "
CREATE TABLE IF NOT EXISTS qkan.notizen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    notiz TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING) )

;

TABLESPACE pg_default;

-- database_createspatialindex_notizen_geom: "
CREATE INDEX idx_notizen_geom ON qkan.notizen USING GIST (geom);

-- database_create_haltungen: "
CREATE TABLE IF NOT EXISTS qkan.haltungen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    haltnam TEXT,
    schoben TEXT,                                   /* join schaechte.schnam */
    schunten TEXT,                                  /* join schaechte.schnam */
    hoehe NUMERIC(4,0),                             /* Profilhoehe (mm) */
    breite NUMERIC(4,0),                            /* Profilbreite (mm) */
    laenge NUMERIC(7,3),                            /* abweichende Haltungslänge (m) */
    aussendurchmesser NUMERIC(4,0),
    sohleoben NUMERIC(7,3),                         /* Sohlhöhe oben (m) */
    sohleunten NUMERIC(7,3),                        /* Sohlhöhe unten (m) */
    baujahr INT,
    eigentum TEXT,                                  /* join eigentum.name */
    teilgebiet TEXT,                                /* join teilgebiet.tgnam */
    strasse TEXT,                                   /* für ISYBAU benötigt */
    profilnam TEXT DEFAULT 'Kreisquerschnitt',      /* join profile.profilnam */
    entwart TEXT DEFAULT 'Regenwasser',             /* join entwaesserungsarten.bezeichnung */
    material TEXT,                                  /* join material.bezeichnung */
    profilauskleidung TEXT,
    innenmaterial TEXT,
    ks NUMERIC(7,4) DEFAULT 1.5,                    /* abs. Rauheit (mm, Prandtl-Colebrook) */
    haltungstyp TEXT DEFAULT 'Haltung',             /* join haltungstypen.bezeichnung */
    simstatus TEXT DEFAULT 'vorhanden',             /* join simulationsstatus.bezeichnung */
    rwanschluss INTEGER DEFAULT 1,                  /* soll bei TEZG-Erstellung berücksichtigt werden */
    druckdicht INTEGER DEFAULT 0,                   /* Druckleitung */
    xschob NUMERIC(11,3),
    yschob NUMERIC(11,3),
    xschun NUMERIC(11,3),
    yschun NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;

-- database_create_einleit: "
CREATE TABLE IF NOT EXISTS qkan.einleit (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,               /* join haltungen.haltnam */
    schnam TEXT,                /* join schaechte.schnam */
    teilgebiet TEXT,            /* join teilgebiet.tgnam  */
    zufluss NUMERIC(8,2),       /* Zufluss (l/s) */
    ew NUMERIC(8,2),            /* Einwohner */
    einzugsgebiet TEXT,         /* join einzugsgebiete.tgnam */
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(POINT, 25832) )

-- database_createspatialindex_haltungen_geom: "
CREATE INDEX idx_haltungen_geom ON qkan.haltungen USING GIST (geom) ;

-- database_create_haltungen_untersucht: "
CREATE TABLE IF NOT EXISTS qkan.haltungen_untersucht (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    haltnam TEXT,
    bezugspunkt TEXT,
    schoben TEXT,                                   /* join schaechte.schnam */
    schunten TEXT,                                  /* join schaechte.schnam */
    hoehe NUMERIC(4,0),                             /* Profilhoehe (mm) */
    breite NUMERIC(4,0),                            /* Profilbreite (mm) */
    laenge NUMERIC(7,3),                            /* abweichende Haltungslänge (m) */
    baujahr INTEGER,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    untersucher TEXT,
    untersuchrichtung TEXT,
    wetter INTEGER DEFAULT 0,
    bewertungsart TEXT,
    bewertungstag TEXT,
    strasse TEXT,
    datenart TEXT,
    auftragsbezeichnung TEXT,
    max_ZD INTEGER,
    max_ZB INTEGER, 
    max_ZS INTEGER,
    xschob NUMERIC(11,3),
    yschob NUMERIC(11,3),
    xschun NUMERIC(11,3),
    yschun NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;

ALTER TABLE IF EXISTS qkan.einleit OWNER to isce;

-- database_createspatialindex_haltungen_untersucht_geom: "
CREATE INDEX idx_haltungen_untersucht_geom ON qkan.haltungen_untersucht USING GIST (geom) ;

-- database_create_haltungen_untersucht_bewertung: "
CREATE TABLE IF NOT EXISTS qkan.haltungen_untersucht_bewertung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    haltnam TEXT,
    bezugspunkt TEXT,
    schoben TEXT,                                   /* join schaechte.schnam */
    schunten TEXT,                                  /* join schaechte.schnam */
    hoehe NUMERIC(4,0),                             /* Profilhoehe (mm) */
    breite NUMERIC(4,0),                            /* Profilbreite (mm) */
    laenge NUMERIC(7,3),                            /* abweichende Haltungslänge (m) */
    baujahr INTEGER,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    untersucher TEXT,
    untersuchrichtung TEXT,
    wetter INTEGER DEFAULT 0,
    bewertungsart TEXT,
    bewertungstag TEXT,
    strasse TEXT,
    datenart TEXT,
    auftragsbezeichnung TEXT,
    max_ZD INTEGER,
    max_ZB INTEGER, 
    max_ZS INTEGER,
    xschob NUMERIC(11,3),
    yschob NUMERIC(11,3),
    xschun NUMERIC(11,3),
    yschun NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    objektklasse_dichtheit          TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_standsicherheit    TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_betriebssicherheit TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_gesamt             TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    hydraulische_auslastung         TEXT,
    lage_grundwasser                TEXT,
    ueberdeckung                    NUMERIC(11,3),
    bodengruppe                     TEXT,
    geom geometry(LINESTRING, 25832) )

;

GRANT ALL ON TABLE qkan.einleit TO isce;
GRANT ALL ON TABLE qkan.einleit TO juelich;

-- database_createspatialindex_haltungen_untersucht_bewertung_geom: "
CREATE INDEX idx_haltungen_untersucht_bewertung_geom ON qkan.haltungen_untersucht_bewertung USING GIST (geom) ;

-- database_create_untersuchdat_haltung: "
CREATE TABLE IF NOT EXISTS qkan.untersuchdat_haltung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    untersuchhal TEXT,
    schoben TEXT,                                   /* join schaechte.schnam  */
    schunten TEXT,                                  /* join schaechte.schnam */
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    bandnr INTEGER,
    videozaehler TEXT,
    inspektionslaenge NUMERIC(7,3),
    station NUMERIC(7,3),
    stationtext NUMERIC(7,3),
    timecode TEXT,
    video_offset NUMERIC(7,1),
    langtext TEXT,
    kuerzel TEXT,
    charakt1 TEXT,
    charakt2 TEXT,
    quantnr1 NUMERIC(7,2), 
    quantnr2 NUMERIC(7,2), 
    streckenschaden TEXT,
    streckenschaden_lfdnr INTEGER,
    pos_von INTEGER, 
    pos_bis INTEGER,
    foto_dateiname TEXT,
    film_dateiname TEXT,
    ordner_bild TEXT,
    ordner_video TEXT,
    filmtyp INTEGER,
    video_start INTEGER,
    video_ende INTEGER,
    ZD INTEGER,
    ZB INTEGER,
    ZS INTEGER,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;

-- Einleitungen aus Aussengebieten 
-- Erfasst alle Außengebiete
-- Die Zuordnung zum Teilgebiet dient nur der Auswahl

-- database_createspatialindex_untersuchdat_haltung_geom: "
CREATE INDEX idx_untersuchdat_haltung_geom ON qkan.untersuchdat_haltung USING GIST (geom) ;

-- database_create_untersuchdat_haltung_bewertung: "
CREATE TABLE IF NOT EXISTS qkan.untersuchdat_haltung_bewertung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    untersuchhal TEXT,
    schoben TEXT,                                   /* join schaechte.schnam  */
    schunten TEXT,                                  /* join schaechte.schnam */
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    bandnr INTEGER,
    videozaehler TEXT,
    inspektionslaenge NUMERIC(7,3),
    station NUMERIC(7,3),
    stationtext NUMERIC(7,3),
    timecode TEXT,
    video_offset NUMERIC(7,1),
    langtext TEXT,
    kuerzel TEXT,
    charakt1 TEXT,
    charakt2 TEXT,
    quantnr1 NUMERIC(7,2), 
    quantnr2 NUMERIC(7,2), 
    streckenschaden TEXT,
    streckenschaden_lfdnr INTEGER,
    pos_von INTEGER, 
    pos_bis INTEGER,
    foto_dateiname TEXT,
    film_dateiname TEXT,
    ordner_bild TEXT,
    ordner_video TEXT,
    filmtyp INTEGER,
    video_start INTEGER,
    video_ende INTEGER,
    ZD INTEGER,
    ZB INTEGER,
    ZS INTEGER,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    Beschreibung     TEXT,
    bw_bs            TEXT,
    Zustandsklasse_D TEXT,
    Zustandsklasse_S TEXT,
    Zustandsklasse_B TEXT,
    geom geometry(LINESTRING, 25832) )

;

TABLESPACE pg_default;

-- database_createspatialindex_untersuchdat_haltung_bewertung_geom: "
CREATE INDEX idx_untersuchdat_haltung_bewertung_geom ON qkan.untersuchdat_haltung_bewertung USING GIST (geom) ;

-- database_create_anschlussleitungen: "
CREATE TABLE IF NOT EXISTS qkan.anschlussleitungen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    leitnam TEXT,
    schoben TEXT,                                   /* join schaechte.schnam */
    schunten TEXT,                                  /* join schaechte.schnam */
    hoehe NUMERIC(4,0),                             /* Profilhoehe (mm) */
    breite NUMERIC(4,0),                            /* Profilbreite (mm) */
    laenge NUMERIC(7,3),                            /* abweichende Haltungslänge (m) */
    aussendurchmesser NUMERIC(4,0),
    sohleoben NUMERIC(7,3),                         /* Sohlhöhe oben (m) */
    sohleunten NUMERIC(7,3),                        /* Sohlhöhe unten (m) */
    baujahr INTEGER,
    haltnam TEXT,                                   /* Anschluss an Haltung */
    urstation NUMERIC(7,3),                         /* Anschlussposition gegen Fließrichtung */
    ursprung TEXT,                                  /* Adresse oder Objektbezeichnung */
    anschlusstyp TEXT,
    lageanschluss INTEGER,                         /* als Uhrzeit 1 - 12 */
    teilgebiet TEXT,                                /* join teilgebiet.tgnam */
    strasse TEXT,                                   /* für ISYBAU benötigt */
    profilnam TEXT DEFAULT 'Kreisquerschnitt',      /* join profile.profilnam */
    entwart TEXT DEFAULT 'Regenwasser',             /* join entwaesserungsarten.bezeichnung */
    material TEXT,                                  /* join material.bezeichnung */
    profilauskleidung TEXT,
    innenmaterial TEXT,
    ks NUMERIC(7,4) DEFAULT 1.5,                    /* abs. Rauheit (mm, Prandtl-Colebrook) */
    simstatus TEXT DEFAULT 'vorhanden',             /* join simulationsstatus.bezeichnung */
    xschob NUMERIC(11,3),
    yschob NUMERIC(11,3),
    xschun NUMERIC(11,3),
    yschun NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;

-- database_createspatialindex_anschlussleitungen_geom: "
CREATE INDEX idx_anschlussleitungen_geom ON qkan.anschlussleitungen USING GIST (geom) ;

-- database_create_anschlussleitungen_untersucht: "
CREATE TABLE IF NOT EXISTS qkan.anschlussleitungen_untersucht (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    leitnam TEXT,
    bezugspunkt TEXT,
    schoben TEXT,                                   /* join schaechte.schnam */
    schunten TEXT,                                  /* join schaechte.schnam */
    hoehe NUMERIC(4,0),                             /* Profilhoehe (mm) */
    breite NUMERIC(4,0),                            /* Profilbreite (mm) */
    laenge NUMERIC(7,3),                            /* abweichende Haltungslänge (m) */
    baujahr INTEGER,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    untersucher TEXT,
    untersuchrichtung TEXT,
    wetter INTEGER DEFAULT 0,
    bewertungsart TEXT,
    bewertungstag TEXT,
    strasse TEXT,
    datenart TEXT,
    auftragsbezeichnung TEXT,
    max_ZD INTEGER,
    max_ZB INTEGER, 
    max_ZS INTEGER,
    xschob NUMERIC(11,3),
    yschob NUMERIC(11,3),
    xschun NUMERIC(11,3),
    yschun NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;


REVOKE ALL ON TABLE qkan.aussengebiete FROM juelich;
-- database_createspatialindex_anschlussleitungen_untersucht_geom: "
CREATE INDEX idx_anschlussleitungen_untersucht_geom ON qkan.anschlussleitungen_untersucht USING GIST (geom) ;

-- database_create_anschlussleitungen_untersucht_bewertung: "
CREATE TABLE IF NOT EXISTS qkan.anschlussleitungen_untersucht_bewertung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    leitnam TEXT,
    bezugspunkt TEXT,
    schoben TEXT,                                   /* join schaechte.schnam */
    schunten TEXT,                                  /* join schaechte.schnam */
    hoehe NUMERIC(4,0),                             /* Profilhoehe (mm) */
    breite NUMERIC(4,0),                            /* Profilbreite (mm) */
    laenge NUMERIC(7,3),                            /* abweichende Haltungslänge (m) */
    baujahr INTEGER,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    untersucher TEXT,
    untersuchrichtung TEXT,
    wetter INTEGER DEFAULT 0,
    bewertungsart TEXT,
    bewertungstag TEXT,
    strasse TEXT,
    datenart TEXT,
    auftragsbezeichnung TEXT,
    max_ZD INTEGER,
    max_ZB INTEGER, 
    max_ZS INTEGER,
    xschob NUMERIC(11,3),
    yschob NUMERIC(11,3),
    xschun NUMERIC(11,3),
    yschun NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    objektklasse_dichtheit          TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_standsicherheit    TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_betriebssicherheit TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_gesamt             TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    hydraulische_auslastung         TEXT,
    lage_grundwasser                TEXT,
    ueberdeckung                    NUMERIC(11,3),
    bodengruppe                     TEXT,
    geom geometry(LINESTRING, 25832) )

;


-- database_createspatialindex_anschlussleitungen_untersucht_bewertung_geom: "
CREATE INDEX idx_anschlussleitungen_untersucht_bewertung_geom ON qkan.anschlussleitungen_untersucht_bewertung USING GIST (geom) ;

-- database_create_untersuchdat_anschlussleitung: "
CREATE TABLE IF NOT EXISTS qkan.untersuchdat_anschlussleitung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    untersuchleit TEXT,
    schoben TEXT,                                   /* join schaechte.schnam  */
    schunten TEXT,                                  /* join schaechte.schnam */
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    bandnr INTEGER,
    videozaehler TEXT,
    inspektionslaenge NUMERIC(7,3),
    station NUMERIC(7,3),
    stationtext NUMERIC(7,3),
    timecode TEXT,
    video_offset NUMERIC(7,1),
    langtext TEXT,
    kuerzel TEXT,
    charakt1 TEXT,
    charakt2 TEXT,
    quantnr1 NUMERIC(7,2), 
    quantnr2 NUMERIC(7,2), 
    streckenschaden TEXT,
    streckenschaden_lfdnr INTEGER,
    pos_von INTEGER, 
    pos_bis INTEGER,
    foto_dateiname TEXT,
    film_dateiname TEXT,
    ordner_bild TEXT,
    ordner_video TEXT,
    filmtyp INTEGER,
    video_start INTEGER,
    video_ende INTEGER,
    ZD INTEGER,
    ZB INTEGER,
    ZS INTEGER,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;


-- database_createspatialindex_untersuchdat_anschlussleitung_geom: "
CREATE INDEX idx_untersuchdat_anschlussleitung_geom ON qkan.untersuchdat_anschlussleitung USING GIST (geom) ;

-- database_create_untersuchdat_anschlussleitung_bewertung: "
CREATE TABLE IF NOT EXISTS qkan.untersuchdat_anschlussleitung_bewertung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    untersuchleit TEXT,
    schoben TEXT,                                   /* join schaechte.schnam  */
    schunten TEXT,                                  /* join schaechte.schnam */
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    bandnr INTEGER,
    videozaehler TEXT,
    inspektionslaenge NUMERIC(7,3),
    station NUMERIC(7,3),
    stationtext NUMERIC(7,3),
    timecode TEXT,
    video_offset NUMERIC(7,1),
    langtext TEXT,
    kuerzel TEXT,
    charakt1 TEXT,
    charakt2 TEXT,
    quantnr1 NUMERIC(7,2), 
    quantnr2 NUMERIC(7,2), 
    streckenschaden TEXT,
    streckenschaden_lfdnr INTEGER,
    pos_von INTEGER, 
    pos_bis INTEGER,
    foto_dateiname TEXT,
    film_dateiname TEXT,
    ordner_bild TEXT,
    ordner_video TEXT,
    filmtyp INTEGER,
    video_start INTEGER,
    video_ende INTEGER,
    ZD INTEGER,
    ZB INTEGER,
    ZS INTEGER,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    Beschreibung     TEXT,
    bw_bs            TEXT,
    Zustandsklasse_D TEXT,
    Zustandsklasse_S TEXT,
    Zustandsklasse_B TEXT,
    geom geometry(LINESTRING, 25832) )

;


-- database_createspatialindex_untersuchdat_anschlussleitung_bewertung_geom: "
CREATE INDEX idx_untersuchdat_anschlussleitung_bewertung_geom ON qkan.untersuchdat_anschlussleitung_bewertung USING GIST (geom) ;

-- database_create_anschlussschaechte (ergänzt jh, 16.02.2026)
CREATE TABLE IF NOT EXISTS qkan.anschlussschaechte (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schnam  TEXT,
    sohlhoehe NUMERIC(7,3),
    deckelhoehe NUMERIC(7,3),
    durchm NUMERIC(7,3),                            /* Schachtdurchmesser (m) */
    druckdicht INTEGER, 
    entwart TEXT DEFAULT 'Regenwasser',             /* join entwaesserungsarten.bezeichnung */
    strasse TEXT,
    baujahr INTEGER,
    haltnam TEXT,                                   /* Anschluss an Haltung */
    urstation NUMERIC(7,3),                         /* Anschlussposition gegen Fließrichtung */
    ursprung TEXT,                                  /* Adresse oder Objektbezeichnung */
    anschlusstyp TEXT,
    eigentum TEXT,                                  /* join eigentum.name */
    teilgebiet TEXT,                                /* join teilgebiet.tgnam */
    simstatus TEXT DEFAULT 'vorhanden',             /* join simulationsstatus.bezeichnung */
    material TEXT,                                  /* join material.bezeichnung */
    xsch NUMERIC(11,3), 
    ysch NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(POINT, 25832))

;


-- database_createspatialindex_schaechte_geom: "
CREATE INDEX idx_anschlussschaechte_geom ON qkan.anschlussschaechte USING GIST (geom) ;

-- database_create_schaechte: "
CREATE TABLE IF NOT EXISTS qkan.schaechte (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schnam TEXT,
    sohlhoehe NUMERIC(7,3),
    deckelhoehe NUMERIC(7,3),
    durchm NUMERIC(7,3),                            /* Schachtdurchmesser (m) */
    druckdicht INTEGER, 
    ueberstauflaeche NUMERIC(7,0) DEFAULT 0,
    entwart TEXT DEFAULT 'Regenwasser',             /* join entwaesserungsarten.bezeichnung */
    strasse TEXT,
    baujahr INTEGER,
    eigentum TEXT,                                  /* join eigentum.name */
    teilgebiet TEXT,                                /* join teilgebiet.tgnam */
    knotentyp TEXT,                                 /* join knotentypen.knotentyp */
    auslasstyp TEXT,                                /* join auslasstypen.bezeichnung */
    schachttyp TEXT DEFAULT 'Schacht',              /* join schachttypen.schachttyp */
    simstatus TEXT DEFAULT 'vorhanden',             /* join simulationsstatus.bezeichnung */
    material TEXT,                                  /* join material.bezeichnung */
    xsch NUMERIC(11,3), 
    ysch NUMERIC(11,3),
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geop geometry(POINT, 25832),
    geom geometry(MULTILINESTRING, 25832) )

;

-- database_createspatialindex_schaechte_geom: "
CREATE INDEX idx_schaechte_geom ON qkan.schaechte USING GIST (geom) ;

-- database_createspatialindex_schaechte_geop: "
CREATE INDEX idx_schaechte_geop ON qkan.schaechte USING GIST (geop);

-- database_create_schaechte_untersucht: "
CREATE TABLE IF NOT EXISTS qkan.schaechte_untersucht (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schnam TEXT, 
    durchm NUMERIC(7,3),                            /* Schachtdurchmesser (m) */
    baujahr INTEGER,
    bezugspunkt TEXT,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT, 
    untersucher TEXT, 
    wetter INTEGER DEFAULT 0, 
    strasse TEXT,
    bewertungsart TEXT, 
    bewertungstag TEXT,
    datenart TEXT,
    auftragsbezeichnung TEXT,
    max_ZD INTEGER,
    max_ZB INTEGER,
    max_ZS INTEGER, 
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geop geometry(POINT, 25832) )

;


-- Anbindung Aussengebiete 
-- Die Tabelle linkageb verwaltet die Anbindung von Aussengebieten an Schächte. Diese Anbindung
-- wird anschließend in das Feld schnam eingetragen. Der Export erfolgt allerdings anhand
-- der grafischen Verknüpfungen dieser Tabelle.
-- database_createspatialindex_schaechte_untersucht_geop: "
CREATE INDEX idx_schaechte_untersucht_geop ON qkan.schaechte_untersucht USING GIST (geop) ;

-- database_create_schaechte_untersucht_bewertung: "
CREATE TABLE IF NOT EXISTS qkan.schaechte_untersucht_bewertung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schnam TEXT, 
    durchm NUMERIC(7,3),                            /* Schachtdurchmesser (m) */
    baujahr INTEGER,
    bezugspunkt TEXT,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT, 
    untersucher TEXT, 
    wetter INTEGER DEFAULT 0, 
    strasse TEXT,
    bewertungsart TEXT, 
    bewertungstag TEXT,
    datenart TEXT,
    auftragsbezeichnung TEXT,
    max_ZD INTEGER,
    max_ZB INTEGER,
    max_ZS INTEGER, 
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    objektklasse_dichtheit          TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_standsicherheit    TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_betriebssicherheit TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    objektklasse_gesamt             TEXT,       /* todo: INTEGER, aber Wert z.b. '-' */
    hydraulische_auslastung         TEXT,
    lage_grundwasser                TEXT,
    ueberdeckung                    NUMERIC(11,3),
    bodengruppe                     TEXT,
    geop geometry(POINT, 25832) )

;


ALTER TABLE IF EXISTS qkan.linkageb OWNER to isce;
-- database_createspatialindex_schaechte_untersucht_bewertung_geop: "
CREATE INDEX idx_schaechte_untersucht_bewertung_geop ON qkan.schaechte_untersucht_bewertung USING GIST (geop) ;

-- database_create_untersuchdat_schacht: "
CREATE TABLE IF NOT EXISTS qkan.untersuchdat_schacht (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    untersuchsch TEXT,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    bandnr INTEGER,
    videozaehler TEXT,
    timecode TEXT,
    langtext TEXT,
    kuerzel TEXT,
    charakt1 TEXT,
    charakt2 TEXT,
    quantnr1 NUMERIC(7,2), 
    quantnr2 NUMERIC(7,2), 
    streckenschaden TEXT,
    streckenschaden_lfdnr INTEGER,
    pos_von INTEGER,
    pos_bis INTEGER,
    vertikale_lage INTEGER,
    inspektionslaenge INTEGER,
    bereich TEXT,
    foto_dateiname TEXT,
    ordner_bild TEXT,
    film_dateiname TEXT,
    ordner_video TEXT,
    filmtyp INTEGER,
    video_start INTEGER,
    video_ende INTEGER,
    ZD INTEGER,
    ZB INTEGER,
    ZS INTEGER,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(LINESTRING, 25832) )

;


GRANT ALL ON TABLE qkan.linkageb TO isce;
GRANT ALL ON TABLE qkan.linkageb TO juelich;
-- database_createspatialindex_untersuchdat_schacht_geom: "
CREATE INDEX idx_untersuchdat_schacht_geom ON qkan.untersuchdat_schacht USING GIST (geom) ;

-- database_create_untersuchdat_schacht_bewertung: "
CREATE TABLE IF NOT EXISTS qkan.untersuchdat_schacht_bewertung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    untersuchsch TEXT,
    id INTEGER,                                     /* absolute Nummer der Inspektion */
    untersuchtag TEXT,
    bandnr INTEGER,
    videozaehler TEXT,
    timecode TEXT,
    langtext TEXT,
    kuerzel TEXT,
    charakt1 TEXT,
    charakt2 TEXT,
    quantnr1 NUMERIC(7,2), 
    quantnr2 NUMERIC(7,2), 
    streckenschaden TEXT,
    streckenschaden_lfdnr INTEGER,
    pos_von INTEGER,
    pos_bis INTEGER,
    vertikale_lage INTEGER,
    inspektionslaenge INTEGER,
    bereich TEXT,
    foto_dateiname TEXT,
    ordner_bild TEXT,
    film_dateiname TEXT,
    ordner_video TEXT,
    filmtyp INTEGER,
    video_start INTEGER,
    video_ende INTEGER,
    ZD INTEGER,
    ZB INTEGER,
    ZS INTEGER,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    Beschreibung     TEXT,
    bw_bs            TEXT,
    Zustandsklasse_D TEXT,
    Zustandsklasse_S TEXT,
    Zustandsklasse_B TEXT,
    geom geometry(LINESTRING, 25832) )

;


TABLESPACE pg_default;
-- database_createspatialindex_untersuchdat_schacht_bewertung_geom: "
CREATE INDEX idx_untersuchdat_schacht_bewertung_geom ON qkan.untersuchdat_schacht_bewertung USING GIST (geom);

-- Einzugsgebiete 
-- Entsprechen in HYSTEM-EXTRAN 7.x den Siedlungstypen
-- "flaeche" wird nur für den Import benötigt, wenn keine Flächenobjekte vorhanden sind
-- Verwendung:
-- Spezifische Verbrauchsdaten in Verbindung mit "einwohner"

-- database_create_einzugsgebiete: "
CREATE TABLE IF NOT EXISTS qkan.einzugsgebiete (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tgnam TEXT,
    ewdichte NUMERIC(6,2),                  /* ewdichte (EW/ha) */
    wverbrauch NUMERIC(4,1),                /* wverbrauch (l/(EW·d)) */
    stdmittel NUMERIC(4,2),                 /* stdmittel (h/d) */
    fremdwas NUMERIC(4,1),                  /* fremdwas (%) */
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(MULTIPOLYGON, 25832) )

;


GRANT ALL ON TABLE qkan.simulationsstatus TO isce;
GRANT ALL ON TABLE qkan.simulationsstatus TO juelich;
-- database_createspatialindex_einzugsgebiete_geom: "
CREATE INDEX idx_einzugsgebiete_geom ON qkan.einzugsgebiete USING GIST (geom) ;

-- Teilgebiete: Auswahl von Objekten in verschiedenen Tabellen für verschiedene 
-- Aufgaben, z. B. automatische Verknüpfung von befestigten Flächen und direkten 
-- Einleitungen.
-- database_create_teilgebiete: "
CREATE TABLE IF NOT EXISTS qkan.teilgebiete (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tgnam TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(MULTIPOLYGON, 25832) )

;


ALTER TABLE IF EXISTS qkan.material OWNER to isce;
-- database_createspatialindex_teilgebiete_geom: "
CREATE INDEX idx_teilgebiete_geom ON qkan.teilgebiete USING GIST (geom) ;

-- database_create_flaechen: "
CREATE TABLE IF NOT EXISTS qkan.flaechen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,                           /* join haltungen.haltnam */
    schnam TEXT,                            /* join schaechte.schnam */
    neigkl INTEGER DEFAULT 1,               /* Neigungsklasse (1-4) */
    neigung NUMERIC(4,1),                   /* absolute Neigung (%) */
    teilgebiet TEXT,                        /* join teilgebiet.tgnam */
    regenschreiber TEXT,
    abflussparameter TEXT,                  /* join abflussparameter.apnam */
    aufteilen INTEGER DEFAULT 0,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(MULTIPOLYGON, 25832) )

;


-- database_create_auslasstypen: "
CREATE TABLE IF NOT EXISTS qkan.auslasstypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)
-- database_createspatialindex_flaechen_geom: "
CREATE INDEX idx_flaechen_geom ON qkan.flaechen USING GIST (geom) ;

-- Anbindung Flächen
-- Die Tabelle linkfl verwaltet die Anbindung von Flächen an Haltungen. Diese Anbindung
-- wird ausschließlich grafisch verwaltet und beim Export direkt verwendet.
-- Flächen, bei denen das Attribut "aufteilen" den Wert 'ja' hat, werden mit dem
-- Werkzeug "QKan_Link_Flaechen" mit allen durch die Verschneidung mit tezg entstehenden
-- Anteilen zugeordnet.

-- database_create_linkfl: "
CREATE TABLE IF NOT EXISTS qkan.linkfl (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,                       /* join haltungen.haltnam */
    schnam TEXT,                        /* join schaechte.schnam */
    tezgnam TEXT,                       /* join tezg.flnam */
    teilgebiet TEXT,                    /* join teilgebiet.tgnam */
    abflusstyp TEXT,                    /* JOIN abflusstypen.abflusstyp */
    speicherzahl INTEGER,               /* HE8 AnzahlSpeicher */
    speicherkonst NUMERIC(4,1),         /* HE8 Speicherkonstante (Typ 0) */
    fliesszeitkanal NUMERIC(4,1),       /* HE8 LaengsteFliesszeitKanal (Typ 1) */
    fliesszeitflaeche NUMERIC(4,1),     /* HE8 FliesszeitOberflaeche (Typ 1) oder */
                                        /* Schwerpunktlaufzeit (Typ 2) */
    geom geometry(MULTIPOLYGON, 25832) ,
    gbuf geometry(MULTIPOLYGON, 25832) ,
    glink geometry(LINESTRING, 25832) )

;


REVOKE ALL ON TABLE qkan.auslasstypen FROM juelich;

-- database_createspatialindex_linkfl_geom: "
CREATE INDEX idx_linkfl_geom ON qkan.linkfl USING GIST (geom) ;

-- database_createspatialindex_linkfl_gbuf: "
CREATE INDEX idx_linkfl_gbuf ON qkan.linkfl USING GIST (gbuf);

-- database_createspatialindex_linkfl_glink: "
CREATE INDEX idx_linkfl_glink ON qkan.linkfl USING GIST (glink);

-- Anbindung Direkteinleitungen:
-- Die Tabelle linksw verwaltet die Anbindung von Gebäuden an Haltungen. Diese Anbindung
-- wird anschließend in das Feld haltnam eingetragen. Der Export erfolgt allerdings anhand
-- der grafischen Verknüpfungen dieser Tabelle.

-- database_create_linksw: "
CREATE TABLE IF NOT EXISTS qkan.linksw (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,               /* join haltungen.haltnam */
    schnam TEXT,                /* join schaechte.schnam */
    teilgebiet TEXT,
    geom geometry(POLYGON, 25832),
    gbuf geometry(MULTIPOLYGON, 25832),
    glink geometry(LINESTRING, 25832) )

;

-- database_createspatialindex_linksw_geom: "
CREATE INDEX idx_linksw_geom ON qkan.linksw USING GIST (geom) ;

-- database_createspatialindex_linksw_gbuf: "
CREATE INDEX idx_linksw_gbuf ON qkan.linksw USING GIST (gbuf);

-- database_createspatialindex_linksw_glink: "
CREATE INDEX idx_linksw_glink ON qkan.linksw USING GIST (glink);

-- database_create_tezg: "
CREATE TABLE IF NOT EXISTS qkan.tezg (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,                       /* join haltungen.haltnam */
    schnam TEXT,                        /* join schaechte.schnam */
    neigkl INTEGER DEFAULT 1,           /* Werte [1-5], als Vorgabe fuer automatisch erzeugte unbef Flaechen */
    neigung NUMERIC(4,1),               /* absolute Neigung (%) */
    befgrad NUMERIC(4,3),               /* (-) Befestigungsgrad absolut, nur optional fuer SWMM und HE6 */
    schwerpunktlaufzeit NUMERIC(4,1),   /* nur, wenn nur Haltungsflächen aber keine Flächen eingelesen werden */
    regenschreiber TEXT,                /* Regenschreiber beziehen sich auf Zieldaten */
    teilgebiet TEXT,                    /* join teilgebiet.tgnam */
    abflussparameter TEXT,              /* als Vorgabe fuer automatisch erzeugte unbef Flaechen */
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(MULTIPOLYGON, 25832) )

;


-- database_create_abflussparameter: "
CREATE TABLE IF NOT EXISTS qkan.abflussparameter (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    apnam TEXT, 
    anfangsabflussbeiwert NUMERIC(4,1), 
    endabflussbeiwert NUMERIC(4,1), 
    benetzungsverlust NUMERIC(4,1), 
    muldenverlust NUMERIC(4,1), 
    benetzung_startwert NUMERIC(4,1), 
    mulden_startwert NUMERIC(4,1), 
    rauheit_kst NUMERIC(4,1),               /* Rauheit Stricklerbeiwert = 1/n */
    pctZero NUMERIC(4,1),                   /* SWMM % Zero-Imperv */
    bodenklasse TEXT,                       /* impervious = NULL, pervious = JOIN TO bodenklasse.bknam */
    flaechentyp TEXT,                       /* JOIN TO flaechentypen.bezeichnung */
    kommentar TEXT, 
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)
-- database_createspatialindex_tezg_geom: "
CREATE INDEX idx_tezg_geom ON qkan.tezg USING GIST (geom) ;

-- Direkte Einleitungen:
-- Erfasst alle Direkteinleitungen mit festem SW-Zufluss (m³/a)
-- Die Zuordnung zum Teilgebiet dient nur der Auswahl

-- database_create_einleit: "
CREATE TABLE IF NOT EXISTS qkan.einleit (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,               /* join haltungen.haltnam */
    schnam TEXT,                /* join schaechte.schnam */
    teilgebiet TEXT,            /* join teilgebiet.tgnam  */
    zufluss NUMERIC(8,2),       /* Zufluss (l/s) */
    ew NUMERIC(8,2),            /* Einwohner */
    einzugsgebiet TEXT,         /* join einzugsgebiete.tgnam */
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(POINT, 25832) )

;

ALTER TABLE IF EXISTS qkan.abflussparameter OWNER to isce;

-- database_createspatialindex_einleit_geom: "
CREATE INDEX idx_einleit_geom ON qkan.einleit USING GIST (geom) ;

-- Einleitungen aus Aussengebieten 
-- Erfasst alle Außengebiete
-- Die Zuordnung zum Teilgebiet dient nur der Auswahl

-- database_create_aussengebiete: "
CREATE TABLE IF NOT EXISTS qkan.aussengebiete (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gebnam TEXT, 
    schnam TEXT,                /* join schaechte.schnam  */
    hoeheob NUMERIC(7,3),
    hoeheun NUMERIC(7,3),
    fliessweg NUMERIC(5,1),
    basisabfluss NUMERIC(5,1), 
    cn NUMERIC(5,1),
    regenschreiber TEXT, 
    teilgebiet TEXT,            /* join teilgebiet.tgnam  */
    kommentar TEXT, 
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(MULTIPOLYGON, 25832) )

;


-- database_createspatialindex_aussengebiete_geom: "
CREATE INDEX idx_aussengebiete_geom ON qkan.aussengebiete USING GIST (geom) ;

-- Anbindung Aussengebiete 
-- Die Tabelle linkageb verwaltet die Anbindung von Aussengebieten an Schächte. Diese Anbindung
-- wird anschließend in das Feld schnam eingetragen. Der Export erfolgt allerdings anhand
-- der grafischen Verknüpfungen dieser Tabelle.

-- database_create_linkageb: "
CREATE TABLE IF NOT EXISTS qkan.linkageb (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gebnam TEXT,
    schnam TEXT,
    glink geometry(LINESTRING, 25832) )

;


-- database_createspatialindex_linkageb_glink: "
CREATE INDEX idx_linkageb_glink ON qkan.linkageb USING GIST (glink) ;

-- database_create_simulationsstatus: "
CREATE TABLE IF NOT EXISTS qkan.simulationsstatus (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    kuerzel TEXT,
    he_nr INTEGER,                      /* HYSTEM-EXTRAN */
    mu_nr INTEGER,                      /* Mike+ */
    kp_nr INTEGER,                      /* DYNA / Kanal++ */
    isybau TEXT,                        /* BFR Abwasser */
    m150 TEXT,                          /* DWA M150 */
    m145 TEXT,                          /* DWA M145 */
    kommentar TEXT)

;


-- database_create_material: "
CREATE TABLE IF NOT EXISTS qkan.material (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    kuerzel TEXT,
    isybau TEXT,                        /* BFR Abwasser */
    m150 TEXT,                          /* DWA M150 */
    m145 TEXT,                          /* DWA M145 */
    kommentar TEXT)

;


-- database_create_auslasstypen: "
CREATE TABLE IF NOT EXISTS qkan.auslasstypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)

;


-- database_create_abflussparameter: "
CREATE TABLE IF NOT EXISTS qkan.abflussparameter (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    apnam TEXT, 
    anfangsabflussbeiwert NUMERIC(4,1), 
    endabflussbeiwert NUMERIC(4,1), 
    benetzungsverlust NUMERIC(4,1), 
    muldenverlust NUMERIC(4,1), 
    benetzung_startwert NUMERIC(4,1), 
    mulden_startwert NUMERIC(4,1), 
    rauheit_kst NUMERIC(4,1),               /* Rauheit Stricklerbeiwert = 1/n */
    pctZero NUMERIC(4,1),                   /* SWMM % Zero-Imperv */
    bodenklasse TEXT,                       /* impervious = NULL, pervious = JOIN TO bodenklasse.bknam */
    flaechentyp TEXT,                       /* JOIN TO flaechentypen.bezeichnung */
    kommentar TEXT, 
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- database_create_flaechentypen: "
CREATE TABLE IF NOT EXISTS qkan.flaechentypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    he_nr INTEGER)

;


-- database_create_bodenklassen: "
CREATE TABLE IF NOT EXISTS qkan.bodenklassen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bknam TEXT, 
    infiltrationsrateanfang NUMERIC(6,3),   /* (mm/min) */
    infiltrationsrateende NUMERIC(6,3),     /* (mm/min) */
    infiltrationsratestart NUMERIC(6,3),    /* (mm/min) */
    rueckgangskonstante NUMERIC(5,1),       /* (1/d) */
    regenerationskonstante NUMERIC(5,1),    /* (1/d) */
    saettigungswassergehalt NUMERIC(5,1),   /* (mm) */
    kommentar TEXT, 
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- database_create_abflusstypen: "
CREATE TABLE IF NOT EXISTS qkan.abflusstypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    abflusstyp TEXT,
    he_nr INTEGER,              /* JOIN he.Flaeche.BerechnungSpeicherkonstante */
    kp_nr INTEGER)

;


-- database_create_knotentypen: "
CREATE TABLE IF NOT EXISTS qkan.knotentypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    knotentyp TEXT)

;



-- database_create_schachttypen: "
CREATE TABLE IF NOT EXISTS qkan.schachttypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schachttyp TEXT)

;



-- database_create_eigentum: "
CREATE TABLE IF NOT EXISTS qkan.eigentum (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT, 
    kommentar TEXT)

;



-- Tabelle Gruppen:
-- Bearbeitungen, die auf Auswahlen basieren, verwenden ausschließlich die
-- Tabelle "Teilgebiete". Diese Zuordnung ist sozusagen aktiv, im Gegensatz
-- zu inaktiven Zuordnungen, die in der Tabelle "gruppen" gespeichert werden.
-- Mit einem plugin "Zuordnung zu Teilgebieten" können gespeicherte
-- Zuordnungen gespeichert und geladen werden. Dabei werden die
-- Zuordnungen für folgende Tabellen verwaltet:
--  - "haltungen"
--  - "schaechte"
--  - "flaechen"
--  - "linkfl"
--  - "linksw"
--  - "tezg"
--  - "einleit"
--  - "swgebaeude"
-- database_create_gruppen: "
CREATE TABLE IF NOT EXISTS qkan.gruppen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pktab INTEGER,
    grnam TEXT,
    teilgebiet TEXT,                               /* join teilgebiet.tgnam */
    tabelle TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- database_create_profile: "
CREATE TABLE IF NOT EXISTS qkan.profile (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profilnam TEXT,
    kuerzel TEXT,                       /* nur für Beschriftung */
    he_nr INTEGER,                      /* HYSTEM-EXTRAN */
    mu_nr INTEGER,
    kp_key TEXT,                        /* DYNA / Kanal++ */
    isybau TEXT,                        /* BFR Abwasser */
    m150 TEXT,                          /* DWA M150 */
    m145 TEXT,                          /* DWA M145 */
    kommentar TEXT)

;


-- database_create_entwaesserungsarten: "
CREATE TABLE IF NOT EXISTS qkan.entwaesserungsarten (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,                   /* eindeutige QKan-Bezeichnung  */
    kuerzel TEXT,                       /* nur für Beschriftung */
    he_nr INTEGER,                      /* HYSTEM-EXTRAN */
    kp_nr INTEGER,                      /* DYNA / Kanal++ */
    isybau TEXT,                        /* BFR Abwasser */
    m150 TEXT,                          /* DWA M150 */
    m145 TEXT,                          /* DWA M145 */
    bemerkung TEXT)

;


-- database_create_haltungstypen: "
CREATE TABLE IF NOT EXISTS qkan.haltungstypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT, 
    bemerkung TEXT)

;



-- Tabelle Untersuchungsrichtung wird nur für das Nachschlagefeld benötigt
-- database_create_untersuchrichtung: "
CREATE TABLE IF NOT EXISTS qkan.untersuchrichtung (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT, 
    kuerzel TEXT, 
    isybau TEXT,                        /* BFR Abwasser */
    m150 TEXT,                          /* DWA M150 */
    m145 TEXT,                          /* DWA M145 */
    bemerkung TEXT)

;


-- database_create_wetter: "
CREATE TABLE IF NOT EXISTS qkan.wetter (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kuerzel INTEGER, 
    bezeichnung TEXT, 
    isybau TEXT,                        /* BFR Abwasser */
    m150 TEXT,                          /* DWA M150 */
    m145 TEXT,                          /* DWA M145 */
    bemerkung TEXT)

;


-- database_create_bewertungsart: "
CREATE TABLE IF NOT EXISTS qkan.bewertungsart (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kuerzel INTEGER, 
    bezeichnung TEXT, 
    bemerkung TEXT)

;

-- database_create_pumpentypen: "
CREATE TABLE IF NOT EXISTS qkan.pumpentypen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT, 
    he_nr INTEGER,
    isybau INTEGER)

;


-- Abfragen für Plausibilitätsprüfungen
-- database_create_pruefsql: "
CREATE TABLE IF NOT EXISTS qkan.pruefsql (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gruppe TEXT,                        /* zur Auswahl nach Thema */
    warntext TEXT,                      /* Beschreibung der SQL-Abfrage */
    warntyp TEXT,                       /* 'Info', 'Warnung', 'Fehler' */
    warnlevel INTEGER,                  /* zur Sortierung, 1-3 = Info, 4-7 = Warnung, 8-10 = Fehler */
    sql TEXT,
    layername TEXT,                     /* Objektsuche Layername */
    attrname TEXT,                      /* Objektsuche Attribut zur Objektidentifikation, */
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- Ergebnisse der Plausibilitätsprüfungen
-- database_create_pruefliste: "
CREATE TABLE IF NOT EXISTS qkan.pruefliste (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warntext TEXT,                      /* Beschreibung der SQL-Abfrage */
    warntyp TEXT,                       /* 'Info', 'Warnung', 'Fehler' */
    warnlevel INTEGER,                  /* zur Sortierung, 1-3 = Info, 4-7 = Warnung, 8-10 = Fehler */
    layername TEXT,                     /* Objektsuche Layername */
    attrname TEXT,                      /* Objektsuche Attribut zur Objektidentifikation, */
    objname TEXT,                       /* Objektsuche Objektname */
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- Referenztabelle für Plausi Zustandsklassen
-- database_create_reflist_zustand: "
CREATE TABLE IF NOT EXISTS qkan.reflist_zustand (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    art TEXT,
    hauptcode TEXT,
    charakterisierung1 TEXT,
    charakterisierung2 TEXT,
    bereich TEXT)

;


-- Allgemeine Referenztabelle
-- database_create_refdata:
CREATE TABLE IF NOT EXISTS qkan.refdata (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezext TEXT,        /* externe Bezeichnung, z. B. gem. DWA-M 150 */
    bezqkan TEXT,        /* Standardbezeichnung in QKan */
    kuerzel TEXT,        /* Kürzel in QKan */
    subject TEXT,        /* Bezeichnung der QKan-Tabelle oder interner Mapping-Tabelle */
    modul TEXT,        /* QKan-Modul (= Modulverzeichnis) */
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;



-- database_create_info: "
CREATE TABLE IF NOT EXISTS qkan.info (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject TEXT, 
    value TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- database_create_fotos: "
CREATE TABLE IF NOT EXISTS qkan.fotos (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT, 
    untersuchtag TEXT,
    objekt TEXT,
    datei TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;

-- database_create_videos: "
CREATE TABLE IF NOT EXISTS qkan.videos (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT, 
    untersuchtag TEXT,
    untersuchrichtung TEXT,
    objekt TEXT,
    datei TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP)

;


-- database_create_symbole: "
CREATE TABLE IF NOT EXISTS qkan.symbole (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    art TEXT,               /* QGIS-Referenz Thematische Karte zur Auswahl des Symbols */
    link TEXT,
    gruppe TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    geom geometry(POINT, 25832) )

;


-- database_createspatialindex_symbole_geom: "
CREATE INDEX idx_symbole_geom ON qkan.symbole USING GIST (geom) ;

-- database_create_symbolkatalog: "
CREATE TABLE IF NOT EXISTS qkan.symbolkatalog (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bezeichnung TEXT,
    gruppe TEXT,                            /* zur Aufteilung auf verschiedene Layer */
    kommentar TEXT)

;



-- database_createview_untersuchdat_aktuell: "
CREATE VIEW qkan.v_untersuchdat_hal_last AS
WITH um AS (
    SELECT untersuchhal, schoben, schunten, max(untersuchtag) AS letzter_untersuchtag
    FROM qkan.untersuchdat_haltung
    GROUP BY untersuchhal, schoben, schunten)
SELECT uh.*
FROM qkan.untersuchdat_haltung AS uh
JOIN um USING(untersuchhal, schoben, schunten);

-- database_create_sel_haltungen: "
CREATE TABLE IF NOT EXISTS qkan.sel_haltungen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY)

;


-- database_create_sel_schaechte: "
CREATE TABLE IF NOT EXISTS qkan.sel_schaechte (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY)

;



-- database_create_sel_flaechen: "
CREATE TABLE IF NOT EXISTS qkan.sel_flaechen (
    pk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY)

;
