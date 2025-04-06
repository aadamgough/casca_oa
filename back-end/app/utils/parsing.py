from datetime import datetime
from decimal import Decimal
import re

class StatementParser:
    def __init__(self, textract_response):
        self.blocks = textract_response.get('Blocks', [])

    def extract_table_data(self):
        """Extract table data from Textract response"""
        rows = []
        current_row = {}
        
        for block in self.blocks:
            if block['BlockType'] == 'CELL':
                row_index = block.get('RowIndex')
                col_index = block.get('ColumnIndex')
                
                if block.get('EntityTypes', []) == ['COLUMN_HEADER']:
                    continue
                
                if 'Text' in block:
                    text = block['Text'].strip()
                    
                    # Assuming standard bank statement format:
                    # Col 1: Date, Col 2: Description, Col 3: Amount
                    if col_index == 1:  # Date
                        current_row = {'date': text}
                    elif col_index == 2:  # Description
                        current_row['description'] = text
                    elif col_index == 3:  # Amount
                        current_row['amount'] = text
                        rows.append(current_row.copy())
        
        return self.clean_transactions(rows)

    def clean_transactions(self, raw_rows):
        """Clean and format the extracted transactions"""
        cleaned = []
        
        for row in raw_rows:
            try:
                # Clean date
                date_str = row.get('date', '')
                try:
                    # Adjust this pattern based on your date format
                    date = datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    continue

                # Clean amount
                amount_str = row.get('amount', '').replace('$', '').replace(',', '')
                try:
                    amount = Decimal(amount_str)
                except:
                    continue

                cleaned.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'description': row.get('description', '').strip(),
                    'amount': str(amount)
                })
                
            except Exception as e:
                print(f"Error cleaning row {row}: {e}")
                continue
                
        return cleaned