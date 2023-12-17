***This project is for electronic timetables in Germany, so the documentation is in German.***

# Fahrplandaten per API abfragen

Hiermit können die Fahrplandaten der Deutschen Bahn abgefragt werden, die in vielen Fällen
auch lokale Nahverkehrsdaten (oft inkl. Echtzeitdaten) beinhalten. Am besten in der App
"DB Navigator" nachsehen, ob die gewünschten Daten dort unter "Abfahrten und Ankünfte"
zu sehen sind.

# Anpassen

In der Methode `main()` kann angepasst werden, welche Haltestelle(n) man abfragt,
und ob man das Ergebnis noch filtern möchte (per `lambda`).

# HTML-Ausgabe

Wenn definiert ist, von welchen Haltestellen man welche Linien bzw. Richtungen haben möchte,
kann aus dem Abfrageergebnis z.B. minütlich eine HTML-Seite erzeugt werden (einfach durch Pipen
der Skript-Ausgabe in eine Datei), die man auf den Webserver schiebt, um sie auf dem Smartphone
per Lesezeichen im Schnellzugriff zu haben oder auf einem Bildschirm neben dem Wohnungsausgang
anzuzeigen.

# Technische Voraussetzungen

* Python 3.9 oder neuer
* pyhafas 0.4.0 oder neuer (siehe `requirements.txt`)