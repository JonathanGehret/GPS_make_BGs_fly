#!/usr/bin/env python3
"""
Internationalization (i18n) Module for Vulture Proximity Analysis GUI

Provides German and English translations with German as default.
"""

import os
import json
from typing import Dict


class Translator:
    """Handles translations for the GUI application"""
    
    def __init__(self):
        self.current_language = "de"  # German as default
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation dictionaries"""
        
        # German translations (default)
        self.translations["de"] = {
            # Window titles
            "app_title": "🦅 Geier Näherungs-Analyse - Professional Edition",
            "help_title": "Hilfe - Geier Näherungs-Analyse",
            
            # Main tabs
            "tab_data": "📁 Daten",
            "tab_analysis": "⚙️ Analyse",
            "tab_animation": "🎬 Animation",
            "tab_results": "📊 Ergebnisse", 
            "tab_log": "📝 Protokoll",
            
            # Buttons
            "btn_run": "🚀 Analyse starten",
            "btn_stop": "⏹ Stoppen",
            "btn_open_results": "📁 Ergebnisordner öffnen",
            "btn_help": "❓ Hilfe",
            "btn_browse": "Durchsuchen...",
            "btn_refresh": "🔄 Datenvorschau aktualisieren",
            "btn_clear_log": "🗑 Protokoll löschen",
            "btn_save_log": "💾 Protokoll speichern",
            "btn_open": "📂 Öffnen",
            "btn_show_folder": "📁 In Ordner zeigen",
            "btn_language": "🌐 Language/Sprache",
            
            # Data tab
            "label_data_folder": "GPS-Datenordner:",
            "label_data_preview": "Datenvorschau:",
            "status_ready": "Bereit für die Analyse von Geier-GPS-Daten",
            "status_running": "Führe Näherungs-Analyse durch...",
            "status_completed": "Analyse abgeschlossen",
            "status_stopping": "Stoppe Analyse...",
            
            # Analysis tab
            "label_analysis_params": "Parameter für Näherungs-Analyse:",
            "group_detection_params": "Erkennungsparameter",
            "label_proximity_threshold": "Näherungsschwelle (km):",
            "label_time_threshold": "Zeitschwelle (Minuten):",
            "group_analysis_options": "Analyse-Optionen",
            "check_generate_animations": "Begegnungs-Animationen generieren",
            "group_parameter_guide": "Parameter-Leitfaden",
            "help_proximity": "• Näherungsschwelle: Maximale Entfernung zwischen Geiern für ein Näherungsereignis",
            "help_time": "• Zeitschwelle: Mindestdauer für die Aufzeichnung eines Näherungsereignisses",
            "help_animations": "• Begegnungs-Animationen: Erstellt interaktive Karten mit Geier-Interaktionen",
            
            # Animation tab
            "label_animation_config": "Animations-Konfiguration:",
            "group_data_range": "Datenbereich",
            "label_time_buffer": "Zeitpuffer (Stunden):",
            "label_trail_length": "Pfadlänge (Stunden):",
            "group_animation_quality": "Animations-Qualität",
            "label_time_step": "Zeitschritt:",
            "label_point_count": "📊 Punktanzahl wird berechnet wenn Daten geladen sind",
            "point_count_format": "📊 {0} {1} Punkte ({2:.1f}% Reduzierung von {3:,})",
            "label_quality_guide": "Qualitäts-Leitfaden:",
            "quality_ultra": "• 1s-30s: Ultra-glatt (langsamere Verarbeitung)",
            "quality_balanced": "• 1m-5m: Ausgewogene Qualität und Geschwindigkeit",
            "quality_fast": "• 10m-1h: Schnelle Verarbeitung (weniger Details)",
            "group_performance": "Leistungsoptionen",
            "label_limit_encounters": "Begegnungen begrenzen (0 = alle):",
            "limit_no_limit": "Keine Begrenzung",
            "limit_encounters": "Begegnungen",
            
            # Results tab
            "label_analysis_results": "Analyse-Ergebnisse:",
            "group_generated_files": "Generierte Dateien",
            
            # Log tab
            "label_analysis_log": "Analyse-Protokoll:",
            
            # Messages and logs
            "log_starting": "🚀 Starte Geier Näherungs-Analyse...",
            "log_data_folder": "📁 Datenordner:",
            "log_loading_data": "📊 Lade GPS-Daten...",
            "log_loaded_files": "✅ {0} GPS-Datendateien geladen",
            "log_proximity_threshold": "⚙️  Näherungsschwelle: {0} km",
            "log_time_threshold": "⚙️  Zeitschwelle: {0} Minuten",
            "log_analyzing": "🔍 Analysiere Näherungsereignisse...",
            "log_found_events": "✅ {0} Näherungsereignisse gefunden!",
            "log_no_events": "⚠️  Keine Näherungsereignisse mit aktuellen Parametern gefunden",
            "log_try_increase": "💡 Versuchen Sie, die Näherungsschwelle zu erhöhen oder überprüfen Sie Ihre Daten",
            "log_creating_animations": "🎬 Erstelle Begegnungs-Animationen...",
            "log_found_encounters": "🎬 {0} Begegnungsgruppe(n) zum Animieren gefunden",
            "log_limited_encounters": "⚡ Auf erste {0} Begegnungen für Leistung begrenzt",
            "log_creating_animation": "🎨 Erstelle Animation für Begegnung {0}/{1}...",
            "log_no_gps_data": "⚠️  Keine GPS-Daten für Begegnung {0} gefunden, überspringe...",
            "log_encounter_animated": "✅ Begegnung {0} animiert: {1} ({2:.1f} min)",
            "log_animation_interrupted": "⚠️  Animation bei Begegnung {0} unterbrochen",
            "log_animation_error": "❌ Fehler beim Animieren von Begegnung {0}: {1}",
            "log_animations_success": "🎉 {0} Begegnungs-Animationen erfolgreich erstellt!",
            "log_no_animations": "⚠️  Keine Begegnungs-Animationen wurden erstellt",
            "log_calculating_stats": "📊 Berechne Statistiken...",
            "log_creating_visualizations": "📈 Erstelle Visualisierungen...",
            "log_exporting_results": "💾 Exportiere Ergebnisse...",
            "log_events_saved": "📄 Ereignisdaten gespeichert in: {0}",
            "log_analysis_complete": "🎉 Näherungs-Analyse erfolgreich abgeschlossen!",
            "log_analysis_failed": "❌ Analyse fehlgeschlagen: {0}",
            "log_stop_requested": "🛑 Stopp vom Benutzer angefordert...",
            
            # Error messages
            "error_no_data": "❌ Ordner nicht gefunden: {0}",
            "error_no_csv": "⚠️ Keine CSV-Dateien gefunden in: {0}",
            "error_reading_folder": "❌ Fehler beim Lesen des Datenordners: {0}",
            "error_large_dataset": "⚠️  Großer Datensatz erkannt. Erwägen Sie größere Zeitschritte für Animationen.",
            "error_no_gps_found": "❌ Keine GPS-Daten gefunden!",
            "error_animation_failed": "❌ Animations-Erstellung fehlgeschlagen: {0}",
            
            # Data preview
            "preview_folder": "📁 Datenordner: {0}",
            "preview_found_files": "📄 {0} CSV-Datei(en) gefunden:",
            "preview_total_points": "📊 GPS-Punkte gesamt: {0:,}",
            "preview_file_ok": "✅ {0:<30} ({1:,} GPS-Punkte)",
            "preview_file_error": "❌ {0:<30} (Fehler: {1})",
            
            # Results display
            "results_title": "🦅 GEIER NÄHERUNGS-ANALYSE ERGEBNISSE",
            "results_separator": "=" * 50,
            "results_summary": "📊 ZUSAMMENFASSENDE STATISTIKEN:",
            "results_total_events": "• Näherungsereignisse gesamt: {0:,}",
            "results_unique_pairs": "• Einzigartige Geier-Paare: {0}",
            "results_avg_distance": "• Durchschnittliche Entfernung: {0:.2f} km",
            "results_closest": "• Nächste Begegnung: {0:.2f} km",
            "results_total_time": "• Gesamte Näherungszeit: {0:.1f} Stunden",
            "results_most_active": "• Aktivstes Paar: {0}",
            "results_peak_hour": "• Spitzenstunde: {0}:00",
            "results_by_vulture": "🦅 EREIGNISSE NACH GEIER:",
            "results_by_hour": "⏰ EREIGNISSE NACH STUNDE:",
            "results_events": "• {0}: {1} Ereignisse",
            "results_hour": "• {0:02d}:00: {1} Ereignisse",
            
            # Validation messages
            "validation_select_folder": "Bitte wählen Sie einen gültigen Datenordner!",
            "validation_analysis_running": "Analyse läuft bereits!",
            
            # File operations
            "file_save_log": "Protokolldatei speichern",
            "file_save_success": "Protokoll gespeichert in {0}",
            "file_save_error": "Fehler beim Speichern des Protokolls: {0}",
            "file_open_error": "Fehler beim Öffnen der Datei: {0}",
            "file_folder_error": "Fehler beim Öffnen des Ordners: {0}",
            
            # Time labels
            "time_hours": "{0:.1f} Stunden",
            "time_km": "{0:.1f} km",
            "time_min": "{0} min",
            
            # Help dialog
            "help_content": """
🦅 Geier Näherungs-Analyse - Hilfe

ÜBERBLICK:
Diese Anwendung analysiert GPS-Tracking-Daten, um zu identifizieren, wann sich Geier in enger Nähe zueinander befinden.

REGISTERKARTEN:
📁 Daten: Wählen Sie Ihren GPS-Datenordner und zeigen Sie Dateien in der Vorschau an
⚙️ Analyse: Konfigurieren Sie Parameter für die Näherungserkennung  
🎬 Animation: Konfigurieren Sie Einstellungen für Begegnungs-Animationen
📊 Ergebnisse: Zeigen Sie Analyseergebnisse und Statistiken an
📝 Protokoll: Überwachen Sie den Analysefortschritt und Nachrichten

SCHNELLSTART:
1. Wählen Sie Ihren GPS-Datenordner in der Registerkarte Daten
2. Passen Sie Näherungs- und Zeitschwellen in der Registerkarte Analyse an
3. Optional: Aktivieren Sie Begegnungs-Animationen
4. Klicken Sie auf "Analyse starten"

TIPPS:
• Verwenden Sie größere Näherungsschwellen für erste Erkundungen
• Aktivieren Sie Animationen nur für kleinere Datensätze zunächst
• Überprüfen Sie das Protokoll für detaillierte Fortschrittsinformationen
• Ergebnisse werden im Visualisierungsordner gespeichert

Für weitere Informationen besuchen Sie die Projektdokumentation.
            """
        }
        
        # English translations
        self.translations["en"] = {
            # Window titles
            "app_title": "🦅 Vulture Proximity Analysis - Professional Edition",
            "help_title": "Help - Vulture Proximity Analysis",
            
            # Main tabs
            "tab_data": "📁 Data",
            "tab_analysis": "⚙️ Analysis",
            "tab_animation": "🎬 Animation",
            "tab_results": "📊 Results", 
            "tab_log": "📝 Log",
            
            # Buttons
            "btn_run": "🚀 Run Analysis",
            "btn_stop": "⏹ Stop",
            "btn_open_results": "📁 Open Results Folder",
            "btn_help": "❓ Help",
            "btn_browse": "Browse...",
            "btn_refresh": "🔄 Refresh Data Preview",
            "btn_clear_log": "🗑 Clear Log",
            "btn_save_log": "💾 Save Log",
            "btn_open": "📂 Open",
            "btn_show_folder": "📁 Show in Folder",
            "btn_language": "🌐 Language/Sprache",
            
            # Data tab
            "label_data_folder": "GPS Data Folder:",
            "label_data_preview": "Data Preview:",
            "status_ready": "Ready to analyze vulture GPS data",
            "status_running": "Running proximity analysis...",
            "status_completed": "Analysis completed",
            "status_stopping": "Stopping analysis...",
            
            # Analysis tab
            "label_analysis_params": "Proximity Analysis Parameters:",
            "group_detection_params": "Detection Parameters",
            "label_proximity_threshold": "Proximity Threshold (km):",
            "label_time_threshold": "Time Threshold (minutes):",
            "group_analysis_options": "Analysis Options",
            "check_generate_animations": "Generate encounter animations",
            "group_parameter_guide": "Parameter Guide",
            "help_proximity": "• Proximity Threshold: Maximum distance between vultures to count as a proximity event",
            "help_time": "• Time Threshold: Minimum duration for a proximity event to be recorded",
            "help_animations": "• Encounter Animations: Creates interactive maps showing vulture interactions",
            
            # Animation tab
            "label_animation_config": "Animation Configuration:",
            "group_data_range": "Data Range",
            "label_time_buffer": "Time Buffer (hours):",
            "label_trail_length": "Trail Length (hours):",
            "group_animation_quality": "Animation Quality",
            "label_time_step": "Time Step:",
            "label_quality_guide": "Quality Guide:",
            "quality_ultra": "• 1s-30s: Ultra-smooth (slower processing)",
            "quality_balanced": "• 1m-5m: Balanced quality and speed",
            "quality_fast": "• 10m-1h: Fast processing (less detail)",
            "label_point_count": "📊 Point count calculated when data is loaded",
            "point_count_format": "📊 {0} {1} Points ({2:.1f}% reduction from {3:,})",
            "group_performance": "Performance Options",
            "label_limit_encounters": "Limit Encounters (0 = all):",
            "limit_no_limit": "No limit",
            "limit_encounters": "encounters",
            
            # Results tab
            "label_analysis_results": "Analysis Results:",
            "group_generated_files": "Generated Files",
            
            # Log tab
            "label_analysis_log": "Analysis Log:",
            
            # Messages and logs
            "log_starting": "🚀 Starting Vulture Proximity Analysis...",
            "log_data_folder": "📁 Data folder:",
            "log_loading_data": "📊 Loading GPS data...",
            "log_loaded_files": "✅ Loaded {0} GPS data files",
            "log_proximity_threshold": "⚙️  Proximity threshold: {0} km",
            "log_time_threshold": "⚙️  Time threshold: {0} minutes",
            "log_analyzing": "🔍 Analyzing proximity events...",
            "log_found_events": "✅ Found {0} proximity events!",
            "log_no_events": "⚠️  No proximity events found with current parameters",
            "log_try_increase": "💡 Try increasing the proximity threshold or check your data",
            "log_creating_animations": "🎬 Creating encounter animations...",
            "log_found_encounters": "🎬 Found {0} encounter group(s) to animate",
            "log_limited_encounters": "⚡ Limited to first {0} encounters for performance",
            "log_creating_animation": "🎨 Creating animation for encounter {0}/{1}...",
            "log_no_gps_data": "⚠️  No GPS data found for encounter {0}, skipping...",
            "log_encounter_animated": "✅ Encounter {0} animated: {1} ({2:.1f} min)",
            "log_animation_interrupted": "⚠️  Animation interrupted at encounter {0}",
            "log_animation_error": "❌ Error animating encounter {0}: {1}",
            "log_animations_success": "🎉 Successfully created {0} encounter animations!",
            "log_no_animations": "⚠️  No encounter animations were created",
            "log_calculating_stats": "📊 Calculating statistics...",
            "log_creating_visualizations": "📈 Creating visualizations...",
            "log_exporting_results": "💾 Exporting results...",
            "log_events_saved": "📄 Events data saved to: {0}",
            "log_analysis_complete": "🎉 Proximity analysis completed successfully!",
            "log_analysis_failed": "❌ Analysis failed: {0}",
            "log_stop_requested": "🛑 Stop requested by user...",
            
            # Error messages
            "error_no_data": "❌ Folder not found: {0}",
            "error_no_csv": "⚠️ No CSV files found in: {0}",
            "error_reading_folder": "❌ Error reading data folder: {0}",
            "error_large_dataset": "⚠️  Large dataset detected. Consider using larger time steps for animations.",
            "error_no_gps_found": "❌ No GPS data found!",
            "error_animation_failed": "❌ Animation creation failed: {0}",
            
            # Data preview
            "preview_folder": "📁 Data Folder: {0}",
            "preview_found_files": "📄 Found {0} CSV file(s):",
            "preview_total_points": "📊 Total GPS points: {0:,}",
            "preview_file_ok": "✅ {0:<30} ({1:,} GPS points)",
            "preview_file_error": "❌ {0:<30} (Error: {1})",
            
            # Results display
            "results_title": "🦅 VULTURE PROXIMITY ANALYSIS RESULTS",
            "results_separator": "=" * 50,
            "results_summary": "📊 SUMMARY STATISTICS:",
            "results_total_events": "• Total proximity events: {0:,}",
            "results_unique_pairs": "• Unique vulture pairs: {0}",
            "results_avg_distance": "• Average distance: {0:.2f} km",
            "results_closest": "• Closest encounter: {0:.2f} km",
            "results_total_time": "• Total proximity time: {0:.1f} hours",
            "results_most_active": "• Most active pair: {0}",
            "results_peak_hour": "• Peak activity hour: {0}:00",
            "results_by_vulture": "🦅 EVENTS BY VULTURE:",
            "results_by_hour": "⏰ EVENTS BY HOUR:",
            "results_events": "• {0}: {1} events",
            "results_hour": "• {0:02d}:00: {1} events",
            
            # Validation messages
            "validation_select_folder": "Please select a valid data folder!",
            "validation_analysis_running": "Analysis is already running!",
            
            # File operations
            "file_save_log": "Save Log File",
            "file_save_success": "Log saved to {0}",
            "file_save_error": "Failed to save log: {0}",
            "file_open_error": "Failed to open file: {0}",
            "file_folder_error": "Failed to open folder: {0}",
            
            # Time labels
            "time_hours": "{0:.1f} hours",
            "time_km": "{0:.1f} km",
            "time_min": "{0} min",
            
            # Help dialog
            "help_content": """
🦅 Vulture Proximity Analysis - Help

OVERVIEW:
This application analyzes GPS tracking data to identify when vultures are in close proximity to each other.

TABS:
📁 Data: Select your GPS data folder and preview files
⚙️ Analysis: Configure proximity detection parameters  
🎬 Animation: Configure encounter animation settings
📊 Results: View analysis results and statistics
📝 Log: Monitor analysis progress and messages

QUICK START:
1. Select your GPS data folder in the Data tab
2. Adjust proximity and time thresholds in Analysis tab
3. Optionally enable encounter animations
4. Click "Run Analysis" to start

TIPS:
• Use larger proximity thresholds for initial exploration
• Enable animations only for smaller datasets initially
• Check the log for detailed progress information
• Results are saved in the visualizations folder

For more information, visit the project documentation.
            """
        }
    
    def set_language(self, language_code: str):
        """Set the current language"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_current_language(self) -> str:
        """Get the current language code"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their display names"""
        return {
            "de": "Deutsch",
            "en": "English"
        }
    
    def t(self, key: str, *args) -> str:
        """
        Translate a key to the current language
        
        Args:
            key: Translation key
            *args: Arguments for string formatting
            
        Returns:
            Translated string
        """
        try:
            translation = self.translations[self.current_language].get(key, key)
            if args:
                return translation.format(*args)
            return translation
        except (KeyError, IndexError):
            # Fallback to English if translation fails
            try:
                translation = self.translations["en"].get(key, key)
                if args:
                    return translation.format(*args)
                return translation
            except Exception:
                return key  # Ultimate fallback
    
    def save_language_preference(self, language_code: str):
        """Save language preference to file"""
        try:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, '.language_config')
            with open(config_file, 'w') as f:
                json.dump({"language": language_code}, f)
        except Exception:
            pass  # Silently fail if we can't save preferences
    
    def load_language_preference(self) -> str:
        """Load language preference from file"""
        try:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, '.language_config')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get("language", "de")  # Default to German
        except Exception:
            pass
        return "de"  # Default to German


# Global translator instance
_translator = None


def get_translator() -> Translator:
    """Get the global translator instance"""
    global _translator
    if _translator is None:
        _translator = Translator()
        # Load saved language preference
        saved_lang = _translator.load_language_preference()
        _translator.set_language(saved_lang)
    return _translator


def t(key: str, *args) -> str:
    """Convenience function for translation"""
    return get_translator().t(key, *args)
