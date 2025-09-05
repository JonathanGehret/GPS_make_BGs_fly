#!/usr/bin/env python3
"""
Proximity Analysis GUI - Internationalization Handler

Manages language switching and UI text updates for the proximity analysis GUI.
"""


class ProximityI18nHandler:
    """Handles internationalization for the Proximity Analysis GUI"""
    
    def __init__(self, config, translator):
        self.config = config
        self.translator = translator
        config.translator = translator
    
    def change_language_dropdown(self, event=None):
        """Handle language dropdown change event"""
        if hasattr(self.config, 'language_var') and hasattr(self.config, 'language_dropdown'):
            selected = self.config.language_var.get()
            if selected in ['English', 'Deutsch']:
                new_lang = 'en' if selected == 'English' else 'de'
                self.switch_language(new_lang)
    
    def switch_language(self, new_lang='en'):
        """Switch to a new language and update all UI text"""
        if self.translator:
            self.translator.set_language(new_lang)
            self.translator.save_language_preference(new_lang)
            
            # Update all UI text
            self.update_ui_text()
    
    def update_ui_text(self):
        """Update all UI elements with current language"""
        if not self.translator:
            return
            
        try:
            # Update window title
            self.config.root.title(self.translator.t("app_title"))
            
            # Update main title
            if self.config.title_label:
                self.config.title_label.config(text=self.translator.t("app_title"))
            
            # Update tab names
            if self.config.notebook:
                try:
                    tab_count = len(self.config.notebook.tabs())
                    if tab_count == 3:
                        # New merged layout: Data & Analysis, Animation & Results, Log
                        label0 = self.translator.t("tab_data") + " & " + self.translator.t("tab_analysis")
                        label1 = self.translator.t("tab_animation") + " & " + self.translator.t("tab_results")
                        self.config.notebook.tab(0, text=label0)
                        self.config.notebook.tab(1, text=label1)
                        self.config.notebook.tab(2, text=self.translator.t("tab_log"))
                    elif tab_count == 4:
                        # Previous merged layout: Data & Analysis, Animation, Results, Log
                        label0 = self.translator.t("tab_data") + " & " + self.translator.t("tab_analysis")
                        self.config.notebook.tab(0, text=label0)
                        self.config.notebook.tab(1, text=self.translator.t("tab_animation"))
                        self.config.notebook.tab(2, text=self.translator.t("tab_results"))
                        self.config.notebook.tab(3, text=self.translator.t("tab_log"))
                    elif tab_count == 5:
                        # Legacy layout: Data, Analysis, Animation, Results, Log
                        self.config.notebook.tab(0, text=self.translator.t("tab_data"))
                        self.config.notebook.tab(1, text=self.translator.t("tab_analysis"))
                        self.config.notebook.tab(2, text=self.translator.t("tab_animation"))
                        self.config.notebook.tab(3, text=self.translator.t("tab_results"))
                        self.config.notebook.tab(4, text=self.translator.t("tab_log"))
                except Exception:
                    pass
            
            # Update button texts
            self._update_button_texts()
            
            # Update status
            self._update_status_text()
            
            # Update tab-specific text
            self._update_data_tab_text()
            self._update_analysis_tab_text()
            self._update_animation_tab_text()
            self._update_results_tab_text()
            self._update_log_tab_text()
            
        except Exception:
            pass  # Gracefully handle any UI update errors
    
    def _update_button_texts(self):
        """Update button texts with current language"""
        if self.config.run_button:
            self.config.run_button.config(text=self.translator.t("btn_run"))
        if self.config.stop_button:
            self.config.stop_button.config(text=self.translator.t("btn_stop"))
        if self.config.open_results_button:
            self.config.open_results_button.config(text=self.translator.t("btn_open_results"))
        if self.config.help_button:
            self.config.help_button.config(text=self.translator.t("btn_help"))
        if self.config.browse_output_button:
            self.config.browse_output_button.config(text=self.translator.t("btn_browse"))
    
    def _update_status_text(self):
        """Update status text with current language"""
        current_status = self.config.status_var.get()
        if "Ready" in current_status or "Bereit" in current_status:
            self.config.status_var.set(self.translator.t("status_ready"))
        elif "Running" in current_status or "Führe" in current_status:
            self.config.status_var.set(self.translator.t("status_running"))
        elif "completed" in current_status or "abgeschlossen" in current_status:
            self.config.status_var.set(self.translator.t("status_completed"))
    
    def _update_data_tab_text(self):
        """Update data tab specific text"""
        # This would be implemented by the UI builder that creates the data tab
        pass
    
    def _update_analysis_tab_text(self):
        """Update analysis tab specific text"""
        # This would be implemented by the UI builder that creates the analysis tab
        pass
    
    def _update_animation_tab_text(self):
        """Update animation tab specific text"""
        # This would be implemented by the UI builder that creates the animation tab
        pass
    
    def _update_results_tab_text(self):
        """Update results tab specific text"""
        # This would be implemented by the UI builder that creates the results tab
        pass
    
    def _update_log_tab_text(self):
        """Update log tab specific text"""
        # This would be implemented by the UI builder that creates the log tab
        pass
