"""Performance Panel - Shows sales history and performance metrics"""

import customtkinter as ctk


class PerformancePanel:
    """Manages the Performance panel content and updates"""
    
    def __init__(self, panel_widget, colors, font_sizes, get_font_func):
        """Initialize the performance panel manager
        
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
        """Update panel with sales performance data
        
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
        
        # Create scrollable frame for performance data
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Show sales history
        self._show_sales_history(scroll_frame, entity_obj, mode)
    
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
    
    def _show_sales_history(self, parent, entity_obj, mode):
        """Show sales history records
        
        Args:
            parent: Parent widget
            entity_obj: Room or TwelveNC object
            mode: Current mode
        """
        # Header
        header_label = ctk.CTkLabel(
            parent,
            text="Sales History",
            font=self._get_font(size=self.FONT_SIZES["title"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        header_label.pack(pady=(0, 15))
        
        # Check if there are sales records
        if not entity_obj.sales_history:
            no_data_label = ctk.CTkLabel(
                parent,
                text="No sales data available",
                font=self._get_font(size=self.FONT_SIZES["body"]),
                text_color=self.COLORS["text_light"]
            )
            no_data_label.pack(pady=20)
            return
        
        # Summary statistics
        self._show_summary_stats(parent, entity_obj.sales_history)
        
        # Separator
        separator = ctk.CTkFrame(parent, height=1, fg_color=self.COLORS["border"])
        separator.pack(fill="x", pady=15)
        
        # Recent sales header
        recent_label = ctk.CTkLabel(
            parent,
            text="Recent Sales (Latest 10)",
            font=self._get_font(size=self.FONT_SIZES["label"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        recent_label.pack(pady=(0, 10))
        
        # Show recent sales records (limit to 10)
        recent_sales = entity_obj.sales_history[-10:] if len(entity_obj.sales_history) > 10 else entity_obj.sales_history
        
        for record in reversed(recent_sales):  # Show most recent first
            self._add_sales_record(parent, record)
    
    def _show_summary_stats(self, parent, sales_history):
        """Show summary statistics
        
        Args:
            parent: Parent widget
            sales_history: List of SalesRecord objects
        """
        # Calculate stats
        total_records = len(sales_history)
        total_quantity = sum(record.quantity for record in sales_history)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["bg_light"],
            corner_radius=8
        )
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Create grid layout for stats
        stats_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_inner.pack(fill="x", padx=15, pady=15)
        stats_inner.grid_columnconfigure((0, 1), weight=1)
        
        # Total Records
        self._add_stat_item(stats_inner, "Total Records", str(total_records), 0, 0)
        
        # Total Quantity
        self._add_stat_item(stats_inner, "Total Quantity", str(total_quantity), 0, 1)
    
    def _add_stat_item(self, parent, label, value, row, col):
        """Add a stat item to the grid
        
        Args:
            parent: Parent widget
            label: Stat label
            value: Stat value
            row: Grid row
            col: Grid column
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        label_widget = ctk.CTkLabel(
            frame,
            text=label,
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["text_muted"]
        )
        label_widget.pack()
        
        value_widget = ctk.CTkLabel(
            frame,
            text=value,
            font=self._get_font(size=self.FONT_SIZES["title"], weight="bold"),
            text_color=self.COLORS["accent_teal"]
        )
        value_widget.pack()
    
    def _add_sales_record(self, parent, record):
        """Add a sales record row
        
        Args:
            parent: Parent widget
            record: SalesRecord object
        """
        record_frame = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["bg_white"],
            corner_radius=8,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        record_frame.pack(fill="x", pady=3, padx=5)
        
        # Inner frame
        inner_frame = ctk.CTkFrame(record_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=12, pady=10)
        inner_frame.grid_columnconfigure(0, weight=1)
        
        # Date and identifier
        id_label = ctk.CTkLabel(
            inner_frame,
            text=f"{record.identifier} - {record.date}",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"],
            anchor="w"
        )
        id_label.grid(row=0, column=0, sticky="w")
        
        # Quantity
        qty_label = ctk.CTkLabel(
            inner_frame,
            text=f"Qty: {record.quantity}",
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["accent_teal"]
        )
        qty_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
