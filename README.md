# Invoice Generator

Generate clean, printable HTML invoices from a simple JSON file.

## Features
- Line items with quantity + rate
- Tax calculation
- Due date
- Professional printable layout (Print → Save as PDF)

## Usage
```bash
# Create a sample invoice definition
python invoice.py sample

# Edit sample-invoice.json, then generate
python invoice.py sample-invoice.json

# Custom output name
python invoice.py sample-invoice.json client-a-001.html
```

Open the HTML file in a browser and use **Print → Save as PDF**.
