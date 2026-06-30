#!/usr/bin/env python3
import argparse
import csv
import re
from html.parser import HTMLParser
from pathlib import Path

class MorganStanleyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tr = False
        self.in_cell = False
        self.current_row = []
        self.current_cell = []
        self.rows = []
        self.cell_attrs = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag in ('td', 'th') and self.in_tr:
            self.in_cell = True
            self.current_cell = []
            self.cell_attrs = attrs_dict

    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr' and self.in_table:
            self.in_tr = False
            if self.current_row:
                self.rows.append(self.current_row)
        elif tag in ('td', 'th') and self.in_tr:
            self.in_cell = False
            cell_text = "".join(self.current_cell).strip()
            # Clean up whitespace
            cell_text = re.sub(r'\s+', ' ', cell_text)
            
            colspan = int(self.cell_attrs.get('colspan', 1))
            self.current_row.append((cell_text, colspan))

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

def parse_html(html_content):
    parser = MorganStanleyHTMLParser()
    parser.feed(html_content)
    
    csv_rows = []
    started = False
    
    for row in parser.rows:
        row_texts = [cell[0] for cell in row]
        
        if not started:
            if 'Entry Date' in row_texts and 'Activity' in row_texts:
                started = True
                csv_rows.append(['Activity', '', '', '', '', '', '', ''])
                # Ensure we use the exact header names
                csv_rows.append([
                    'Entry Date', 'Activity', 'Type of Money', 'Cash', 
                    'Number of Shares', 'Share Price', 'Book Value', 'Market Value'
                ])
            continue
        
        # If we have started, process rows
        if len(row) == 1 and row[0][1] > 1:
            text = row[0][0]
            if text.startswith('Fund:'):
                csv_rows.append([text, '', '', '', '', '', '', ''])
        elif len(row) > 0:
            # It's a data row. Reconstruct based on colspans.
            data_row = []
            for text, colspan in row:
                data_row.append(text)
                for _ in range(colspan - 1):
                    data_row.append('')
            
            # Pad or truncate to 8 columns
            while len(data_row) < 8:
                data_row.append('')
            csv_rows.append(data_row[:8])
                
    return csv_rows

def main():
    parser = argparse.ArgumentParser(description="Convert Morgan Stanley Account Summary HTML to CSV")
    parser.add_argument("--html", required=True, help="Path to the HTML file")
    parser.add_argument("--output", default="account-summary.csv", help="Path to the output CSV file")
    args = parser.parse_args()
    
    html_path = Path(args.html)
    if not html_path.exists():
        print(f"Error: File {html_path} not found.")
        return
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    csv_rows = parse_html(content)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
        
    print(f"Successfully converted {html_path} to {args.output}")

if __name__ == "__main__":
    main()
