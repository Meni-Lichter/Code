"""Belonging Panel - Shows related entities (12NCs for rooms, rooms for 12NCs)"""

import customtkinter as ctk


class BelongingPanel:
    """Manages the Belonging List panel content and updates"""
    
    def __init__(self, panel_widget, colors, font_sizes, get_font_func):
        """Initialize the belonging panel manager
        
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
        """Update panel with related entities
        
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
        
        # Create scrollable frame for belonging list
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mode-specific content
        if mode == "room":
            self._show_room_components(scroll_frame, entity_obj)
        else:  # 12nc mode
            self._show_12nc_rooms(scroll_frame, entity_obj)
    
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
    
    def _show_room_components(self, parent, room_obj):
        """Show 12NC components in the room
        
        Args:
            parent: Parent widget
            room_obj: Room object
        """
        # Header
        header_label = ctk.CTkLabel(
            parent,
            text=f"Components in {room_obj.id}",
            font=self._get_font(size=self.FONT_SIZES["title"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        header_label.pack(pady=(0, 15))
        
        # Check if there are components
        if not room_obj.componenets:
            no_data_label = ctk.CTkLabel(
                parent,
                text="No components found",
                font=self._get_font(size=self.FONT_SIZES["body"]),
                text_color=self.COLORS["text_light"]
            )
            no_data_label.pack(pady=20)
            return
        
        # List components
        for nc12_id, quantity in room_obj.componenets.items():
            self._add_belonging_item(parent, nc12_id, quantity, "12NC")
    
    def _show_12nc_rooms(self, parent, nc12_obj):
        """Show rooms containing this 12NC
        
        Args:
            parent: Parent widget
            nc12_obj: TwelveNC object
        """
        # Header
        header_label = ctk.CTkLabel(
            parent,
            text=f"Rooms containing {nc12_obj.id}",
            font=self._get_font(size=self.FONT_SIZES["title"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        header_label.pack(pady=(0, 15))
        
        # Check if deployed in any rooms
        if not nc12_obj.componenets:
            no_data_label = ctk.CTkLabel(
                parent,
                text="Not deployed in any rooms",
                font=self._get_font(size=self.FONT_SIZES["body"]),
                text_color=self.COLORS["text_light"]
            )
            no_data_label.pack(pady=20)
            return
        
        # List rooms
        for room_id, quantity in nc12_obj.componenets.items():
            self._add_belonging_item(parent, room_id, quantity, "Room")
    
    def _add_belonging_item(self, parent, item_id, quantity, item_type):
        """Add a belonging item row
        
        Args:
            parent: Parent widget
            item_id: ID of the item
            quantity: Quantity
            item_type: Type label ('12NC' or 'Room')
        """
        item_frame = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["bg_white"],
            corner_radius=8,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        item_frame.pack(fill="x", pady=5, padx=5)
        
        # Create inner frame for padding
        inner_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=15, pady=12)
        
        # Item ID
        id_label = ctk.CTkLabel(
            inner_frame,
            text=item_id,
            font=self._get_font(size=self.FONT_SIZES["body"], weight="bold"),
            text_color=self.COLORS["text_dark"],
            anchor="w"
        )
        id_label.pack(side="left", fill="x", expand=True)
        
        # Quantity badge
        qty_badge = ctk.CTkLabel(
            inner_frame,
            text=f"Qty: {quantity}",
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["bg_white"],
            fg_color=self.COLORS["accent_teal"],
            corner_radius=6,
            padx=10,
            pady=4
        )
        qty_badge.pack(side="right")
