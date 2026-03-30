"""Prediction Panel - Shows forecast and prediction data"""

import customtkinter as ctk


class PredictionPanel:
    """Manages the Prediction panel content and updates"""
    
    def __init__(self, panel_widget, colors, font_sizes, get_font_func):
        """Initialize the prediction panel manager
        
        Args:
            panel_widget: The CTkFrame panel widget
            colors: Dictionary of color constants
            font_sizes: Dictionary of font sizes
            get_font_func: Function to get cached fonts
        """
        self.panel = panel_widget
        self.COLORS = colors
        self.FONT_SIZES = font_sizes
        self._get_font = get_font_func
        self.content_frame = None
    
    def update(self, entity_obj, mode):
        """Update panel with prediction data
        
        Args:
            entity_obj: Room or TwelveNC object
            mode: Current mode ('room' or '12nc')
        """
        # Find the content frame in the panel
        self.content_frame = self._find_content_frame()
        
        if not self.content_frame:
            return
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create content frame
        content_inner = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        content_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Placeholder for predictions (Stage 4+)
        self._show_placeholder(content_inner)
    
    def _find_content_frame(self):
        """Find the content frame within the panel widget"""
        # Look for the content frame at grid row=1
        for child in self.panel.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                try:
                    grid_info = child.grid_info()
                    if grid_info and grid_info.get('row') == 1:
                        return child
                except:
                    continue
        return None
    
    def _show_placeholder(self, parent):
        """Show placeholder content for predictions
        
        Args:
            parent: Parent widget
        """
        # Icon
        icon_label = ctk.CTkLabel(
            parent,
            text="🔮",
            font=self._get_font(size=48)
        )
        icon_label.pack(pady=(50, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Predictions Coming Soon",
            font=self._get_font(size=self.FONT_SIZES["title"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            parent,
            text="Demand forecasting and predictive analytics\nwill be available in Stage 4+",
            font=self._get_font(size=self.FONT_SIZES["body"]),
            text_color=self.COLORS["text_muted"]
        )
        desc_label.pack(pady=(0, 50))
