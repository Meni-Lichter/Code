"""Entity Mode Screen - Shared by 12NC and Room analysis modes"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Listbox


class EntityModeScreen(ctk.CTkFrame):
    """Main analysis screen with 2x2 grid layout for 12NC and Room modes"""
    
    # ============================================================================
    # THEME CONFIGURATION & CONSTANTS
    # ============================================================================
    
    # Color scheme
    COLORS = {
        "bg_main": "#EEF2F6",
        "bg_panel": "#F8FAFC",
        "bg_white": "#FFFFFF",
        "bg_light": "#E7EDF3",
        "bg_input": "#F8FAFC",
        "border": "#D8E0E8",
        "border_light": "#DCE4EC",
        "text_dark": "#1E2A33",
        "text_muted": "#5F6E7C",
        "text_light": "#8A98A6",
        "text_lighter": "#A8B3BD",
        "text_button": "#2B3A44",
        "accent_dark": "#35586E",
        "accent_hover": "#2F4F63",
        "accent_teal": "#4A8F93",
        "accent_teal_hover": "#3F7F83",
    }
    
    # Font sizes (stored for easy caching)
    FONT_SIZES = {
        "header": 36,
        "title": 20,
        "label": 18,
        "body": 17,
        "small": 15,
        "xsmall": 10,
    }
    
    # Mode configuration - defaults (will be populated from uploaded files)
    MODE_CONFIG = {
        "12nc": {
            "key": "12nc",
            "display": "12NC",
            "title": "12NC Component Analysis",
            "description": "Search and analyze component performance, belonging relationships, and demand forecasts",
            "items": [],  # Will be populated from loaded CBOM data
        },
        "room": {
            "key": "room",
            "display": "Room",
            "title": "Room Performance Analysis",
            "description": "Analyze room performance metrics, deployed components, and predict future demand",
            "items": [],  # Will be populated from loaded CBOM data
        },
    }
    
    def __init__(self, parent, app_controller, mode="12nc"):
        super().__init__(parent, fg_color=self.COLORS["bg_main"])
        
        self.app_controller = app_controller
        self.current_mode = mode
        self.selected_entity = None
        
        # Cache fonts to avoid recreating them repeatedly
        self._font_cache = {}
        
        # Populate sample data from previously loaded CBOM data
        self._initialize_sample_data_from_controller()
        
        # Store all items for current mode (for filtering)
        self.all_items = self.MODE_CONFIG[mode]["items"]
        
        # Configure grid weights for responsive layout
        self.grid_rowconfigure(0, weight=0)  # Title header (fixed)
        self.grid_rowconfigure(1, weight=0)  # Search area (fixed)
        self.grid_rowconfigure(2, weight=1)  # Top row panels
        self.grid_rowconfigure(3, weight=1)  # Bottom row panels
        self.grid_columnconfigure(0, weight=1)  # Left column
        self.grid_columnconfigure(1, weight=1)  # Right column
        
        # Create UI components
        self._create_title_header()
        self._create_search_area()
        self._create_grid_panels()
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_font(self, family="Segoe UI", size=15, weight="normal"):
        """Get or create cached font to avoid memory overhead"""
        key = (family, size, weight)
        if key not in self._font_cache:
            self._font_cache[key] = ctk.CTkFont(family=family, size=size, weight=weight)  # type: ignore
        return self._font_cache[key]
    
    def _initialize_sample_data_from_controller(self):
        """Load sample data from app controller's loaded CBOM files
        
        Checks if the app controller has loaded Room and TwelveNC data from CBOM files,
        and populates MODE_CONFIG items with actual entity IDs from those files.
        """
        try:
            # Try to get loaded data from the app controller
            if hasattr(self.app_controller, 'current_data') and self.app_controller.current_data:
                current_data = self.app_controller.current_data
                
                # Extract Room and TwelveNC objects if available
                if 'rooms' in current_data:
                    room_ids = [room.id for room in current_data['rooms']]
                    self.MODE_CONFIG["room"]["items"] = sorted(room_ids)
                
                if 'nc12s' in current_data:
                    nc12_ids = [nc12.id for nc12 in current_data['nc12s']]
                    self.MODE_CONFIG["12nc"]["items"] = sorted(nc12_ids)
        except (AttributeError, KeyError, TypeError):
            # If data isn't available or in expected format, keep empty lists
            pass
    
    def reload_sample_data_from_uploaded_files(self, rooms_list, nc12_list):
        """Update sample data when new CBOM files are uploaded and processed
        
        Args:
            rooms_list: List of Room objects from data_transformer
            nc12_list: List of TwelveNC objects from data_transformer
        """
        # Extract and sort IDs from the loaded data
        room_ids = sorted([room.id for room in rooms_list]) if rooms_list else []
        nc12_ids = sorted([nc12.id for nc12 in nc12_list]) if nc12_list else []
        
        # Update MODE_CONFIG with actual loaded data
        self.MODE_CONFIG["room"]["items"] = room_ids
        self.MODE_CONFIG["12nc"]["items"] = nc12_ids
        
        # Update current mode's all_items
        self.all_items = self.MODE_CONFIG[self.current_mode]["items"]
        
        # Always refresh the dropdown listbox with new items
        # (don't wait for it to be opened - populate it now so it's ready)
        self._populate_dropdown(self.all_items)
    
    def _create_button(self, parent, text, command, width=120, height=48, 
                      fg_color=None, hover_color=None, is_secondary=False):
        """Create a styled button with consistent appearance
            Args:
                parent: The parent widget to attach the button to
                text: The text to display on the button
                command: The function to call when the button is clicked
                width: The width of the button (default 120)
                height: The height of the button (default 48)
                fg_color: The background color of the button (optional)
                hover_color: The background color when hovering (optional)
                is_secondary: Whether to use secondary styling (optional)
            Does: Creates and returns a styled button with the specified properties
            returns: The created button instance  
        """
        if fg_color is None:
            fg_color = self.COLORS["accent_dark"] if not is_secondary else self.COLORS["bg_light"]
        if hover_color is None:
            hover_color = self.COLORS["accent_hover"] if not is_secondary else self.COLORS["border_light"]
        
        text_color = "white" if not is_secondary else self.COLORS["text_button"]
        font_weight = "bold" if not is_secondary else "normal"
        
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=8,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=self._get_font(size=self.FONT_SIZES["body"], weight=font_weight)
        )
    
    def _create_icon_button(self, parent, text, command, tooltip_text=None):
        """Create a small icon button with optional tooltip
            Args:
                parent: The parent widget to attach the button to
                text: The text or emoji to display on the button
                command: The function to call when the button is clicked
                tooltip_text: Optional text for a tooltip to explain the button's function
            Does: Creates and returns a small icon button with consistent styling and an optional tooltip
            Returns: The created button instance        
        """
        btn = ctk.CTkButton(
            parent,
            text=text,
            width=38,
            height=38,
            corner_radius=6,
            fg_color=self.COLORS["bg_light"],
            hover_color=self.COLORS["border_light"],
            text_color=self.COLORS["text_button"],
            border_width=1,
            border_color=self.COLORS["border"],
            font=self._get_font(size=18),
            command=command
        )
        if tooltip_text:
            self._create_tooltip(btn, tooltip_text)
        return btn
    
    def _create_title_header(self):
        """Create title and description header
            Args: None
            Does: Initializes the title and description labels at the top of the screen
            Returns: None
        """
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 15))
        
        mode_config = self.MODE_CONFIG[self.current_mode]
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=mode_config["title"],
            font=self._get_font(size=self.FONT_SIZES["header"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        self.title_label.pack()
        
        # Description
        self.description_label = ctk.CTkLabel(
            header_frame,
            text=mode_config["description"],
            font=self._get_font(size=self.FONT_SIZES["label"]),
            text_color=self.COLORS["text_muted"]
        )
        self.description_label.pack(pady=(5, 0))
    
    def _create_search_area(self):
        """Create search area split into two equal sections: search (left) and toggle (right)
            Args: None
            Does: Initializes the search area with search and toggle sections
            Returns: None
        """
        search_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        search_container.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        
        # Configure grid for equal width distribution
        search_container.grid_columnconfigure(0, weight=1)
        search_container.grid_columnconfigure(1, weight=1)
        
        # Left side: Search section
        self._create_search_section(search_container)
        
        # Right side: Toggle section
        self._create_toggle_section(search_container)
    
    def _create_search_section(self, parent):
        """Create search input and dropdown components (left half of search area)
            Args:
                parent: The parent widget to attach the search section to
            Does: Initializes the search input and dropdown components on the left side of the search area
            Returns: None
        """
        # Search container
        search_section = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_white"], corner_radius=12, border_width=2, border_color=self.COLORS["border"])
        search_section.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Configure grid for responsive layout - make it fill available width
        search_section.grid_rowconfigure(0, weight=0)
        search_section.grid_rowconfigure(1, weight=1)
        search_section.grid_columnconfigure(0, weight=1)
        
        # Search section header
        search_content = ctk.CTkFrame(search_section, fg_color="transparent")
        search_content.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        search_content.grid_columnconfigure(1, weight=1)  # Make input_container expand
        
        # Search label
        search_label = ctk.CTkLabel(
            search_content,
            text="🔍 Search:",
            font=self._get_font(size=self.FONT_SIZES["label"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        search_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Search input and dropdown container
        input_container = ctk.CTkFrame(search_content, fg_color="transparent")
        input_container.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        input_container.grid_columnconfigure(0, weight=1)  # Entry expands
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        
        self.search_entry = ctk.CTkEntry(
            input_container,
            textvariable=self.search_var,
            placeholder_text=f"Type to search {self.MODE_CONFIG[self.current_mode]['display']}...",
            height=48,
            font=self._get_font(size=self.FONT_SIZES["body"]),
            fg_color=self.COLORS["bg_input"],
            border_color=self.COLORS["border"],
            border_width=2,
            text_color=self.COLORS["text_dark"],
            placeholder_text_color=self.COLORS["text_light"]
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<FocusIn>", self._on_entry_focus)
        self.search_entry.bind("<FocusOut>", self._on_entry_blur)
        
        # Dropdown toggle button with arrow
        self.dropdown_toggle_btn = ctk.CTkButton(
            input_container,
            text="▼",
            width=48,
            height=48,
            corner_radius=8,
            fg_color=self.COLORS["bg_light"],
            hover_color=self.COLORS["border_light"],
            text_color=self.COLORS["text_button"],
            border_width=2,
            border_color=self.COLORS["border"],
            font=self._get_font(size=20, weight="bold"),
            command=self._toggle_dropdown
        )
        self.dropdown_toggle_btn.grid(row=0, column=1, sticky="e", padx=(0, 5))
        self._create_tooltip(self.dropdown_toggle_btn, "Show/hide dropdown list")
        
        # Search button
        search_btn = self._create_button(
            search_content,
            "Search",
            self._on_search_button,
            width=120,
            height=48
        )
        search_btn.grid(row=0, column=2, sticky="e")
        self._create_tooltip(search_btn, f"Search for {self.MODE_CONFIG[self.current_mode]['display']}")
        
        # Dropdown list (initially hidden)
        self.dropdown_frame = ctk.CTkFrame(
            search_section, 
            fg_color=self.COLORS["bg_white"], 
            corner_radius=8, 
            border_width=2, 
            border_color=self.COLORS["border"]
        )
        self.dropdown_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 0))
        self.dropdown_frame.grid_remove()  # Hide initially
        
        self.dropdown_listbox = Listbox(
            self.dropdown_frame,
            font=("Segoe UI", self.FONT_SIZES["small"]),
            bg=self.COLORS["bg_white"],
            fg=self.COLORS["text_dark"],
            selectbackground=self.COLORS["accent_teal"],
            selectforeground=self.COLORS["bg_white"],
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            height=8
        )
        self.dropdown_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.dropdown_listbox.bind("<<ListboxSelect>>", self._on_dropdown_select)
        self.dropdown_listbox.bind("<Button-1>", self._on_dropdown_select)
        
        self.dropdown_visible = False
        
        # Populate dropdown with initial items from current mode
        self._populate_dropdown(self.all_items)
    
    def _create_toggle_section(self, parent):
        """Create mode toggle components (right half of search area)
            Args:
                parent: The parent widget to attach the toggle section to
            Does: Initializes the mode toggle components on the right side of the search area
            Returns: None
        """
        # Toggle container
        toggle_section = ctk.CTkFrame(parent, fg_color=self.COLORS["bg_white"], corner_radius=12, border_width=2, border_color=self.COLORS["border"])
        toggle_section.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        # Configure grid to center content
        toggle_section.grid_rowconfigure(0, weight=1)
        toggle_section.grid_columnconfigure(0, weight=1)
        
        toggle_content = ctk.CTkFrame(toggle_section, fg_color="transparent")
        toggle_content.grid(row=0, column=0, padx=15, pady=15)
        
        # Toggle label
        toggle_label = ctk.CTkLabel(
            toggle_content,
            text="Mode:",
            font=self._get_font(size=self.FONT_SIZES["label"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        toggle_label.pack(pady=(0, 10))
        
        # Mode toggle using segmented button
        self.mode_toggle = ctk.CTkSegmentedButton(
            toggle_content,
            values=["12NC", "Room"],
            command=self._on_mode_toggle,
            height=50,
            corner_radius=8,
            fg_color=self.COLORS["bg_light"],
            selected_color=self.COLORS["accent_teal"],
            selected_hover_color=self.COLORS["accent_teal_hover"],
            unselected_color=self.COLORS["bg_white"],
            unselected_hover_color=self.COLORS["bg_input"],
            text_color=self.COLORS["text_dark"],
            font=self._get_font(size=self.FONT_SIZES["label"], weight="bold"),
            border_width=2
        )
        self.mode_toggle.pack()
        
        # Set initial value
        self.mode_toggle.set(self.MODE_CONFIG[self.current_mode]["display"])
    
    def _create_grid_panels(self):
        """Create 2x2 grid with four main panels        
            Args: None
            Does: Initializes the 2x2 grid layout with four main panels
            Returns: None
        """
        # Top-left: Belonging List
        self.belonging_panel = self._create_panel(
            row=2, column=0,
            title="📦 Belonging List",
            content_text="Selected entity and related items will appear here"
        )
        
        # Top-right: Details
        self.details_panel = self._create_panel(
            row=2, column=1,
            title="ℹ️ Details",
            content_text="Entity information and metadata"
        )
        
        # Bottom-left: Performance
        self.performance_panel = self._create_panel(
            row=3, column=0,
            title="📈 Performance",
            content_text="Historical sales chart will appear here"
        )
        
        # Bottom-right: Prediction
        self.prediction_panel = self._create_panel(
            row=3, column=1,
            title="🔮 Prediction",
            content_text="Forecast and prediction data"
        )
    
    def _create_panel(self, row, column, title, content_text):
        """Create a single panel in the grid 
            Args:
                row: The row index for the panel
                column: The column index for the panel
                title: The title text to display in the panel header
                content_text: The placeholder text to display in the panel content area
            Does: Creates and returns a panel with a header and content area, placed in the specified grid location
            Returns: The created panel instance
        """
        # Panel container
        panel = ctk.CTkFrame(
            self,
            fg_color=self.COLORS["bg_panel"],
            corner_radius=12,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        panel.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
        
        # Configure panel grid
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header = ctk.CTkFrame(panel, fg_color=self.COLORS["bg_white"], corner_radius=0, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=self._get_font(size=self.FONT_SIZES["title"], weight="bold"),
            text_color=self.COLORS["text_dark"],
            anchor="w"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Export buttons frame
        export_frame = ctk.CTkFrame(header, fg_color="transparent")
        export_frame.pack(side="right", padx=15)
        
        # Excel export
        excel_btn = self._create_icon_button(
            export_frame,
            "📊",
            lambda: self._export_panel(title, "excel"),
            "Export to Excel"
        )
        excel_btn.pack(side="left", padx=2)
        
        # PNG export
        png_btn = self._create_icon_button(
            export_frame,
            "🖼️",
            lambda: self._export_panel(title, "png"),
            "Export as PNG image"
        )
        png_btn.pack(side="left", padx=2)
        
        # Separator
        separator = ctk.CTkFrame(panel, height=1, fg_color=self.COLORS["border"])
        separator.grid(row=0, column=0, sticky="ews", pady=(60, 0))
        
        # Content area
        content = ctk.CTkFrame(panel, fg_color=self.COLORS["bg_white"], corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew")
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            content,
            text=content_text,
            font=self._get_font(size=self.FONT_SIZES["label"]),
            text_color=self.COLORS["text_light"]
        )
        placeholder.pack(expand=True, pady=50)
        
        # Coming soon label
        coming_soon = ctk.CTkLabel(
            content,
            text="Implementation: Stage 3+",
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["text_lighter"]
        )
        coming_soon.pack(pady=(0, 50))
        
        return panel
    
    # ============================================================================
    # MODE MANAGEMENT
    # ============================================================================
    
    def _switch_mode(self, new_mode):
        """Centralized mode switching logic        
            Args:
                new_mode: The mode to switch to
            Does: Switches the current mode to the new mode and updates relevant components
            Returns: None
        """
        if new_mode == self.current_mode:
            return
            
        self.current_mode = new_mode
        self._update_data_for_mode()
        self._update_ui_for_mode()
        self._update_search_for_mode()
        self._update_navigation_for_mode()
    
    def _update_data_for_mode(self):
        """Update data lists based on current mode
            Args: None        
            Does: Updates the list of all items based on the current mode
            Returns: None
        """
        self.all_items = self.MODE_CONFIG[self.current_mode]["items"]
    
    def _update_ui_for_mode(self):
        """Update UI components for current mode
            Args: None
            Does: Updates the title, description, and mode toggle button to reflect the current mode
            Returns: None
        """
        mode_config = self.MODE_CONFIG[self.current_mode]
        
        self.title_label.configure(text=mode_config["title"])
        self.description_label.configure(text=mode_config["description"])
        self.mode_toggle.set(mode_config["display"])
    
    def _update_navigation_for_mode(self):
        """Update side menu navigation highlight
            Args: None
            Does: Highlights the active mode in the side menu if it exists
            Returns: None
        """
        screen_name = f"{self.current_mode}_mode"
        if hasattr(self.app_controller, 'side_menu'):
            self.app_controller.side_menu._highlight_active_button(screen_name)
    
    def _on_mode_change(self, value):
        """Handle mode change from side menu
            Args:
                value: The new mode value from the side menu
            Does: Switches to the selected mode
            Returns: None
        """
        # Always update - don't skip even if same mode
        self._update_data_for_mode()
        self._update_ui_for_mode()
        self._update_search_for_mode()
        self._update_navigation_for_mode()
    
    def _on_mode_toggle(self, value):
        """Handle mode toggle button click
            Args:
                value: The new mode value from the toggle button
            Does: Switches to the selected mode based on the toggle button value
            Returns: None
        """
        new_mode = "12nc" if value == "12NC" else "room"
        # Only switch if different from current mode
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self._update_data_for_mode()
            self._update_ui_for_mode()
            self._update_search_for_mode()
            self._update_navigation_for_mode()
    
    # ============================================================================
    # SEARCH FUNCTIONALITY
    # ============================================================================
    
    def _update_search_for_mode(self):
        """Update search components for current mode
            Args: None
            Does: Updates the search entry and dropdown for the current mode
            Returns: None
        """
        mode_display = self.MODE_CONFIG[self.current_mode]["display"]
        self.search_entry.configure(placeholder_text=f"Type to search {mode_display}...")
        self.search_var.set("")
        # Populate dropdown with the new mode's items
        self._populate_dropdown(self.all_items)
        self._hide_dropdown()
    
    # ============================================================================
    # DROPDOWN METHODS
    # ============================================================================
    
    def _toggle_dropdown(self):
        """Toggle dropdown visibility
            Args: None
            Does: Shows the dropdown if it's hidden, or hides it if it's visible
            Returns: None
        """
        if self.dropdown_visible:
            self._hide_dropdown()
        else:
            self._populate_dropdown(self.all_items)
            self._show_dropdown()

    def _populate_dropdown(self, items):
        """Populate dropdown with items
            Args:
                items: List of items to populate the dropdown
            Does: Clears the dropdown and inserts the provided items
            Returns: None
        """
        self.dropdown_listbox.delete(0, tk.END)
        for item in items:
            self.dropdown_listbox.insert(tk.END, item)

    def _filter_and_show_dropdown(self, search_text):
        """Filter items and show dropdown (optimized - no double clearing)
            Args:
                search_text: The text to filter the dropdown items by
            Does: Filters the list of all items based on the search text and updates the dropdown accordingly
            Returns: None
        """
        if not search_text:
            self._hide_dropdown()
            return

        filtered = [item for item in self.all_items if search_text.lower() in item.lower()]

        # Clear and populate in one step
        self.dropdown_listbox.delete(0, tk.END)
        if filtered:
            for item in filtered:
                self.dropdown_listbox.insert(tk.END, item)
        else:
            self.dropdown_listbox.insert(tk.END, "No matches found")

        self._show_dropdown()

    def _on_search_change(self, *args):
        """Handle search text changes
            Args: None
            Does: Filters the dropdown items based on the current search text whenever it changes
            Returns: None
        """
        search_text = self.search_var.get().strip()
        self._filter_and_show_dropdown(search_text)

    def _on_entry_focus(self, event):
        """Show all items when entry gets focus
            Args: None
            Does: Shows the dropdown with all items when the search entry gains focus, if the search text is empty
            Returns: None
        """
        if not self.search_var.get().strip():
            self._populate_dropdown(self.all_items)
            self._show_dropdown()

    def _on_entry_blur(self, event):
        """Hide dropdown when losing focus
            Args: None
            Does: Hides the dropdown when the search entry loses focus
            Returns: None
        """
        self.after(200, self._check_hide_dropdown)

    def _check_hide_dropdown(self):
        """Check if dropdown should be hidden
            Args: None
            Does: Checks if the dropdown should be hidden based on the pointer location
            Returns: None
        """
        try:
            if not self.dropdown_listbox.winfo_containing(self.winfo_pointerx(), self.winfo_pointery()):
                self._hide_dropdown()
        except tk.TclError:
            # Widget no longer exists
            pass

    def _on_dropdown_select(self, event):
        """Handle dropdown selection and click (consolidated)
            Args:
                event: The event object from the dropdown selection or click
            Does: Sets the search variable to the selected item and hides the dropdown on click, while allowing selection for preview
            Returns: None
        """
        selection = self.dropdown_listbox.curselection()
        if selection:
            selected = self.dropdown_listbox.get(selection[0])
            if selected != "No matches found":
                self.search_var.set(selected)
                # Hide on click, keep open on selection for preview
                if event.type == tk.EventType.ButtonPress:
                    self._hide_dropdown()
                    self.search_entry.focus()

    def _show_dropdown(self):
        """Show the dropdown list
            Args: None
            Does: Displays the dropdown list if it is not already visible
            Returns: None
        """
        if not self.dropdown_visible:
            self.dropdown_frame.grid()
            self.dropdown_visible = True
            self.dropdown_toggle_btn.configure(text="▲")

    def _hide_dropdown(self):
        """Hide the dropdown list
            Args: None
            Does: Hides the dropdown list if it is currently visible
            Returns: None
        """
        if self.dropdown_visible:
            self.dropdown_frame.grid_remove()
            self.dropdown_visible = False
            self.dropdown_toggle_btn.configure(text="▼")

    def _on_search_button(self):
        """Handle search button click
            Args: None
            Does: Initiates a search based on the current search text and updates the panels
            Returns: None
        """
        search_term = self.search_var.get().strip()
        if search_term and search_term != "No matches found":
            print(f"Searching for {self.current_mode}: {search_term}")
            self.selected_entity = search_term
            self._update_panels()
            self._hide_dropdown()
        else:
            print("Please enter or select a search term")
    
    def _update_panels(self):
        """Update all panels with data for selected entity
            Args: None
            Does: Updates the content of all panels based on the currently selected entity
            Returns: None
        """
        print(f"Updating panels for entity: {self.selected_entity}")
    
    def _export_panel(self, panel_title, format_type):
        """Export panel data to Excel or PNG
            Args:
                panel_title: The title of the panel to export
                format_type: The format to export (e.g., 'excel' or 'png')
            Does: Exports the panel data to the specified format
            Returns: None
        """
        print(f"Exporting '{panel_title}' as {format_type.upper()}")
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget
            Args:
                widget: The widget to attach the tooltip to
                text: The text to display in the tooltip
            Does: Creates a tooltip that appears when hovering over the specified widget
            Returns: None
        """
        tooltip = None
        
        def on_enter(event):
            nonlocal tooltip
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background=self.COLORS["text_dark"],
                foreground=self.COLORS["bg_white"],
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", self.FONT_SIZES["xsmall"]),
                padx=8,
                pady=4
            )
            label.pack()
        
        def on_leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
        
        try:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        except (AttributeError, NotImplementedError):
            # Some CustomTkinter widgets don't support bind
            pass
