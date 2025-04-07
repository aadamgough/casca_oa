from datetime import datetime
from decimal import Decimal
import re
from typing import List, Dict
from ..models.transaction import Transaction

class PreprocessingService:
    def __init__(self):
        self.debug = True
        
    def log(self, message: str):
        """Debug logging"""
        if self.debug:
            print(f"DEBUG: {message}")

    def find_potential_header(self, blocks: List[Dict], current_block: Dict) -> str:
        """Find potential header by looking at text above the current position"""
        current_left = current_block['Geometry']['BoundingBox']['Left']
        current_top = current_block['Geometry']['BoundingBox']['Top']
        
        potential_headers = []
        for block in blocks:
            if block['BlockType'] != 'LINE' or 'Text' not in block:
                continue
                
            block_left = block['Geometry']['BoundingBox']['Left']
            block_top = block['Geometry']['BoundingBox']['Top']
            
            # Check if block is above current line and in similar horizontal position
            if (block_top < current_top and 
                abs(block_left - current_left) < 0.1):  # Adjust threshold as needed
                potential_headers.append(block['Text'])
        
        # Take the closest header above current position
        return potential_headers[-1] if potential_headers else "UNKNOWN"

    def process_textract_blocks(self, blocks: List[Dict]) -> List[Transaction]:
        """Process Textract blocks into transactions"""
        transactions = []
        
        # Get all LINE blocks
        lines = [
            block for block in blocks 
            if block['BlockType'] == 'LINE' and 
            'Text' in block and 
            block['Text'].strip() and
            len(block['Text'].strip()) > 3  # Skip very short lines
        ]
        
        self.log(f"Found {len(lines)} LINE blocks")
        
        for line in lines:
            text = line['Text'].strip()
            
            # Find potential header for this line based on geometry
            potential_header = self.find_potential_header(blocks, line)
            self.log(f"\nProcessing line: {text} (Potential header: {potential_header})")
            
            try:
                transaction = Transaction(
                    date=datetime.now(),           # Default current date
                    description=text,              # Use full line as description
                    amount=Decimal('0.00'),        # Default amount
                    transaction_type="UNKNOWN",    # Required field
                    category=potential_header,     # Use potential header as category
                    status="UNVERIFIED",           # Default status
                    balance_after=Decimal('0.00')  # Required field
                )
                
                transactions.append(transaction)
                self.log(f"Created transaction: {transaction}")
                
            except Exception as e:
                self.log(f"Error creating transaction: {str(e)}")
                continue
        
        self.log(f"\nTotal transactions found: {len(transactions)}")
        return transactions

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime"""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y',
            '%d/%m/%Y', '%d-%m-%Y',
            '%m/%d/%y', '%m-%d-%y',
            '%Y-%m-%d'  # ISO format
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")

    def parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string into Decimal"""
        # Remove currency symbols, spaces, and commas
        clean_amount = amount_str.replace('$', '').replace(',', '').replace(' ', '')
        
        # Handle negative amounts in parentheses
        if '(' in clean_amount and ')' in clean_amount:
            clean_amount = '-' + clean_amount.replace('(', '').replace(')', '')
        
        try:
            return Decimal(clean_amount)
        except:
            raise ValueError(f"Unable to parse amount: {amount_str}")

    def clean_description(self, description: str) -> str:
        """Clean and normalize description"""
        # Convert to uppercase and remove extra spaces
        desc = ' '.join(description.upper().split())
        
        # Remove special characters but keep spaces and basic punctuation
        desc = re.sub(r'[^A-Z0-9\s\-\.]', '', desc)
        
        return desc.strip() or 'UNKNOWN'