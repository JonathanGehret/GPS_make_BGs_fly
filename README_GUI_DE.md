# 🦅 Geier Näherungs-Analyse - GUI Edition

## Professionelle grafische Benutzeroberfläche für GPS-Näherungs-Analyse

Diese GUI-Anwendung macht die Geier-GPS-Näherungs-Analyse für nicht-technische Benutzer durch eine intuitive grafische Benutzeroberfläche zugänglich.

## 🌐 Mehrsprachige Unterstützung

Die Anwendung unterstützt **Deutsch** (Standard) und **Englisch**:
- **Standardsprache**: Deutsch
- **Sprachwechsel**: Klicken Sie auf "🌐 Language/Sprache" oben rechts
- **Automatisches Speichern**: Ihre Spracheinstellung wird gespeichert

## 🚀 Schnellstart

### Methode 1: Doppelklick-Start (Einfachste)
1. Doppelklicken Sie auf `launch_gui.py` um die Anwendung zu starten
2. Die GUI öffnet sich automatisch

### Methode 2: Kommandozeile
```bash
python3 scripts/proximity_analysis_gui.py
```

### Methode 3: Desktop-Verknüpfung (Linux)
1. Kopieren Sie `VultureProximityAnalysis.desktop` auf Ihren Desktop
2. Rechtsklicken und "Ausführung erlauben" wählen oder ausführbar machen
3. Doppelklicken zum Starten

## 📋 Benutzerhandbuch

### 1. Daten-Registerkarte - 📁
- **GPS-Datenordner auswählen**: Durchsuchen Sie Ihren Ordner mit CSV-Dateien
- **Datenvorschau**: Zeigt erkannte CSV-Dateien und GPS-Punktzahlen
- **Automatische Validierung**: Überprüft auf Datenprobleme und zeigt Warnungen

### 2. Analyse-Registerkarte - ⚙️
- **Näherungsschwelle**: Entfernung in km für Geier, die als "nah" betrachtet werden
  - Schieberegler-Bereich: 0,1km bis 10km
  - Empfohlen: 2-5km für Geier
- **Zeitschwelle**: Mindestdauer für Näherungsereignisse
  - Bereich: 1-60 Minuten
  - Empfohlen: 5-15 Minuten
- **Animationen aktivieren**: Ankreuzen um interaktive Begegnungskarten zu erstellen

### 3. Animations-Registerkarte - 🎬 (wenn aktiviert)
- **Zeitpuffer**: GPS-Datenstunden vor/nach Begegnungen (0,5-12 Stunden)
- **Pfadlänge**: Wie lange Flugpfade sichtbar bleiben (0,1-6 Stunden)
- **Zeitschritt**: Animationsqualität vs. Geschwindigkeit
  - Ultra-glatt: 1s-30s (langsamere Verarbeitung)
  - Ausgewogen: 1m-5m (empfohlen)
  - Schnell: 10m-1h (schnelle Verarbeitung)
- **Begegnungen begrenzen**: Nur erste N Begegnungen zum Testen verarbeiten

### 4. Ergebnisse-Registerkarte - 📊
- **Analyse-Zusammenfassung**: Wichtige Statistiken und Erkenntnisse
- **Generierte Dateien**: Liste der Ausgabedateien mit direktem Zugriff
- **Datei-Aktionen**: Dateien öffnen oder im Ordner anzeigen

### 5. Protokoll-Registerkarte - 📝
- **Echtzeit-Fortschritt**: Analyse während der Ausführung überwachen
- **Fehlermeldungen**: Informationen zur Fehlerbehebung
- **Protokoll speichern**: Protokoll zum Teilen oder Debuggen exportieren

## 🎯 Funktionen

### ✅ Benutzerfreundliche Oberfläche
- **Registerkarten-Layout**: Organisierter Arbeitsablauf von Daten zu Ergebnissen
- **Visuelles Feedback**: Fortschrittsbalken, Status-Updates und farbkodierte Nachrichten
- **Intuitive Bedienelemente**: Schieberegler, Dropdown-Menüs und Kontrollkästchen
- **Echtzeit-Validierung**: Sofortiges Feedback zu Einstellungen und Daten

### ✅ Professionelle Analyse
- **Vollständige Näherungserkennung**: Identifiziert wann Geier nah sind
- **Statistische Analyse**: Umfassende Metriken und Zusammenfassungen
- **Interaktive Visualisierungen**: Karten, Zeitlinien und Dashboards
- **Begegnungs-Animationen**: Professionelle animierte Karten zeigen Interaktionen

### ✅ Leistung & Zuverlässigkeit
- **Thread-Verarbeitung**: GUI bleibt während der Analyse reaktionsfähig
- **Fortschritts-Überwachung**: Echtzeit-Updates und Protokollierung
- **Fehlerbehandlung**: Elegante Wiederherstellung von Problemen
- **Unterbrechungs-Unterstützung**: Lange Analysen sicher stoppen

### ✅ Ausgabe-Verwaltung
- **Mehrere Formate**: HTML-Karten, CSV-Daten, interaktive Dashboards
- **Organisierte Speicherung**: Ergebnisse im visualizations/-Ordner gespeichert
- **Direkter Zugriff**: Dateien direkt aus der Anwendung öffnen
- **Export-Optionen**: Protokolle speichern und Ergebnisse einfach teilen

## 📁 Dateistruktur

```
GPS_make_BGs_fly/
├── launch_gui.py                    # Einfacher Starter
├── VultureProximityAnalysis.desktop # Desktop-Verknüpfung
├── scripts/
│   ├── proximity_analysis_gui.py    # Haupt-GUI-Anwendung
│   ├── i18n.py                      # Übersetzungssystem
│   └── proximity_analysis.py        # Kern-Analyse-Engine
├── data/                            # Platzieren Sie Ihre GPS-CSV-Dateien hier
├── visualizations/                  # Generierte Karten und Diagramme
└── analysis/                        # Analyseergebnisse und Daten
```

## 🔧 Systemanforderungen

### Systemvoraussetzungen
- **Python 3.7+** mit tkinter (normalerweise enthalten)
- **Betriebssystem**: Windows, macOS oder Linux
- **Arbeitsspeicher**: 2GB RAM minimal (4GB+ für große Datensätze)
- **Speicher**: 100MB für Anwendung + Platz für Ergebnisse

### Python-Abhängigkeiten
Alle erforderlichen Pakete sind im Projekt enthalten:
- pandas (Datenverarbeitung)
- plotly (interaktive Visualisierungen) 
- tkinter (GUI-Framework - mit Python enthalten)

## 📊 Datenformat

### Erwartetes CSV-Format
Ihre GPS-Datendateien sollten Spalten enthalten wie:
- **Timestamp**: Datum/Zeit in UTC
- **Latitude**: Dezimalgrad
- **Longitude**: Dezimalgrad
- **Vulture ID**: Bezeichner für jedes Individuum
- **Altitude/Height**: Optionale Höhendaten

### Unterstützte Variationen
Die Anwendung behandelt automatisch übliche Spaltennamen-Variationen:
- `TIMESTAMP`, `TIME`, `Timestamp [UTC]`
- `LAT`, `LATITUDE`, `Latitude`
- `LON`, `LONGITUDE`, `Longitude`
- `VULTURE_ID`, `vulture_id`, etc.

## 🎯 Nutzungstipps

### Für kleine Datensätze (< 1 Woche, < 3 Individuen)
- Standardeinstellungen verwenden
- Animationen mit 1-2 Minuten Zeitschritten aktivieren
- Pfade: 1-2 Stunden

### Für mittlere Datensätze (1-4 Wochen, 3-5 Individuen)
- Näherungsschwelle: 2-5km
- Animationen mit 5-10 Minuten Zeitschritten aktivieren
- Pfade: 2-4 Stunden
- Begegnungen für erste Tests begrenzen erwägen

### Für große Datensätze (> 1 Monat, > 5 Individuen)
- Mit größeren Näherungsschwellen beginnen (5-10km)
- 10-30 Minuten Zeitschritte für Animationen verwenden
- Pfade: 2-6 Stunden
- Begegnungen auf erste 10-20 für Leistung begrenzen

### Leistungsoptimierung
- **Große Datensätze**: Größere Zeitschritte und kürzere Pfade verwenden
- **Hohe Qualität**: Kleinere Zeitschritte aber Begegnungen begrenzen
- **Testen**: Immer erst Begegnungen begrenzen, dann erhöhen
- **Arbeitsspeicher**: Andere Anwendungen für sehr große Datensätze schließen

## 🌐 Spracheinstellungen

### Sprachwechsel
- Klicken Sie auf "🌐 Language/Sprache" oben rechts
- Wählen Sie zwischen Deutsch und English
- Die Einstellung wird automatisch gespeichert
- Alle UI-Elemente werden sofort aktualisiert

### Standardsprache
- **Deutsch** ist die Standardsprache
- Beim ersten Start wird Deutsch angezeigt
- Ihre Sprachwahl wird für zukünftige Sitzungen gespeichert

## 🆘 Fehlerbehebung

### Häufige Probleme

**"Keine CSV-Dateien gefunden"**
- Überprüfen Sie, dass CSV-Dateien im ausgewählten Ordner sind
- Stellen Sie sicher, dass Dateien .csv Erweiterung haben
- Überprüfen Sie, dass Dateien GPS-Daten enthalten

**"Analyse fehlgeschlagen"**
- Überprüfen Sie die Protokoll-Registerkarte für detaillierte Fehlermeldungen
- Stellen Sie sicher, dass CSV-Dateien richtige Spaltennamen haben
- Versuchen Sie es zuerst mit einem kleineren Datensatz

**"GUI startet nicht"**
- Stellen Sie sicher, dass Python 3.7+ installiert ist
- Überprüfen Sie, dass tkinter verfügbar ist: `python3 -c "import tkinter"`
- Versuchen Sie den Start von der Kommandozeile für Fehlermeldungen

**"Animationen dauern zu lange"**
- Zeitschritt erhöhen (z.B. von 1m auf 10m)
- Pfadlänge reduzieren
- Anzahl der Begegnungen begrenzen
- Kleineren Zeitpuffer verwenden

### Hilfe erhalten
1. Überprüfen Sie die Protokoll-Registerkarte für detaillierte Fehlermeldungen
2. Versuchen Sie es zuerst mit den enthaltenen Testdaten
3. Reduzieren Sie die Datensatzgröße zum Testen
4. Überprüfen Sie, dass alle erforderlichen Dateien vorhanden sind

## 🎉 Erfolgs-Indikatoren

Wenn alles richtig funktioniert, sollten Sie sehen:
- ✅ **Daten-Registerkarte**: Zeigt CSV-Dateien und GPS-Punktzahlen
- ✅ **Analyse**: Vervollständigt ohne Fehler im Protokoll
- ✅ **Ergebnisse**: Zeigt Statistiken und Begegnungs-Zusammenfassungen
- ✅ **Dateien**: Generierte Visualisierungen erscheinen in der Dateiliste
- ✅ **Ausgabe**: HTML-Dateien öffnen sich in Ihrem Webbrowser

## 📈 Nächste Schritte

Nach erfolgreicher Analyse:
1. **Ergebnisse überprüfen**: Statistiken und generierte Visualisierungen prüfen
2. **Animationen erkunden**: Begegnungs-Animationen im Browser öffnen
3. **Erkenntnisse teilen**: Protokolle und Ergebnisse für Zusammenarbeit exportieren
4. **Analyse verfeinern**: Parameter anpassen und nach Bedarf neu ausführen
5. **Ergebnisse archivieren**: Wichtige Analysen mit beschreibenden Namen speichern

---

**🦅 Frohes Analysieren!** Die GUI macht professionelle Geier-Näherungs-Analyse für alle zugänglich.
