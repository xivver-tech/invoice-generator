#!/usr/bin/env python3
"""
Invoice Generator
Creates clean, printable HTML invoices from a simple JSON description.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Invoice {number}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
    h1 {{ margin-bottom: 0.2rem; }}
    .meta {{ color: #555; margin-bottom: 2rem; }}
    .parties {{ display: flex; justify-content: space-between; margin-bottom: 2rem; }}
    .parties div {{ width: 45%; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; }}
    th, td {{ padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid #ddd; }}
    th {{ background: #f5f5f5; }}
    .right {{ text-align: right; }}
    .totals {{ margin-top: 1rem; width: 280px; margin-left: auto; }}
    .totals td {{ border: none; }}
    .totals .grand {{ font-weight: 700; font-size: 1.15rem; }}
    .notes {{ margin-top: 2rem; color: #555; font-size: 0.95rem; }}
    @media print {{
      body {{ margin: 0; }}
      .no-print {{ display: none; }}
    }}
  </style>
</head>
<body>
  <h1>INVOICE</h1>
  <div class="meta">
    <strong>#{number}</strong><br>
    Date: {date}<br>
    Due: {due}
  </div>

  <div class="parties">
    <div>
      <strong>From</strong><br>
      {from_name}<br>
      {from_address}
    </div>
    <div>
      <strong>Bill To</strong><br>
      {to_name}<br>
      {to_address}
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Description</th>
        <th class="right">Qty</th>
        <th class="right">Rate</th>
        <th class="right">Amount</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <table class="totals">
    <tr><td>Subtotal</td><td class="right">{subtotal}</td></tr>
    <tr><td>Tax ({tax_rate}%)</td><td class="right">{tax}</td></tr>
    <tr class="grand"><td>Total</td><td class="right">{total}</td></tr>
  </table>

  {notes_block}

  <p class="no-print" style="margin-top:3rem;color:#888">
    Open this file in a browser and use Print → Save as PDF
  </p>
</body>
</html>
"""

def money(n):
    return f"${n:,.2f}"

def generate(data, output="invoice.html"):
    items = data.get("items", [])
    rows = []
    subtotal = 0.0
    for it in items:
        qty = float(it.get("qty", 1))
        rate = float(it.get("rate", 0))
        amount = qty * rate
        subtotal += amount
        rows.append(
            f"<tr><td>{it.get('description','')}</td>"
            f"<td class='right'>{qty:g}</td>"
            f"<td class='right'>{money(rate)}</td>"
            f"<td class='right'>{money(amount)}</td></tr>"
        )

    tax_rate = float(data.get("tax_rate", 0))
    tax = subtotal * tax_rate / 100
    total = subtotal + tax

    notes = data.get("notes", "")
    notes_block = f'<div class="notes"><strong>Notes</strong><br>{notes}</div>' if notes else ""

    today = datetime.now()
    due_days = int(data.get("due_days", 14))
    due = (today + timedelta(days=due_days)).strftime("%Y-%m-%d")

    html = TEMPLATE.format(
        number=data.get("number", "001"),
        date=today.strftime("%Y-%m-%d"),
        due=due,
        from_name=data.get("from", {}).get("name", ""),
        from_address=data.get("from", {}).get("address", "").replace("\n", "<br>"),
        to_name=data.get("to", {}).get("name", ""),
        to_address=data.get("to", {}).get("address", "").replace("\n", "<br>"),
        rows="\n".join(rows),
        subtotal=money(subtotal),
        tax_rate=f"{tax_rate:g}",
        tax=money(tax),
        total=money(total),
        notes_block=notes_block
    )

    Path(output).write_text(html, encoding="utf-8")
    print(f"✓ Invoice written to {output}")
    print(f"  Total: {money(total)}")

def sample():
    sample_data = {
        "number": "2026-001",
        "from": {
            "name": "Your Name / Company",
            "address": "123 Main St\nCity, Country"
        },
        "to": {
            "name": "Client Name",
            "address": "456 Client Ave\nCity, Country"
        },
        "items": [
            {"description": "Website design", "qty": 1, "rate": 1200},
            {"description": "Hosting (12 months)", "qty": 12, "rate": 15},
            {"description": "Support hours", "qty": 5, "rate": 80}
        ],
        "tax_rate": 10,
        "due_days": 14,
        "notes": "Payment due within 14 days. Thank you for your business."
    }
    Path("sample-invoice.json").write_text(json.dumps(sample_data, indent=2), encoding="utf-8")
    print("✓ Created sample-invoice.json")
    print("  Edit it, then run: python invoice.py sample-invoice.json")

def main():
    if len(sys.argv) < 2:
        print("""Invoice Generator
=================
  python invoice.py sample          Create a sample JSON
  python invoice.py <file.json>     Generate HTML invoice
  python invoice.py <file.json> out.html
""")
        return

    if sys.argv[1] == "sample":
        sample()
        return

    path = Path(sys.argv[1])
    if not path.exists():
        print("File not found:", path)
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    output = sys.argv[2] if len(sys.argv) > 2 else f"invoice-{data.get('number', 'out')}.html"
    generate(data, output)

if __name__ == "__main__":
    main()
