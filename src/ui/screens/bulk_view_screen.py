"""Bulk View Screen - Analyze multiple entities simultaneously"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from typing import Dict, List, Set, Optional
import calendar
from collections import defaultdict
from pathlib import Path

from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.models.performance import PerformanceData
from src.models.mapping import G_entity
from src.ui.theme import COLORS, FONT_SIZES, YEAR_COLORS, GRANULARITY_MAP, GRANULARITY_PERIODS
from src.ui.chart_utils import (
    extract_year_from_period,
    convert_period_label_to_ui,
    get_all_period_labels,
    add_bar_value_labels
)
from src.ui.ui_utils import FontCache
from src.ui.export_utils import export_chart_to_pdf, export_data_to_excel, get_export_folder, export_screen_to_pdf


class BulkViewScreen(ctk.CTkFrame):
    """Bulk analysis screen for comparing multiple entities"""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=COLORS["bg_main"])
        
        self.app_controller = app_controller
        
        # Use centralized theme
        self.COLORS = COLORS
        self.FONT_SIZES = FONT_SIZES
        self.YEAR_COLORS = YEAR_COLORS
        
        # State management
        self.current_mode = "12nc"  # "12nc" or "room"
        self.selected_entities_12nc: Set[str] = set()  # IDs of selected 12NC entities
        self.selected_entities_room: Set[str] = set()  # IDs of selected room entities
        self.search_text = ""
        self.sort_by = "Sales (High to Low)"  # Default sort
        
        # Chart state
        self.granularity = "Months"
        self.selected_years = set()
        self.time_range = (0, 11)
        self.year_checkboxes = {}  # Initialize year checkboxes dict
        
        # UI components
        self.entity_checkboxes = {}  # {entity_id: checkbox_widget}
        self.entity_list_frame = None
        self.canvas = None
        self.figure = None
        self.ax = None
        self.sum_label = None
        self.avg_label = None
        self.count_label = None
        self.year_checkboxes_frame = None  # Initialize frame reference
        
        # Analyzer
        self.analyzer = PerformanceAnalyzer()
        
        # Use centralized granularity mapping
        self.granularity_map = GRANULARITY_MAP
        
        # Configure grid
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Entity list (scrollable, fixed height)
        self.grid_rowconfigure(2, weight=1)  # Chart area
        self.grid_columnconfigure(0, weight=1)
        
        # Build UI
        self._create_header()
        self._create_entity_list_section()
        self._create_chart_section()
        
        # Initialize with data from app controller
        self._initialize_data()
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_font(self, family="Segoe UI", size=15, weight="normal"):
        """Get or create a cached font"""
        return FontCache.get_font(family, size, weight)
    
    def _initialize_data(self):
        """Initialize entity data from app controller - show blank state initially"""
        # Check if data is loaded
        if not hasattr(self.app_controller, 'current_data') or not self.app_controller.current_data:
            return
        
        rooms_dict = self.app_controller.current_data.get('rooms_dict', {})
        nc12s_dict = self.app_controller.current_data.get('nc12s_dict', {})
       
        if not rooms_dict or not nc12s_dict:
            return
        
        # Initialize years from data
        self._initialize_available_years()
        
        # Don't auto-select entities - show blank state
        # self._select_top_entity_by_sales()  # Commented out
        
        # Refresh UI to show entities but none selected
        self._refresh_entity_list()
        # self._update_chart()  # Commented out - will show blank state
    
    def _initialize_available_years(self):
        """Initialize available years from all entities"""
        years = set()
        
        entities = self._get_current_entities()
        for entity in entities:
            if hasattr(entity, 'sales_history'):
                for record in entity.sales_history:
                    years.add(record.date.year)
        
        # Select up to 4 most recent years
        sorted_years = sorted(years, reverse=True)[:4]
        self.selected_years = set(sorted_years)
    
    def _select_top_entity_by_sales(self):
        """Select the entity with most sales overall as default"""
        entities = self._get_current_entities()
        if not entities:
            return
        
        # Calculate total sales for each entity
        entity_sales = {}
        for entity in entities:
            total = 0
            if hasattr(entity, 'sales_history'):
                for record in entity.sales_history:
                    total += record.quantity
            entity_sales[entity.id] = total
        
        # Find entity with max sales
        if entity_sales:
            top_entity_id = max(entity_sales.keys(), key=lambda k: entity_sales[k])
            
            # Select it
            if self.current_mode == "12nc":
                self.selected_entities_12nc.add(top_entity_id)
            else:
                self.selected_entities_room.add(top_entity_id)
    
    def _get_current_entities(self):
        """Get list of entities for current mode"""
        if not hasattr(self.app_controller, 'current_data') or not self.app_controller.current_data:
            return []
        
        if self.current_mode == "12nc":
            nc12s_dict = self.app_controller.current_data.get('nc12s_dict', {})
            return list(nc12s_dict.values())
        else:
            rooms_dict = self.app_controller.current_data.get('rooms_dict', {})
            return list(rooms_dict.values())
    
    def _get_selected_entities(self) -> Set[str]:
        """Get selected entity IDs for current mode"""
        if self.current_mode == "12nc":
            return self.selected_entities_12nc
        else:
            return self.selected_entities_room
    
    def _set_selected_entities(self, entity_ids: Set[str]):
        """Set selected entity IDs for current mode"""
        if self.current_mode == "12nc":
            self.selected_entities_12nc = entity_ids
        else:
            self.selected_entities_room = entity_ids
    
    # ============================================================================
    # UI CREATION
    # ============================================================================
    
    def _create_header(self):
        """Create header with centered title and prominent mode toggle"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 20))
        header_frame.grid_columnconfigure(0, weight=1)  # Center the title
        
        # Centered Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Bulk Performance Analysis",
            font=self._get_font(size=self.FONT_SIZES["header"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        title_label.grid(row=0, column=0)
        
        # Mode toggle frame on right
        mode_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="e")
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Analysis Mode:",
            font=self._get_font(size=self.FONT_SIZES["body"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        mode_label.pack(side="left", padx=(0, 10))
        
        # More prominent mode toggle with larger size and icons
        self.mode_toggle = ctk.CTkSegmentedButton(
            mode_frame,
            values=["📦 12NC Mode", "🏢 Room Mode"],
            command=self._on_mode_change,
            fg_color=self.COLORS["bg_light"],
            selected_color=self.COLORS["accent_teal"],
            selected_hover_color=self.COLORS["accent_teal_hover"],
            unselected_color=self.COLORS["bg_white"],
            font=self._get_font(size=16, weight="bold"),
            height=48,
            border_width=2
        )
        self.mode_toggle.set("📦 12NC Mode")
        self.mode_toggle.pack(side="left")
    
    def _create_entity_list_section(self):
        """Create entity selection list with controls at top"""
        # Main container
        list_container = ctk.CTkFrame(
            self,
            fg_color=self.COLORS["bg_white"],
            corner_radius=12,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        list_container.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        
        # Controls bar - compressed to single line
        controls_frame = ctk.CTkFrame(list_container, fg_color=self.COLORS["bg_light"], corner_radius=8)
        controls_frame.pack(fill="x", padx=15, pady=10)
        
        # Search box
        search_label = ctk.CTkLabel(
            controls_frame,
            text="Search:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        search_label.pack(side="left", padx=(10, 5))
        
        self.search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Search by ID...",
            width=280,
            height=32,
            font=self._get_font(size=self.FONT_SIZES["small"]),
            fg_color=self.COLORS["bg_white"],
            border_color=self.COLORS["border"]
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        
        # Sort dropdown
        sort_label = ctk.CTkLabel(
            controls_frame,
            text="Sort:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        sort_label.pack(side="left", padx=(0, 5))
        
        self.sort_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=["ID (A-Z)", "ID (Z-A)", "Sales (High to Low)", "Sales (Low to High)"],
            command=self._on_sort_change,
            width=160,
            height=32,
            fg_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color=self.COLORS["accent_teal_hover"],
            font=self._get_font(size=self.FONT_SIZES["xsmall"])
        )
        self.sort_dropdown.set(self.sort_by)
        self.sort_dropdown.pack(side="left", padx=(0, 15))
        
        # Select All / Deselect All buttons - compressed
        self.select_all_btn = ctk.CTkButton(
            controls_frame,
            text="Select All",
            command=self._select_all,
            width=90,
            height=32,
            fg_color=self.COLORS["accent_dark"],
            hover_color=self.COLORS["accent_hover"],
            font=self._get_font(size=self.FONT_SIZES["xsmall"], weight="bold")
        )
        self.select_all_btn.pack(side="left", padx=(0, 5))
        
        self.deselect_all_btn = ctk.CTkButton(
            controls_frame,
            text="Deselect All",
            command=self._deselect_all,
            width=90,
            height=32,
            fg_color=self.COLORS["text_light"],
            hover_color=self.COLORS["text_muted"],
            font=self._get_font(size=self.FONT_SIZES["xsmall"], weight="bold")
        )
        self.deselect_all_btn.pack(side="left", padx=(0, 10))
        
        # Scrollable entity list
        list_scroll_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color=self.COLORS["bg_white"],
            height=250,  # Fixed height for entity list
            corner_radius=0
        )
        list_scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.entity_list_frame = list_scroll_frame
    
    def _create_chart_section(self):
        """Create chart area with reorganized layout: controls → chart → summary + exports"""
        chart_container = ctk.CTkFrame(
            self,
            fg_color=self.COLORS["bg_white"],
            corner_radius=12,
            border_width=1,
            border_color=self.COLORS["border"]
        )
        chart_container.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 30))
        
        # Configure grid - reorganized order
        chart_container.grid_rowconfigure(1, weight=1)  # Chart expands
        chart_container.grid_columnconfigure(0, weight=1)
        
        # Row 0: Chart controls (compressed to single line) - initially hidden
        self.controls_frame = ctk.CTkFrame(
            chart_container,
            fg_color=self.COLORS["bg_light"],
            corner_radius=8
        )
        # Don't grid it yet - will show when entities are selected
        
        self._build_chart_controls(self.controls_frame)
        
        # Row 1: Chart area
        chart_frame = ctk.CTkFrame(
            chart_container,
            fg_color=self.COLORS["bg_white"],
            corner_radius=0
        )
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        
        self._build_chart(chart_frame)
        
        # Row 2: Summary statistics + Export buttons - initially hidden
        self.bottom_frame = ctk.CTkFrame(
            chart_container,
            fg_color=self.COLORS["bg_light"],
            corner_radius=8
        )
        # Don't grid it yet - will show when entities are selected
        
        # Left side: Summary stats
        stats_container = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        stats_container.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        self._build_stats_bar(stats_container)
        
        # Right side: Export buttons adjacent to chart
        export_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        export_frame.pack(side="right", padx=10, pady=10)
        
        # Excel Export button
        self.export_excel_btn = ctk.CTkButton(
            export_frame,
            text="📊 Export Excel",
            command=self._export_excel,
            width=130,
            height=35,
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold")
        )
        self.export_excel_btn.pack(side="left", padx=(0, 8))
        
        # PDF Export button
        self.export_pdf_btn = ctk.CTkButton(
            export_frame,
            text="📑 Export PDF",
            command=self._export_pdf,
            width=130,
            height=35,
            fg_color="#f59e0b",
            hover_color="#d97706",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold")
        )
        self.export_pdf_btn.pack(side="left")
    
    def _build_chart_controls(self, parent):
        """Build chart control widgets - compressed to single line"""
        # Outer frame for centering
        outer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        outer_frame.pack(fill="x", padx=15, pady=8)
        
        # Inner frame with all controls - centered
        controls_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        controls_frame.pack(anchor="center")
        
        # 1. Granularity dropdown
        granularity_label = ctk.CTkLabel(
            controls_frame,
            text="Granularity:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        granularity_label.pack(side="left", padx=(0, 5))
        
        self.granularity_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=["Months", "Quarters", "Years"],
            command=self._on_granularity_change,
            width=110,
            height=32,
            fg_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color="#1C7A7A",
            font=self._get_font(size=self.FONT_SIZES["xsmall"])
        )
        self.granularity_dropdown.set(self.granularity)
        self.granularity_dropdown.pack(side="left", padx=(0, 20))
        
        # 2. Time Range dropdowns
        time_range_label = ctk.CTkLabel(
            controls_frame,
            text="Time Range:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        time_range_label.pack(side="left", padx=(0, 5))
        
        # From dropdown
        from_label = ctk.CTkLabel(
            controls_frame,
            text="From:",
            font=self._get_font(size=self.FONT_SIZES["xsmall"]),
            text_color=self.COLORS["text_muted"]
        )
        from_label.pack(side="left", padx=(0, 3))
        
        all_periods = self._get_all_period_labels()
        self.range_dropdown_start = ctk.CTkOptionMenu(
            controls_frame,
            values=all_periods if all_periods else ["1"],
            command=lambda _: self._on_range_change(),
            width=90,
            height=32,
            fg_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color="#1C7A7A",
            font=self._get_font(size=self.FONT_SIZES["xsmall"])
        )
        self.range_dropdown_start.set(all_periods[0] if all_periods else "1")
        self.range_dropdown_start.pack(side="left", padx=(0, 10))
        
        # To dropdown
        to_label = ctk.CTkLabel(
            controls_frame,
            text="To:",
            font=self._get_font(size=self.FONT_SIZES["xsmall"]),
            text_color=self.COLORS["text_muted"]
        )
        to_label.pack(side="left", padx=(0, 3))
        
        max_periods = self._get_max_periods()
        self.range_dropdown_end = ctk.CTkOptionMenu(
            controls_frame,
            values=all_periods if all_periods else ["1"],
            command=lambda _: self._on_range_change(),
            width=90,
            height=32,
            fg_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color="#1C7A7A",
            font=self._get_font(size=self.FONT_SIZES["xsmall"])
        )
        end_idx = max_periods - 1 if all_periods else 0
        self.range_dropdown_end.set(all_periods[end_idx] if all_periods and end_idx < len(all_periods) else "1")
        self.range_dropdown_end.pack(side="left", padx=(0, 20))
        
        # 3. Year checkboxes
        years_label = ctk.CTkLabel(
            controls_frame,
            text="Years:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        years_label.pack(side="left", padx=(0, 5))
        
        self.year_checkboxes_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        self.year_checkboxes_frame.pack(side="left")
        
        self._rebuild_year_checkboxes()
    
    def _rebuild_year_checkboxes(self):
        """Rebuild year checkboxes based on available data"""
        # Clear existing only if frame exists
        if self.year_checkboxes_frame:
            for widget in self.year_checkboxes_frame.winfo_children():
                widget.destroy()
        
        available_years = self._get_available_years()
        self.year_checkboxes = {}
        
        for year in available_years:
            color = self.YEAR_COLORS.get(year, "#666666")
            
            checkbox = ctk.CTkCheckBox(
                self.year_checkboxes_frame,
                text=str(year),
                command=lambda y=year: self._on_year_toggle(y),
                font=self._get_font(size=self.FONT_SIZES["xsmall"]),
                fg_color=color,
                hover_color=color,
                border_color=color,
                width=65
            )
            
            if year in self.selected_years:
                checkbox.select()
                
            checkbox.pack(side="left", padx=(0, 8))
            self.year_checkboxes[year] = checkbox
    
    def _build_stats_bar(self, parent):
        """Build summary statistics bar with Summary prefix"""
        stats_container = ctk.CTkFrame(parent, fg_color="transparent")
        stats_container.pack(fill="x", padx=5)
        
        # Summary label prefix
        summary_prefix = ctk.CTkLabel(
            stats_container,
            text="Summary:",
            font=self._get_font(size=self.FONT_SIZES["body"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        summary_prefix.pack(side="left", padx=(5, 15))
        
        # Count label (left)
        self.count_label = ctk.CTkLabel(
            stats_container,
            text="Entities: 0",
            font=self._get_font(size=self.FONT_SIZES["body"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        self.count_label.pack(side="left", padx=(0, 8))
        
        # Separator
        sep1 = ctk.CTkLabel(stats_container, text="|", text_color=self.COLORS["border"])
        sep1.pack(side="left", padx=5)
        
        # Total label (center-left)
        self.sum_label = ctk.CTkLabel(
            stats_container,
            text="Total: 0",
            font=self._get_font(size=self.FONT_SIZES["body"], weight="bold"),
            text_color=self.COLORS["accent_teal"]
        )
        self.sum_label.pack(side="left", padx=(0, 8))
        
        # Separator
        sep2 = ctk.CTkLabel(stats_container, text="|", text_color=self.COLORS["border"])
        sep2.pack(side="left", padx=5)
        
        # Average label (center-right)
        self.avg_label = ctk.CTkLabel(
            stats_container,
            text="Average: 0",
            font=self._get_font(size=self.FONT_SIZES["body"], weight="bold"),
            text_color=self.COLORS["accent_dark"]
        )
        self.avg_label.pack(side="left", padx=0)
    
    def _build_chart(self, parent):
        """Build matplotlib chart"""
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 6), dpi=100, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    # ============================================================================
    # DATA & CHART METHODS
    # ============================================================================
    
    def _get_available_years(self) -> List[int]:
        """Get list of years from selected entities"""
        years = set()
        
        selected_ids = self._get_selected_entities()
        entities = self._get_current_entities()
        
        for entity in entities:
            if entity.id in selected_ids and hasattr(entity, 'sales_history'):
                for record in entity.sales_history:
                    years.add(record.date.year)
        
        sorted_years = sorted(years, reverse=True)
        return sorted_years[:4]  # Up to 4 most recent years
    
    def _get_max_periods(self) -> int:
        """Get maximum number of periods based on granularity"""
        return GRANULARITY_PERIODS.get(self.granularity, 12)
    
    def _get_all_period_labels(self) -> List[str]:
        """Get all possible period labels for current granularity"""
        available_years = self._get_available_years() if self.granularity == "Years" else None
        return get_all_period_labels(self.granularity, available_years)
    
    def _aggregate_bulk_sales_data(self) -> Dict[int, Dict[str, int]]:
        """Aggregate sales data from all selected entities with robustness checks
        
        Returns:
            Dictionary: {year: {period_label: total_quantity}}
        """
        selected_ids = self._get_selected_entities()
        if not selected_ids:
            return {}
        
        entities = self._get_current_entities()
        if not entities:
            return {}
        
        analyzer_granularity = self.granularity_map.get(self.granularity, "monthly")
        
        # Aggregate data across all selected entities
        aggregated_data = defaultdict(lambda: defaultdict(int))
        
        for entity in entities:
            if entity.id not in selected_ids:
                continue
            
            # Robustness check: verify entity has sales history
            if not hasattr(entity, 'sales_history') or not entity.sales_history:
                continue
            
            try:
                # Wrap entity in G_entity for analyzer
                entity_type = "12NC" if self.current_mode == "12nc" else "room"
                g_entity_obj = G_entity(g_entity=entity, entity_type=entity_type)
                
                # Analyze performance
                performance_data: PerformanceData = self.analyzer.analyze(
                    analyzed_obj=g_entity_obj,
                    lookback_years=4,
                    granularity=analyzer_granularity
                )
                
                # Robustness check: verify periods exist
                if not hasattr(performance_data, 'periods') or not performance_data.periods:
                    continue
                
                # Add to aggregated data - only for selected years
                for period in performance_data.periods:
                    year = extract_year_from_period(period.label, analyzer_granularity)
                    if year is None or year not in self.selected_years:
                        continue
                    
                    ui_label = convert_period_label_to_ui(period.label, analyzer_granularity)
                    aggregated_data[year][ui_label] += period.quantity
                    
            except Exception as e:
                print(f"Error analyzing entity {entity.id}: {e}")
                continue
        
        return dict(aggregated_data)
    
    def _update_chart(self):
        """Update the aggregated bar chart"""
        if not self.ax or not self.canvas or not self.figure:
            return
        
        # Clear previous chart
        self.ax.clear()  # type: ignore
        
        # Check if any entities are selected
        selected_ids = self._get_selected_entities()
        if not selected_ids:
            # Hide controls and bottom frame
            if hasattr(self, 'controls_frame'):
                self.controls_frame.grid_remove()
            if hasattr(self, 'bottom_frame'):
                self.bottom_frame.grid_remove()
            
            # Show blank state message
            if self.ax is not None:
                self.ax.text(0.5, 0.5, 'Select entities to analyze',  # type: ignore
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform=self.ax.transAxes,
                            fontsize=16, color='#666666', style='italic')
            if self.canvas:
                self.canvas.draw()
            self._update_stats(0, 0, 0)
            return
        
        # Show controls and bottom frame when entities are selected
        if hasattr(self, 'controls_frame'):
            self.controls_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        if hasattr(self, 'bottom_frame'):
            self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Get aggregated data
        data = self._aggregate_bulk_sales_data()
        
        # Get all period labels
        all_periods = self._get_all_period_labels()
        
        # Apply time range filter
        start_idx = int(self.time_range[0])
        end_idx = int(self.time_range[1])
        filtered_periods = all_periods[start_idx:end_idx + 1]
        
        if not filtered_periods or not data:
            # Type assertion for matplotlib axes
            if self.ax is not None:
                self.ax.text(0.5, 0.5, 'No data to display\nSelect entities to analyze',  # type: ignore
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform=self.ax.transAxes,
                            fontsize=14, color='#666666')
            if self.canvas:
                self.canvas.draw()
            self._update_stats(0, 0, 0)
            return
        
        # Prepare data for plotting
        x_positions = list(range(len(filtered_periods)))
        
        # For yearly granularity, show single bars
        if self.granularity == "Years":
            values = []
            colors = []
            for period in filtered_periods:
                try:
                    year = int(period)
                    if year in data and period in data[year]:
                        values.append(data[year][period])
                        colors.append(self.YEAR_COLORS.get(year, "#666666"))
                    else:
                        values.append(0)
                        colors.append("#CCCCCC")
                except ValueError:
                    values.append(0)
                    colors.append("#CCCCCC")
            
            bars = self.ax.bar(  # type: ignore
                x_positions,
                values,
                width=0.6,
                color=colors,
                alpha=0.9,
                edgecolor='white',
                linewidth=1
            )
            
            add_bar_value_labels(self.ax, bars, values)
        else:
            # For monthly/quarterly: group bars by year
            bar_width = 0.8 / max(len(self.selected_years), 1)
            
            for i, year in enumerate(sorted(self.selected_years)):
                if year not in data:
                    continue
                
                year_data = data[year]
                values = [year_data.get(period, 0) for period in filtered_periods]
                
                offset = (i - len(self.selected_years) / 2 + 0.5) * bar_width
                x_positions_offset = [x + offset for x in x_positions]
                
                color = self.YEAR_COLORS.get(year, "#666666")
                bars = self.ax.bar(  # type: ignore
                    x_positions_offset,
                    values,
                    width=bar_width,
                    label=str(year),
                    color=color,
                    alpha=0.9,
                    edgecolor='white',
                    linewidth=1
                )
                
                add_bar_value_labels(self.ax, bars, values)
        
        # Customize chart
        mode_text = "12NC Components" if self.current_mode == "12nc" else "Rooms"
        self.ax.set_xlabel('Time Period', fontsize=11, fontweight='bold', color='#333333')  # type: ignore
        self.ax.set_ylabel('Total Sales Quantity', fontsize=11, fontweight='bold', color='#333333')  # type: ignore
        self.ax.set_title(f'Bulk Analysis - {mode_text} ({self.granularity})',   # type: ignore
                         fontsize=13, fontweight='bold', color='#333333', pad=15)
        
        self.ax.set_xticks(x_positions)  # type: ignore
        self.ax.set_xticklabels(filtered_periods, rotation=45, ha='right')  # type: ignore
        
        self.ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.5)  # type: ignore
        self.ax.set_axisbelow(True)  # type: ignore
        
        if self.selected_years and self.granularity != "Years":
            self.ax.legend(loc='upper right', framealpha=0.9, edgecolor='#CCCCCC')  # type: ignore
        
        # Calculate statistics
        total_sum = 0
        for year in self.selected_years:
            if year in data:
                for period in filtered_periods:
                    if period in data[year]:
                        total_sum += data[year][period]
        
        num_entities = len(self._get_selected_entities())
        avg_per_entity = total_sum / num_entities if num_entities > 0 else 0
        
        self._update_stats(total_sum, avg_per_entity, num_entities)
        
        if self.figure:
            self.figure.tight_layout()
        
        if self.canvas:
            self.canvas.draw()
    
    def _update_stats(self, total, average, count):
        """Update summary statistics labels"""
        if self.sum_label:
            self.sum_label.configure(text=f"Total: {int(total)}")
        if self.avg_label:
            self.avg_label.configure(text=f"Average: {int(average)}")
        if self.count_label:
            self.count_label.configure(text=f"Entities: {count}")
    
    # ============================================================================
    # ENTITY LIST METHODS
    # ============================================================================
    
    def _refresh_entity_list(self):
        """Refresh the entity list based on current filters and sort"""
        if not self.entity_list_frame:
            return
        
        # Clear existing
        for widget in self.entity_list_frame.winfo_children():
            widget.destroy()
        self.entity_checkboxes = {}
        
        # Get entities
        entities = self._get_current_entities()
        if not entities:
            no_data = ctk.CTkLabel(
                self.entity_list_frame,
                text="No data loaded. Please load CBOM file from Welcome screen.",
                font=self._get_font(size=self.FONT_SIZES["body"]),
                text_color=self.COLORS["text_light"]
            )
            no_data.pack(pady=30)
            return
        
        # Filter by search (ID only)
        filtered_entities = []
        search_lower = self.search_text.lower()
        for entity in entities:
            if search_lower:
                if search_lower not in entity.id.lower():
                    continue
            filtered_entities.append(entity)
        
        # Calculate total sales for sorting - MATCHED TO CHART CALCULATION
        # Use same logic as _aggregate_bulk_sales_data to ensure consistency
        entity_sales = {}
        analyzer_granularity = self.granularity_map.get(self.granularity, "monthly")
        
        for entity in filtered_entities:
            total = 0
            if hasattr(entity, 'sales_history') and entity.sales_history:
                try:
                    # Wrap entity for analyzer
                    entity_type = "12NC" if self.current_mode == "12nc" else "room"
                    g_entity_obj = G_entity(g_entity=entity, entity_type=entity_type)
                    
                    # Analyze performance
                    performance_data: PerformanceData = self.analyzer.analyze(
                        analyzed_obj=g_entity_obj,
                        lookback_years=4,
                        granularity=analyzer_granularity
                    )
                    
                    # Sum up quantities for selected years only
                    for period in performance_data.periods:
                        year = extract_year_from_period(period.label, analyzer_granularity)
                        if year and year in self.selected_years:
                            total += period.quantity
                except Exception as e:
                    # Fallback to raw sales history
                    for record in entity.sales_history:
                        if record.date.year in self.selected_years:
                            total += record.quantity
            
            entity_sales[entity.id] = total
        
        # Sort
        if self.sort_by == "ID (A-Z)":
            filtered_entities.sort(key=lambda e: e.id)
        elif self.sort_by == "ID (Z-A)":
            filtered_entities.sort(key=lambda e: e.id, reverse=True)
        elif self.sort_by == "Sales (High to Low)":
            filtered_entities.sort(key=lambda e: entity_sales.get(e.id, 0), reverse=True)
        elif self.sort_by == "Sales (Low to High)":
            filtered_entities.sort(key=lambda e: entity_sales.get(e.id, 0))
        
        # Display entities
        selected_ids = self._get_selected_entities()
        
        for entity in filtered_entities:
            entity_frame = ctk.CTkFrame(
                self.entity_list_frame,
                fg_color=self.COLORS["bg_light"],
                corner_radius=6,
                height=50
            )
            entity_frame.pack(fill="x", pady=3, padx=5)
            entity_frame.pack_propagate(False)
            
            # Checkbox
            checkbox = ctk.CTkCheckBox(
                entity_frame,
                text="",
                command=lambda eid=entity.id: self._on_entity_toggle(eid),
                fg_color=self.COLORS["accent_teal"],
                hover_color=self.COLORS["accent_teal_hover"],
                width=30
            )
            checkbox.pack(side="left", padx=(10, 5))
            
            if entity.id in selected_ids:
                checkbox.select()
            
            self.entity_checkboxes[entity.id] = checkbox
            
            # ID
            id_label = ctk.CTkLabel(
                entity_frame,
                text=entity.id,
                font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
                text_color=self.COLORS["text_dark"],
                width=150,
                anchor="w"
            )
            id_label.pack(side="left", padx=(0, 10))
            
            # Description
            desc_label = ctk.CTkLabel(
                entity_frame,
                text=entity.description,
                font=self._get_font(size=self.FONT_SIZES["small"]),
                text_color=self.COLORS["text_muted"],
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            # Sales count - uses calculated value for consistency
            sales_count = entity_sales.get(entity.id, 0)
            sales_label = ctk.CTkLabel(
                entity_frame,
                text=f"Sales: {int(sales_count)}",
                font=self._get_font(size=self.FONT_SIZES["xsmall"], weight="bold"),
                text_color=self.COLORS["accent_teal"],
                width=100,
                anchor="e"
            )
            sales_label.pack(side="right", padx=10)
    
    # ============================================================================
    # EVENT HANDLERS
    # ============================================================================
    
    def _on_mode_change(self, value):
        """Handle mode toggle change"""
        self.current_mode = "12nc" if "12NC" in value else "room"
        
        # Reset search
        self.search_text = ""
        if self.search_entry:
            self.search_entry.delete(0, tk.END)
        
        # Refresh UI
        self._initialize_available_years()
        self._rebuild_year_checkboxes()
        self._refresh_entity_list()
        self._update_chart()
    
    def _on_search_change(self, event):
        """Handle search text change"""
        self.search_text = self.search_entry.get()
        self._refresh_entity_list()
    
    def _on_sort_change(self, value):
        """Handle sort dropdown change"""
        self.sort_by = value
        self._refresh_entity_list()
    
    def _on_entity_toggle(self, entity_id):
        """Handle entity checkbox toggle"""
        selected = self._get_selected_entities()
        
        if entity_id in selected:
            selected.remove(entity_id)
        else:
            selected.add(entity_id)
        
        self._set_selected_entities(selected)
        
        # Update years and chart immediately
        self._initialize_available_years()
        self._rebuild_year_checkboxes()
        self._update_chart()
    
    def _select_all(self):
        """Select all visible entities"""
        entities = self._get_current_entities()
        search_lower = self.search_text.lower()
        
        selected = self._get_selected_entities()
        
        for entity in entities:
            # Apply search filter
            if search_lower:
                if search_lower not in entity.id.lower() and search_lower not in entity.description.lower():
                    continue
            selected.add(entity.id)
        
        self._set_selected_entities(selected)
        self._refresh_entity_list()
        self._initialize_available_years()
        self._rebuild_year_checkboxes()
        self._update_chart()
    
    def _deselect_all(self):
        """Deselect all entities"""
        self._set_selected_entities(set())
        self._refresh_entity_list()
        self._initialize_available_years()
        self._rebuild_year_checkboxes()
        self._update_chart()
    
    def _on_granularity_change(self, new_granularity: str):
        """Handle granularity change"""
        self.granularity = new_granularity
        
        max_periods = self._get_max_periods()
        self.time_range = (0, max_periods - 1)
        
        if self.range_dropdown_start and self.range_dropdown_end:
            all_periods = self._get_all_period_labels()
            
            self.range_dropdown_start.configure(values=all_periods)
            self.range_dropdown_end.configure(values=all_periods)
            
            self.range_dropdown_start.set(all_periods[0] if all_periods else "1")
            self.range_dropdown_end.set(all_periods[max_periods - 1] if all_periods and max_periods - 1 < len(all_periods) else all_periods[-1] if all_periods else "1")
        
        self._update_chart()
    
    def _on_year_toggle(self, year: int):
        """Handle year checkbox toggle"""
        if year in self.selected_years:
            self.selected_years.remove(year)
        else:
            self.selected_years.add(year)
        
        self._update_chart()
    
    def _on_range_change(self):
        """Handle time range change"""
        if not self.range_dropdown_start or not self.range_dropdown_end:
            return
        
        all_periods = self._get_all_period_labels()
        if not all_periods:
            return
        
        start_value = self.range_dropdown_start.get()
        end_value = self.range_dropdown_end.get()
        
        try:
            start = all_periods.index(start_value)
            end = all_periods.index(end_value)
        except ValueError:
            return
        
        if start > end:
            start, end = end, start
            self.range_dropdown_start.set(all_periods[start])
            self.range_dropdown_end.set(all_periods[end])
        
        self.time_range = (start, end)
        self._update_chart()
    
    def _get_export_folder(self) -> Path:
        """Get export folder path based on source files location"""
        # Try to get CBOM path from loaded files
        if hasattr(self.app_controller, 'loaded_files') and self.app_controller.loaded_files:
            cbom_path = self.app_controller.loaded_files.get('cbom')
            if cbom_path:
                return get_export_folder(cbom_path)
        
        # Fallback to current working directory
        return get_export_folder()
    
    def _export_excel(self):
        """Export bulk analysis data to Excel in predetermined folder with entity IDs"""
        selected_ids = self._get_selected_entities()
        if not selected_ids:
            messagebox.showwarning("No Data", "Please select entities to export.")
            return
        
        # Get aggregated data
        data = self._aggregate_bulk_sales_data()
        all_periods = self._get_all_period_labels()
        
        # Get export folder
        export_folder = self._get_export_folder()
        
        # Export using shared utility with entity IDs
        mode_text = "12NC" if self.current_mode == "12nc" else "Room"
        filename_prefix = f"bulk_analysis_{mode_text}"
        
        export_data_to_excel(
            data=data,
            periods=all_periods,
            years=list(self.selected_years),
            export_folder=export_folder,
            filename_prefix=filename_prefix,
            entity_count=len(selected_ids),
            mode=self.current_mode,
            granularity=self.granularity,
            selected_entity_ids=list(selected_ids)
        )
    
    def _export_pdf(self):
        """Export screenshot of entire bulk view screen to PDF"""
        selected_ids = self._get_selected_entities()
        if not selected_ids:
            messagebox.showwarning("No Data", "Please select entities to export.")
            return
        
        # Get export folder
        export_folder = self._get_export_folder()
        
        # Export screenshot of the entire screen
        mode_text = "12NC" if self.current_mode == "12nc" else "Room"
        filename_prefix = f"bulk_analysis_{mode_text}_screenshot"
        title = f"Bulk Analysis - {mode_text} ({self.granularity})"
        
        export_screen_to_pdf(
            widget=self,
            export_folder=export_folder,
            filename_prefix=filename_prefix,
            title=title
        )
