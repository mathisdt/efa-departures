***This project is for electronic timetables in Germany, so the documentation is in German.***

# EFA per API abfragen

Die "Elektronische Fahrplan-Auskunft" kann über eine JSON-basierte API angesteuert werden.
Die Idee (und auch Teile des Codes) habe ich von [hier](https://finalrewind.org/interblag/entry/efa-json-api/).

# Anpassen

In der Methode `main()` kann angepasst werden, welche Haltestelle(n) man abfragt,
und ob man das Ergebnis noch filtern möchte (per `lambda`).

# HTML-Ausgabe

Wenn definiert ist, von welchen Haltestellen man welche Linien bzw. Richtungen haben möchte,
kann aus dem Abfrageergebnis z.B. minütlich eine HTML-Seite erzeugt werden (einfach durch Pipen
der Skript-Ausgabe in eine Datei), die man auf den Webserver schiebt, um sie auf dem Smartphone
per Lesezeichen im Schnellzugriff zu haben oder auf einem Bildschirm neben dem Wohnungsausgang
anzuzeigen.
