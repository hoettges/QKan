-- Änderungen an der Profilbezeichnung in der Detailtabelle nachführen
CREATE TRIGGER IF NOT EXISTS trig_ref_profile AFTER UPDATE OF profilnam ON profile
                BEGIN
                    UPDATE haltungen
                    SET profilnam = new.profilnam
                    WHERE profilnam = old.profilnam AND profilnam IS NOT NULL;
                    UPDATE anschlussleitungen
                    SET profilnam = new.profilnam
                    WHERE profilnam = old.profilnam AND profilnam IS NOT NULL;
                END;

-- Änderungen an der Bezeichnung in der Detailtabelle nachführen
CREATE TRIGGER IF NOT EXISTS trig_ref_entwart AFTER UPDATE OF bezeichnung ON entwaesserungsarten
                BEGIN
                    UPDATE haltungen
                    SET entwart = new.bezeichnung
                    WHERE entwart = old.bezeichnung AND entwart IS NOT NULL;
                    UPDATE schaechte
                    SET entwart = new.bezeichnung
                    WHERE entwart = old.bezeichnung AND entwart IS NOT NULL;
                    UPDATE anschlussleitungen
                    SET entwart = new.bezeichnung
                    WHERE entwart = old.bezeichnung AND entwart IS NOT NULL;
                END;

-- Änderungen an der Bezeichnung in der Detailtabelle nachführen
CREATE TRIGGER IF NOT EXISTS trig_ref_simstatus AFTER UPDATE OF bezeichnung ON simulationsstatus
                BEGIN
                    UPDATE haltungen
                    SET simstatus = new.bezeichnung
                    WHERE simstatus = old.bezeichnung AND simstatus IS NOT NULL;
                    UPDATE schaechte
                    SET simstatus = new.bezeichnung
                    WHERE simstatus = old.bezeichnung AND simstatus IS NOT NULL;
                    UPDATE anschlussleitungen
                    SET simstatus = new.bezeichnung
                    WHERE simstatus = old.bezeichnung AND simstatus IS NOT NULL;
                END;

-- Änderungen an der Bezeichnung in der Detailtabelle nachführen
CREATE TRIGGER IF NOT EXISTS trig_ref_material AFTER UPDATE OF bezeichnung ON material
                BEGIN
                    UPDATE haltungen
                    SET material = new.bezeichnung
                    WHERE material = old.bezeichnung AND material IS NOT NULL;
                    UPDATE schaechte
                    SET material = new.bezeichnung
                    WHERE material = old.bezeichnung AND material IS NOT NULL;
                    UPDATE anschlussleitungen
                    SET material = new.bezeichnung
                    WHERE material = old.bezeichnung AND material IS NOT NULL;
                END;
