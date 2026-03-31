"""Performance Panel - Shows sales history and performance metrics"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import calendar

from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.models.performance import PerformanceData, TimePeriod
from src.models.mapping import G_entity


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
        
        # Initialize the performance analyzer
        self.analyzer = PerformanceAnalyzer()
        
        # Chart state
        self.entity_obj = None
        self.mode = None
        self.granularity = "Months"  # UI granularity
        self.selected_years = set()  # Years to display
        self.time_range = (0, 11)  # Default: full range (12 periods for months)
        
        # Map UI granularities to analyzer granularities
        self.granularity_map = {
            "Months": "monthly",
            "Quarters": "quarterly",
            "Years": "yearly"
        }
        
        # Year colors
        self.year_colors = {
            2026: "#FF8C42",  # Orange
            2025: "#4A90E2",  # Blue
            2024: "#50C878",  # Green
            2023: "#9E9E9E",  # Grey
        }
        
        # UI components
        self.canvas = None
        self.figure = None
        self.ax = None
        self.year_checkboxes = {}
        self.range_slider_start = None
        self.range_slider_end = None
        self.granularity_dropdown = None
    
    def update(self, entity_obj, mode):
        """Update panel with sales performance data
        
        Args:
            entity_obj: Room or TwelveNC object
            mode: Current mode ('room' or '12nc')
        """
        # Store entity and mode
        self.entity_obj = entity_obj
        self.mode = mode
        
        # Find the content frame in the panel
        self.content_frame = self._find_content_frame()
        
        if not self.content_frame:
            return
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Check if there are sales records
        if not entity_obj.sales_history:
            no_data_label = ctk.CTkLabel(
                self.content_frame,
                text="No sales data available",
                font=self._get_font(size=self.FONT_SIZES["body"]),
                text_color=self.COLORS["text_light"]
            )
            no_data_label.pack(pady=20)
            return
        
        # Initialize selected years (default: all available years)
        available_years = self._get_available_years()
        self.selected_years = set(available_years)
        
        # Build the UI
        self._build_ui()
        
        # Initial chart render
        self._update_chart()
    
    def _find_content_frame(self):
        """Find the content frame within the panel widget
        Args:None 
        Does: Searches for a CTkFrame in the panel's children that is located at grid row=1, which is where we expect the content to be.
        Returns: The content frame widget if found, otherwise None.
        """
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
    
    def _get_available_years(self) -> List[int]:
        """Get list of years present in sales data, limited to last 3 years from most recent
        Args: None
        Does: Extracts the years from the sales history of the current entity object.
        Returns: A list of up to 3 most recent years.
        """
        if not self.entity_obj or not self.entity_obj.sales_history:
            return []
        
        years = set(record.date.year for record in self.entity_obj.sales_history)
        sorted_years = sorted(years, reverse=True)
        # Return up to 3 most recent years
        return sorted_years[:3]
    
    def _build_ui(self):
        """Build the complete UI with controls and chart
        Args: None
        Does: Creates the main container, controls panel, and chart area within the content frame.
        Returns: None
        """
        # Main container
        main_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Controls panel at the top
        controls_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.COLORS["bg_light"],
            corner_radius=8
        )
        controls_frame.pack(fill="x", pady=(0, 15))
        
        self._build_controls(controls_frame)
        
        # Chart area
        chart_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.COLORS["bg_white"],
            corner_radius=8
        )
        chart_frame.pack(fill="both", expand=True)
        
        self._build_chart(chart_frame)
    
    def _build_controls(self, parent):
        """Build control widgets (granularity dropdown, year checkboxes, range slider)
        Args:
            parent: Parent frame for controls
        Does: Creates the controls for adjusting the chart, including a dropdown for granularity,
        checkboxes for selecting years, and sliders for adjusting the time range.
        Returns: None
        """
        inner_frame = ctk.CTkFrame(parent, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=15)
        
        # Row 1: Granularity and Year filters
        row1_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        row1_frame.pack(fill="x", pady=(0, 15))
        
        # 1. Granularity dropdown
        granularity_label = ctk.CTkLabel(
            row1_frame,
            text="Granularity:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        granularity_label.pack(side="left", padx=(0, 10))
        
        self.granularity_dropdown = ctk.CTkOptionMenu(
            row1_frame,
            values=["Months", "Quarters", "Years"],
            command=self._on_granularity_change,
            width=120,
            fg_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color="#1C7A7A"
        )
        self.granularity_dropdown.set(self.granularity)
        self.granularity_dropdown.pack(side="left", padx=(0, 30))
        
        # 2. Year checkboxes
        years_label = ctk.CTkLabel(
            row1_frame,
            text="Years:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        years_label.pack(side="left", padx=(0, 10))
        
        available_years = self._get_available_years()
        for year in available_years:
            color = self.year_colors.get(year, "#666666")
            
            checkbox = ctk.CTkCheckBox(
                row1_frame,
                text=str(year),
                command=lambda y=year: self._on_year_toggle(y),
                font=self._get_font(size=self.FONT_SIZES["small"]),
                fg_color=color,
                hover_color=color,
                border_color=color
            )
            checkbox.select()  # Default: all selected
            checkbox.pack(side="left", padx=(0, 15))
            
            self.year_checkboxes[year] = checkbox
        
        # 3. Time range slider
        row2_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        row2_frame.pack(fill="x")
        
        slider_label = ctk.CTkLabel(
            row2_frame,
            text="Time Range:",
            font=self._get_font(size=self.FONT_SIZES["small"], weight="bold"),
            text_color=self.COLORS["text_dark"]
        )
        slider_label.pack(anchor="w", pady=(0, 5))
        
        # Slider container
        slider_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
        slider_container.pack(fill="x")
        slider_container.grid_columnconfigure(1, weight=1)
        
        # Start slider
        start_label = ctk.CTkLabel(
            slider_container,
            text="Start:",
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["text_muted"]
        )
        start_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        max_periods = self._get_max_periods()
        self.range_slider_start = ctk.CTkSlider(
            slider_container,
            from_=0,
            to=max_periods - 1,
            number_of_steps=max_periods - 1,
            command=self._on_range_change,
            fg_color=self.COLORS["border"],
            progress_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color="#1C7A7A"
        )
        # Default to full range
        self.range_slider_start.set(0)
        self.range_slider_start.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Get initial period label
        all_periods = self._get_all_period_labels()
        start_period_label = all_periods[0] if all_periods else "1"
        
        self.start_value_label = ctk.CTkLabel(
            slider_container,
            text=start_period_label,
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["text_dark"],
            width=50
        )
        self.start_value_label.grid(row=0, column=2)
        
        # End slider
        end_label = ctk.CTkLabel(
            slider_container,
            text="End:",
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["text_muted"]
        )
        end_label.grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="w")
        
        self.range_slider_end = ctk.CTkSlider(
            slider_container,
            from_=0,
            to=max_periods - 1,
            number_of_steps=max_periods - 1,
            command=self._on_range_change,
            fg_color=self.COLORS["border"],
            progress_color=self.COLORS["accent_teal"],
            button_color=self.COLORS["accent_teal"],
            button_hover_color="#1C7A7A"
        )
        # Default to full range
        self.range_slider_end.set(max_periods - 1)
        self.range_slider_end.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(10, 0))
        
        # Get end period label
        end_period_label = all_periods[max_periods - 1] if all_periods else str(max_periods)
        
        self.end_value_label = ctk.CTkLabel(
            slider_container,
            text=end_period_label,
            font=self._get_font(size=self.FONT_SIZES["small"]),
            text_color=self.COLORS["text_dark"],
            width=50
        )
        self.end_value_label.grid(row=1, column=2, pady=(10, 0))
    
    def _build_chart(self, parent):
        """Build matplotlib chart
        Args:
            parent: Parent frame for chart
        Does: Initializes the matplotlib figure and canvas for displaying the sales performance chart.
        Returns: None
        """
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
        
        # Connect hover event for tooltips
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
        
        # Store tooltip annotation (initially invisible)
        self.tooltip = None
    
    def _get_max_periods(self) -> int:
        """Get maximum number of periods based on granularity"""
        granularity_periods = {
            "Months": 12,
            "Quarters": 4,
            "Years": 3
        }
        return granularity_periods.get(self.granularity, 12)
    
    def _aggregate_sales_data(self) -> Dict[int, Dict[str, int]]:
        """Aggregate sales data by year and time period using PerformanceAnalyzer
        
        Args: None
        Does: Analyzes sales data for the last 3 years combined using PerformanceAnalyzer,
              then groups results by year for display.
        Returns:
            Dictionary: {year: {period_label: quantity}}
        """
        if not self.entity_obj or not self.entity_obj.sales_history:
            return {}
        
        # Get analyzer granularity from UI granularity
        analyzer_granularity = self.granularity_map.get(self.granularity, "monthly")
        
        try:
            # Analyze using PerformanceAnalyzer for the last 3 years
            performance_data: PerformanceData = self.analyzer.analyze(
                analyzed_obj=self.entity_obj,
                lookback_years=3,
                granularity=analyzer_granularity
            )
            
            # Group periods by year
            data = {}
            for period in performance_data.periods:
                # Extract year from period label
                year = self._extract_year_from_period(period.label, analyzer_granularity)
                if year is None:
                    continue
                    
                # Convert period label to UI format
                ui_label = self._convert_period_label_to_ui(period.label, analyzer_granularity)
                
                # Initialize year dict if needed
                if year not in data:
                    data[year] = {}
                
                data[year][ui_label] = period.quantity
            
            return data
            
        except Exception as e:
            print(f"Error analyzing sales data: {e}")
            return {}
    
    def _extract_year_from_period(self, period_label: str, analyzer_granularity: str) -> int | None:
        """Extract year from analyzer period label
        
        Args:
            period_label: Period label from analyzer (e.g., "03-2024", "2024-Q1", "2024")
            analyzer_granularity: The granularity used by analyzer
            
        Returns:
            Year as integer, or None if cannot be extracted
        """
        try:
            if analyzer_granularity == "monthly":
                # Format: "03-2024" -> 2024
                return int(period_label.split("-")[1])
            elif analyzer_granularity == "quarterly":
                # Format: "2024-Q1" -> 2024
                return int(period_label.split("-")[0])
            elif analyzer_granularity == "yearly":
                # Format: "2024" -> 2024
                return int(period_label)
        except (ValueError, IndexError):
            return None
        return None
    
    def _convert_period_label_to_ui(self, period_label: str, analyzer_granularity: str) -> str:
        """Convert analyzer period label to UI-friendly format
        
        Args:
            period_label: Period label from analyzer (e.g., "03-2024", "2024-Q1")
            analyzer_granularity: The granularity used by analyzer
            
        Returns:
            UI-friendly label (e.g., "Mar", "Q1", "2024")
        """
        try:
            if analyzer_granularity == "monthly":
                # Format: "03-2024" -> "Mar"
                month_num = int(period_label.split("-")[0])
                return calendar.month_abbr[month_num]
            elif analyzer_granularity == "quarterly":
                # Format: "2024-Q1" -> "Q1"
                parts = period_label.split("-")
                return parts[1] if len(parts) > 1 else period_label
            elif analyzer_granularity == "yearly":
                # Format: "2024" -> "2024"
                return period_label
        except (ValueError, IndexError):
            pass
        return period_label
    
    def _get_all_period_labels(self) -> List[str]:
        """Get all possible period labels for current granularity
        
        Returns:
            List of period labels in order
        """
        if self.granularity == "Months":
            return [calendar.month_abbr[i] for i in range(1, 13)]
        elif self.granularity == "Quarters":
            return ["Q1", "Q2", "Q3", "Q4"]
        elif self.granularity == "Years":
            available_years = self._get_available_years()
            return [str(year) for year in sorted(available_years)]
        return []
    
    def _update_chart(self):
        """Update the bar chart with current settings"""
        if not self.ax:
            return
        
        # Clear previous chart
        self.ax.clear()
        
        # Get aggregated data
        data = self._aggregate_sales_data()
        
        # Get all period labels
        all_periods = self._get_all_period_labels()
        
        # Apply time range filter
        start_idx = int(self.time_range[0])
        end_idx = int(self.time_range[1])
        filtered_periods = all_periods[start_idx:end_idx + 1]
        
        if not filtered_periods:
            self.ax.text(0.5, 0.5, 'No data to display',
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=self.ax.transAxes,
                        fontsize=14, color='#666666')
            if self.canvas:
                self.canvas.draw()
            return
        
        # Prepare data for plotting
        x_positions = list(range(len(filtered_periods)))
        bar_width = 0.8 / max(len(self.selected_years), 1)
        
        # Plot bars for each selected year
        bars_metadata = []  # Store bar metadata for tooltips
        
        for i, year in enumerate(sorted(self.selected_years)):
            if year not in data:
                continue
            
            year_data = data[year]
            values = [year_data.get(period, 0) for period in filtered_periods]
            
            # Calculate x offset for grouped bars
            offset = (i - len(self.selected_years) / 2 + 0.5) * bar_width
            x_positions_offset = [x + offset for x in x_positions]
            
            color = self.year_colors.get(year, "#666666")
            bars = self.ax.bar(
                x_positions_offset,
                values,
                width=bar_width,
                label=str(year),
                color=color,
                alpha=0.9,
                edgecolor='white',
                linewidth=1
            )
            
            # Store metadata for each bar
            for bar, period, value in zip(bars, filtered_periods, values):
                bars_metadata.append({
                    'bar': bar,
                    'year': year,
                    'period': period,
                    'value': value
                })
        
        self.bars_metadata = bars_metadata
        
        # Customize chart
        self.ax.set_xlabel('Time Period', fontsize=11, fontweight='bold', color='#333333')
        self.ax.set_ylabel('Sales Quantity', fontsize=11, fontweight='bold', color='#333333')
        self.ax.set_title(f'Sales History ({self.granularity})', 
                         fontsize=13, fontweight='bold', color='#333333', pad=15)
        
        # Set x-axis labels
        self.ax.set_xticks(x_positions)
        self.ax.set_xticklabels(filtered_periods, rotation=45, ha='right')
        
        # Customize grid
        self.ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax.set_axisbelow(True)
        
        # Legend
        if self.selected_years:
            self.ax.legend(loc='upper right', framealpha=0.9, edgecolor='#CCCCCC')
        
        # Tight layout
        if self.figure:

            self.figure.tight_layout()
        
        # Redraw canvas
        if self.canvas:
            self.canvas.draw()
    
    def _on_granularity_change(self, new_granularity: str):
        """Handle granularity dropdown change
        
        Args:
            new_granularity: New granularity value
        """
        self.granularity = new_granularity
        
        # Reset time range
        max_periods = self._get_max_periods()
        self.time_range = (0, max_periods - 1)
        
        # Update sliders
        if self.range_slider_start and self.range_slider_end:
            self.range_slider_start.configure(to=max_periods - 1, number_of_steps=max_periods - 1)
            self.range_slider_start.set(0)
            self.range_slider_end.configure(to=max_periods - 1, number_of_steps=max_periods - 1)
            self.range_slider_end.set(max_periods - 1)
            
            # Update labels with period names
            all_periods = self._get_all_period_labels()
            start_label = all_periods[0] if all_periods else "1"
            end_label = all_periods[max_periods - 1] if all_periods and len(all_periods) > max_periods - 1 else str(max_periods)
            self.start_value_label.configure(text=start_label)
            self.end_value_label.configure(text=end_label)
        
        # Update chart
        self._update_chart()
    
    def _on_year_toggle(self, year: int):
        """Handle year checkbox toggle
        
        Args:
            year: Year that was toggled
        """
        if year in self.selected_years:
            self.selected_years.remove(year)
        else:
            self.selected_years.add(year)
        
        # Update chart
        self._update_chart()
    
    def _on_range_change(self, value):
        """Handle range slider change
        
        Args:
            value: Slider value (not used, we read directly from sliders)
        """
        if not self.range_slider_start or not self.range_slider_end:
            return
            
        start = int(self.range_slider_start.get())
        end = int(self.range_slider_end.get())
        
        # Ensure start <= end
        if start > end:
            if self.time_range[0] != start:
                # Start was changed, adjust end
                self.range_slider_end.set(start)
                end = start
            else:
                # End was changed, adjust start
                self.range_slider_start.set(end)
                start = end
        
        self.time_range = (start, end)
        
        # Update labels with period names
        all_periods = self._get_all_period_labels()
        start_label = all_periods[start] if all_periods and start < len(all_periods) else str(start + 1)
        end_label = all_periods[end] if all_periods and end < len(all_periods) else str(end + 1)
        self.start_value_label.configure(text=start_label)
        self.end_value_label.configure(text=end_label)
        
        # Update chart
        self._update_chart()
    
    def _on_hover(self, event):
        """Handle mouse hover for tooltip display
        
        Args:
            event: Matplotlib mouse event
        """
        if event.inaxes != self.ax or not self.canvas:
            # Hide tooltip if mouse leaves axes
            if self.tooltip and self.canvas:
                self.tooltip.set_visible(False)
                self.canvas.draw_idle()
            return
        
        # Check if mouse is over any bar
        bar_found = False
        
        if hasattr(self, 'bars_metadata'):
            for metadata in self.bars_metadata:
                bar = metadata['bar']
                contains, _ = bar.contains(event)
                
                if contains:
                    # Show tooltip
                    bar_found = True
                    year = metadata['year']
                    period = metadata['period']
                    value = metadata['value']
                    
                    # Create or update tooltip
                    tooltip_text = f"{period} {year}\nQuantity: {value}"
                    
                    if not self.tooltip and self.ax:
                        self.tooltip = self.ax.annotate(
                            tooltip_text,
                            xy=(0, 0),
                            xytext=(10, 10),
                            textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.9, edgecolor='#666666'),
                            fontsize=9,
                            fontweight='bold'
                        )
                    else:
                        if self.tooltip:
                            self.tooltip.set_text(tooltip_text)
                            self.tooltip.set_visible(True)
                    
                    # Position tooltip at bar center
                    x = bar.get_x() + bar.get_width() / 2
                    y = bar.get_height()
                    if self.tooltip:
                      self.tooltip.xy = (x, y)
                    
                    self.canvas.draw_idle()
                    break
        
        # Hide tooltip if no bar found
        if not bar_found and self.tooltip:
            self.tooltip.set_visible(False)
            self.canvas.draw_idle()
