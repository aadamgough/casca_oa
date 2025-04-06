from datetime import datetime
from decimal import Decimal
import re
from typing import List, Dict
from ..models.transaction import Transaction

class PreprocessingService:
    def __init__(self):
        self.common_prefixes = [
            'POS', 'ACH', 'DEBIT', 'CREDIT', 'PMT', 'PAYMENT', 'TFR', 'TRANSFER',
            'WDL', 'WITHDRAWAL', 'DEP', 'DEPOSIT', 'CHK', 'CHECK'
        ]

    def clean_description(self, description: str) -> str:
        """Normalize transaction descriptions"""
        # Convert to uppercase for consistency
        desc = description.upper()
        
        # Remove common banking prefixes
        for prefix in self.common_prefixes:
            if desc.startswith(prefix):
                desc = desc.replace(prefix, '', 1).strip()
        
        # Remove multiple spaces
        desc = ' '.join(desc.split())
        
        # Remove special characters but keep spaces and alphanumeric
        desc = re.sub(r'[^A-Z0-9\s]', '', desc)
        
        return desc.strip()

    def parse_amount(self, amount_str: str) -> Decimal:
        """Convert amount string to Decimal"""
        # Remove currency symbols and commas
        clean_amount = amount_str.replace('$', '').replace(',', '')
        
        try:
            return Decimal(clean_amount)
        except:
            raise ValueError(f"Could not parse amount: {amount_str}")

    def parse_date(self, date_str: str) -> datetime:
        """Convert date string to datetime"""
        # Try common date formats
        date_formats = [
            '%m/%d/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")

    def process_textract_blocks(self, blocks: List[Dict]) -> List[Transaction]:
        """Convert Textract blocks to Transaction objects"""
        transactions = []
        current_row = {}
        
        for block in blocks:
            if block['BlockType'] == 'CELL':
                row_index = block.get('RowIndex')
                col_index = block.get('ColumnIndex')
                
                # Skip header row
                if block.get('EntityTypes', []) == ['COLUMN_HEADER']:
                    continue
                
                if 'Text' in block:
                    text = block['Text'].strip()
                    
                    # Assuming standard format: Date | Description | Amount
                    if col_index == 1:  # Date
                        current_row = {'date': text}
                    elif col_index == 2:  # Description
                        current_row['description'] = text
                    elif col_index == 3:  # Amount
                        current_row['amount'] = text
                        # Process complete row
                        try:
                            transactions.append(self.create_transaction(current_row))
                        except Exception as e:
                            print(f"Error processing row {current_row}: {e}")
        
        return transactions

    def create_transaction(self, row_data: Dict) -> Transaction:
        """Create a Transaction object from row data"""
        try:
            return Transaction(
                date=self.parse_date(row_data['date']),
                description=self.clean_description(row_data['description']),
                amount=self.parse_amount(row_data['amount'])
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")