"""Shared export utilities for Excel and PDF"""

import csv
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional
import io

try:
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def export_to_csv(
    data: Dict[int, Dict[str, int]],
    periods: List[str],
    years: List[int],
    entity_count: int,
    mode: str,
    granularity: str,
    default_filename: Optional[str] = None
) -> bool:
    """Export bulk analysis data to CSV
    
    Args:
        data: Dictionary {year: {period: value}}
        periods: List of period labels
        years: List of selected years
        entity_count: Number of entities selected
        mode: Analysis mode ("12nc" or "room")
        granularity: Time granularity
        default_filename: Optional default filename
        
    Returns:
        True if export succeeded, False otherwise
    """
    if default_filename is None:
        default_filename = f"bulk_analysis_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile=default_filename
    )
    
    if not file_path:
        return False
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Analysis Type', f'Bulk {mode.upper()} Analysis'])
            writer.writerow(['Selected Entities', entity_count])
            writer.writerow(['Granularity', granularity])
            writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # Data table header
            header = ['Period'] + [str(year) for year in sorted(years)]
            writer.writerow(header)
            
            # Data rows
            for period in periods:
                row = [period]
                for year in sorted(years):
                    value = data.get(year, {}).get(period, 0)
                    row.append(str(int(value)))
                writer.writerow(row)
            
            writer.writerow([])
            
            # Summary
            total = sum(data.get(year, {}).get(period, 0) 
                       for year in years 
                       for period in periods)
            writer.writerow(['Total', int(total)])
            writer.writerow(['Average per Entity', int(total / entity_count) if entity_count else 0])
        
        messagebox.showinfo("Export Successful", f"Data exported to:\n{file_path}")
        return True
        
    except Exception as e:
        messagebox.showerror("Export Failed", f"Error exporting data:\n{str(e)}")
        return False


def export_chart_to_pdf(
    figure,
    default_filename: Optional[str] = None,
    title: Optional[str] = None
) -> bool:
    """Export matplotlib figure to PDF
    
    Args:
        figure: Matplotlib figure object
        default_filename: Optional default filename
        title: Optional title for the PDF
        
    Returns:
        True if export succeeded, False otherwise
    """
    if not HAS_MATPLOTLIB:
        messagebox.showerror("Export Failed", "Matplotlib is not available for PDF export")
        return False
    
    if default_filename is None:
        default_filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        initialfile=default_filename
    )
    
    if not file_path:
        return False
    
    try:
        with PdfPages(file_path) as pdf:
            # Save the figure to PDF
            pdf.savefig(figure, bbox_inches='tight')
            
            # Add metadata
            d = pdf.infodict()
            d['Title'] = title or 'Performance Chart'
            d['Author'] = 'Performance Center'
            d['Creator'] = 'Performance Center Application'
            d['CreationDate'] = datetime.now()
        
        messagebox.showinfo("Export Successful", f"Chart exported to:\n{file_path}")
        return True
        
    except Exception as e:
        messagebox.showerror("Export Failed", f"Error exporting chart:\n{str(e)}")
        return False


def export_data_to_excel(
    data: Dict[int, Dict[str, int]],
    periods: List[str],
    years: List[int],
    entity_count: int,
    mode: str,
    granularity: str,
    default_filename: Optional[str] = None
) -> bool:
    """Export data to Excel file
    
    Args:
        data: Dictionary {year: {period: value}}
        periods: List of period labels
        years: List of selected years
        entity_count: Number of entities selected
        mode: Analysis mode ("12nc" or "room")
        granularity: Time granularity
        default_filename: Optional default filename
        
    Returns:
        True if export succeeded, False otherwise
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
    except ImportError:
        messagebox.showerror(
            "Export Failed", 
            "openpyxl library is required for Excel export.\nPlease install it with: pip install openpyxl"
        )
        return False
    
    if default_filename is None:
        default_filename = f"bulk_analysis_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=default_filename
    )
    
    if not file_path:
        return False
    
    try:
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Bulk Analysis"
        
        # Styles
        header_font = Font(bold=True, size=12)
        title_font = Font(bold=True, size=14)
        header_fill = PatternFill(start_color="4A8F93", end_color="4A8F93", fill_type="solid")
        
        # Title section
        ws['A1'] = 'Analysis Type'
        ws['B1'] = f'Bulk {mode.upper()} Analysis'
        ws['A1'].font = title_font
        
        ws['A2'] = 'Selected Entities'
        ws['B2'] = entity_count
        
        ws['A3'] = 'Granularity'
        ws['B3'] = granularity
        
        ws['A4'] = 'Export Date'
        ws['B4'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Data table header (starting at row 6)
        start_row = 6
        ws.cell(start_row, 1, 'Period').font = header_font
        ws.cell(start_row, 1).fill = header_fill
        
        for col_idx, year in enumerate(sorted(years), start=2):
            cell = ws.cell(start_row, col_idx, str(year))
            cell.font = header_font
            cell.fill = header_fill
        
        # Data rows
        for row_idx, period in enumerate(periods, start=start_row + 1):
            ws.cell(row_idx, 1, period)
            for col_idx, year in enumerate(sorted(years), start=2):
                value = data.get(year, {}).get(period, 0)
                ws.cell(row_idx, col_idx, int(value))
        
        # Summary section
        summary_row = start_row + len(periods) + 2
        ws.cell(summary_row, 1, 'Total').font = header_font
        total = sum(data.get(year, {}).get(period, 0) 
                   for year in years 
                   for period in periods)
        ws.cell(summary_row, 2, int(total))
        
        ws.cell(summary_row + 1, 1, 'Average per Entity').font = header_font
        ws.cell(summary_row + 1, 2, int(total / entity_count) if entity_count else 0)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2
        
        # Save workbook
        wb.save(file_path)
        
        messagebox.showinfo("Export Successful", f"Data exported to:\n{file_path}")
        return True
        
    except Exception as e:
        messagebox.showerror("Export Failed", f"Error exporting to Excel:\n{str(e)}")
        return False
