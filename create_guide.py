from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Flowable
)


ROOT = Path(__file__).parent
OUT = ROOT / "output" / "pdf" / "dynamic_pricing_implementation_guide.pdf"


class ArchitectureDiagram(Flowable):
    def __init__(self, width=175 * mm, height=95 * mm):
        super().__init__()
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        x0, y0 = 6 * mm, 12 * mm
        box_w, box_h = 38 * mm, 17 * mm
        gap_x, gap_y = 7 * mm, 8 * mm
        colors_map = [colors.HexColor("#E8F1FB"), colors.HexColor("#EAF7EF"), colors.HexColor("#FFF3D6")]
        boxes = [
            ("CSV / API input", 0, 2, colors_map[0]),
            ("Validation +\nnormalization", 1, 2, colors_map[0]),
            ("City graph\nKD-tree", 2, 2, colors_map[1]),
            ("Dijkstra\nshortest paths", 3, 2, colors_map[1]),
            ("Demand\nforecaster", 1, 1, colors_map[2]),
            ("Pricing engine", 2, 1, colors_map[2]),
            ("CSV output /\nJSON API", 3, 1, colors_map[0]),
            ("Monitoring, tests,\npolicy review", 2, 0, colors_map[1]),
        ]
        positions = {}
        for label, col, row, fill in boxes:
            x = x0 + col * (box_w + gap_x)
            y = y0 + row * (box_h + gap_y)
            positions[label] = (x, y)
            c.setFillColor(fill)
            c.setStrokeColor(colors.HexColor("#355070"))
            c.roundRect(x, y, box_w, box_h, 3 * mm, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#17324D"))
            c.setFont("Helvetica-Bold", 8)
            lines = label.split("\n")
            for i, line in enumerate(lines):
                c.drawCentredString(x + box_w / 2, y + box_h / 2 + (len(lines) - 1 - i) * 8, line)

        def arrow(a, b):
            xa, ya = positions[a]
            xb, yb = positions[b]
            c.setStrokeColor(colors.HexColor("#5A6B7B"))
            c.setLineWidth(1.2)
            c.line(xa + box_w, ya + box_h / 2, xb, yb + box_h / 2)
            c.line(xb - 2 * mm, yb + box_h / 2 + 1.2 * mm, xb, yb + box_h / 2)
            c.line(xb - 2 * mm, yb + box_h / 2 - 1.2 * mm, xb, yb + box_h / 2)

        arrow("CSV / API input", "Validation +\nnormalization")
        arrow("Validation +\nnormalization", "City graph\nKD-tree")
        arrow("City graph\nKD-tree", "Dijkstra\nshortest paths")
        arrow("Validation +\nnormalization", "Demand\nforecaster")
        arrow("Dijkstra\nshortest paths", "Pricing engine")
        arrow("Demand\nforecaster", "Pricing engine")
        arrow("Pricing engine", "CSV output /\nJSON API")
        arrow("Pricing engine", "Monitoring, tests,\npolicy review")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=colors.HexColor("#17324D"), alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontSize=12, leading=17, textColor=colors.HexColor("#557086"), alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#17324D"), spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#2D5D7B"), spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=colors.HexColor("#263746"), spaceAfter=6))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.2, leading=11, textColor=colors.HexColor("#415466"), spaceAfter=4))
styles.add(ParagraphStyle(name="CodeCustom", parent=styles["BodyText"], fontName="Courier", fontSize=8, leading=11, backColor=colors.HexColor("#F1F5F8"), borderColor=colors.HexColor("#D5E0E8"), borderWidth=0.5, borderPadding=6, spaceBefore=3, spaceAfter=7))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=9.5, leading=14, textColor=colors.HexColor("#17324D"), backColor=colors.HexColor("#EAF7EF"), borderColor=colors.HexColor("#84B59A"), borderWidth=0.7, borderPadding=8, spaceBefore=5, spaceAfter=8))


def P(text, style="BodyCustom"):
    return Paragraph(text, styles[style])


def bullets(items):
    return KeepTogether([P("&#8226; " + item, "BodyCustom") for item in items])


def table(data, widths=None, header=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D6E0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
        commands.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FA")]))
    t.setStyle(TableStyle(commands))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D4DEE6"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#71808C"))
    canvas.drawString(18 * mm, 9 * mm, "Dynamic E-Commerce Pricing | Implementation Guide")
    canvas.drawRightString(192 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=20 * mm, title="Dynamic E-Commerce Pricing - Implementation Guide", author="Codex")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=footer)])
    story = []

    story += [Spacer(1, 20 * mm), P("Dynamic E-Commerce Pricing", "TitleCustom"), P("Architecture, implementation, technology stack, setup, and handoff guide", "Subtitle"), Spacer(1, 7 * mm)]
    story += [P("Purpose", "H2Custom"), P("This document gives your friend everything needed to create the architecture diagram and explain the complete implementation. The system combines location-aware logistics pricing, Dijkstra shortest paths, and machine-learning demand forecasting.", "BodyCustom")]
    story += [P("What was implemented", "H2Custom"), table([[P("Area", "Small"), P("Implementation", "Small")], [P("Geospatial layer", "Small"), P("Haversine distance, KD-tree neighbor search, city graph", "Small")], [P("Routing layer", "Small"), P("Dijkstra shortest paths from an origin city", "Small")], [P("Demand layer", "Small"), P("Random Forest regression with categorical encoding and temporal features", "Small")], [P("Pricing layer", "Small"), P("Transport-cost and demand-adjusted price calculation", "Small")], [P("Interfaces", "Small"), P("CLI for batch jobs and JSON HTTP API for integration", "Small")], [P("Quality", "Small"), P("Unit tests, demo data, validation, and reproducible commands", "Small")]], [42 * mm, 128 * mm])]
    story += [Spacer(1, 5 * mm), P("Important interpretation: the attached paper is the technical specification. The user's request is to implement and document it. The implementation is a decision-support baseline; production pricing still needs business policy, fairness review, tax/shipping rules, authentication, and monitoring.", "Callout"), PageBreak()]

    story += [P("1. Architecture overview", "H1Custom"), P("The architecture is a batch/online hybrid. CSV files are the simplest input for experiments and scheduled jobs. The JSON endpoint exposes the same pipeline for an e-commerce service. Both paths converge on the same validation, geographic, forecasting, and pricing modules.", "BodyCustom"), ArchitectureDiagram(), Spacer(1, 5 * mm), P("Diagram labels to use", "H2Custom"), table([[P("Box", "Small"), P("What to show", "Small")], [P("CSV / API input", "Small"), P("City master data and historical transactions", "Small")], [P("Validation + normalization", "Small"), P("Column aliases, dates, numeric types, required fields", "Small")], [P("City graph / KD-tree", "Small"), P("Fast nearby-city discovery and weighted edges", "Small")], [P("Dijkstra", "Small"), P("Shortest route distance from the warehouse/origin", "Small")], [P("Demand forecaster", "Small"), P("Monthly demand features and Random Forest model", "Small")], [P("Pricing engine", "Small"), P("Distance cost plus demand multiplier", "Small")], [P("Output", "Small"), P("Priced CSV, API JSON, metrics and audit data", "Small")]], [48 * mm, 122 * mm]), PageBreak()]

    story += [P("2. End-to-end implementation", "H1Custom")]
    story += [P("Step 1 - Load and normalize data", "H2Custom"), P("The pipeline reads a city table and a transaction table. Column names are normalized to lowercase and common retail aliases are accepted: StockCode becomes product, InvoiceDate becomes date, Quantity becomes quantity, and UnitPrice becomes unit_price. Missing required columns produce a clear validation error.", "BodyCustom")]
    story += [P("Required city fields", "H2Custom"), table([[P("Field", "Small"), P("Type", "Small"), P("Meaning", "Small")], [P("city", "Small"), P("string", "Small"), P("Unique city name", "Small")], [P("latitude", "Small"), P("float", "Small"), P("Latitude in degrees", "Small")], [P("longitude", "Small"), P("float", "Small"), P("Longitude in degrees", "Small")]], [40 * mm, 28 * mm, 102 * mm])]
    story += [P("Required transaction fields", "H2Custom"), table([[P("Field", "Small"), P("Type", "Small"), P("Meaning", "Small")], [P("product", "Small"), P("string", "Small"), P("SKU or product identifier", "Small")], [P("city", "Small"), P("string", "Small"), P("Customer/delivery city", "Small")], [P("date", "Small"), P("date", "Small"), P("Transaction date", "Small")], [P("quantity", "Small"), P("number", "Small"), P("Units sold", "Small")], [P("unit_price", "Small"), P("number", "Small"), P("Original price before adjustment", "Small")]], [40 * mm, 28 * mm, 102 * mm])]
    story += [P("Step 2 - Construct the geographic graph", "H2Custom"), P("Each city is a node. The KD-tree finds candidate city pairs near one another. The exact Haversine distance is then calculated and only pairs within the configured maximum distance, 500 km by default, become undirected weighted edges. This avoids an expensive all-pairs comparison on larger datasets.", "BodyCustom")]
    story += [P("Step 3 - Compute route distances", "H2Custom"), P("Dijkstra starts at the configured origin, normally a warehouse or distribution hub. It initializes the origin at distance zero and all other cities at infinity, then repeatedly relaxes the lowest-cost edge. The result is a map from every reachable city to its shortest logistics distance.", "BodyCustom")]
    story += [P("Step 4 - Prepare demand features", "H2Custom"), P("Transactions are aggregated by product, city, year, and month. Month and year expose seasonal behavior while product and city capture different demand patterns. The forecaster uses a one-hot encoder for product/city and passes year/month as numeric features.", "BodyCustom")]
    story += [P("Step 5 - Train and evaluate the model", "H2Custom"), P("A Random Forest Regressor is trained on historical monthly demand. A held-out split calculates mean squared error when enough records are available. If the ML dependency or dataset is too small, the implementation safely falls back to the product-city historical mean, then the global mean.", "BodyCustom")]
    story += [P("Step 6 - Calculate dynamic price", "H2Custom"), P("For each transaction, the system looks up route distance and predicts demand. Transport cost is distance multiplied by fuel consumption and fuel price. The demand multiplier increases or decreases the original unit price based on predicted demand relative to the baseline, with a configurable cap.", "BodyCustom"), P("dynamic_price = unit_price * demand_multiplier + transport_cost", "CodeCustom")]
    story += [P("Default configuration", "H2Custom"), table([[P("Parameter", "Small"), P("Default", "Small"), P("Role", "Small")], [P("max_distance_km", "Small"), P("500", "Small"), P("Maximum graph edge distance", "Small")], [P("fuel_litres_per_km", "Small"), P("0.025", "Small"), P("Fuel consumption assumption", "Small")], [P("fuel_price_per_litre", "Small"), P("1.72", "Small"), P("Transport price assumption", "Small")], [P("demand_sensitivity", "Small"), P("0.05", "Small"), P("Price response to demand ratio", "Small")], [P("max_demand_multiplier", "Small"), P("1.50", "Small"), P("Safety cap on demand multiplier", "Small")]], [58 * mm, 28 * mm, 84 * mm]), PageBreak()]

    story += [P("3. Technology stack", "H1Custom"), table([[P("Layer", "Small"), P("Technology", "Small"), P("Why it is used", "Small")], [P("Language", "Small"), P("Python 3", "Small"), P("Fast implementation for data, graph algorithms, ML, and APIs", "Small")], [P("Data", "Small"), P("pandas, NumPy", "Small"), P("CSV handling, grouping, dates, numeric operations", "Small")], [P("Machine learning", "Small"), P("scikit-learn", "Small"), P("OneHotEncoder, ColumnTransformer, RandomForestRegressor, MSE", "Small")], [P("Spatial search", "Small"), P("SciPy cKDTree", "Small"), P("Efficient nearby-city candidate search", "Small")], [P("Routing", "Small"), P("Python heapq", "Small"), P("Priority queue for Dijkstra", "Small")], [P("API", "Small"), P("Python http.server", "Small"), P("Dependency-light JSON endpoint for the baseline", "Small")], [P("Testing", "Small"), P("unittest", "Small"), P("Distance, routing, and pricing regression tests", "Small")], [P("Documentation PDF", "Small"), P("ReportLab", "Small"), P("Programmatic, repeatable guide generation", "Small")]], [38 * mm, 45 * mm, 87 * mm]), P("Why no database or frontend yet?", "H2Custom"), P("The paper describes an analytics and pricing engine rather than a complete marketplace. The baseline keeps storage file-based so the algorithm can be tested easily. For a production architecture, add PostgreSQL for master/transaction data, Redis for route/model caching, object storage for datasets, a scheduled worker, and an authenticated API gateway.", "BodyCustom"), PageBreak()]

    story += [P("4. Project structure", "H1Custom"), P("The friend creating the architecture diagram can map each box to these files:", "BodyCustom"), table([[P("Path", "Small"), P("Responsibility", "Small")], [P("dynamic_pricing/geo.py", "Small"), P("Haversine formula, CityGraph, KD-tree graph construction, Dijkstra", "Small")], [P("dynamic_pricing/demand.py", "Small"), P("Feature preparation, Random Forest forecasting, fallback behavior", "Small")], [P("dynamic_pricing/pricing.py", "Small"), P("Pipeline orchestration and price calculation", "Small")], [P("dynamic_pricing/cli.py", "Small"), P("Demo data generation and batch CSV command", "Small")], [P("dynamic_pricing/api.py", "Small"), P("POST /price JSON endpoint", "Small")], [P("tests/test_core.py", "Small"), P("Core regression tests", "Small")], [P("data/", "Small"), P("Generated sample cities and transactions", "Small")], [P("output/", "Small"), P("Generated priced transaction files", "Small")]], [58 * mm, 112 * mm]), P("Suggested production additions", "H2Custom"), bullets(["Authentication and authorization around the API.", "Persistent storage for cities, transactions, model versions, and pricing decisions.", "A model registry and scheduled retraining workflow.", "Audit logging: input data version, model version, policy parameters, and final price.", "Fairness and abuse checks so location is used for logistics cost rather than protected-trait discrimination.", "Observability: request latency, unreachable cities, forecast error, price deltas, and revenue/customer-impact metrics."]), PageBreak()]

    story += [P("5. How to run", "H1Custom"), P("Windows PowerShell commands", "H2Custom"), P("cd C:\\Users\\malha\\OneDrive\\Desktop\\dynamic-pricing\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt", "CodeCustom"), P("Run the full demo", "H2Custom"), P("python -m dynamic_pricing.cli demo", "CodeCustom"), P("This creates data/cities.csv, data/transactions.csv, and output/priced_transactions.csv.", "BodyCustom"), P("Run with your own files", "H2Custom"), P("python -m dynamic_pricing.cli price `\n  --cities data/cities.csv `\n  --transactions data/transactions.csv `\n  --origin London `\n  --output output/priced_transactions.csv", "CodeCustom"), P("Start the JSON API", "H2Custom"), P("python -m dynamic_pricing.api", "CodeCustom"), P("The API listens on http://127.0.0.1:8000 and accepts POST /price. The request body contains origin, cities, and transactions arrays. The response contains rows and demand metrics.", "BodyCustom")]
    story += [P("Example API request shape", "H2Custom"), P('{"origin":"London","cities":[{"city":"London","latitude":51.5072,"longitude":-0.1276}],"transactions":[{"product":"SKU-1","city":"London","date":"2025-01-15","quantity":3,"unit_price":25.0}]}', "CodeCustom"), PageBreak()]

    story += [P("6. Testing and expected outputs", "H1Custom"), P("Run tests with:", "BodyCustom"), P("python -m unittest discover -s tests -v", "CodeCustom"), P("The current test suite checks that the Haversine result is sensible, Dijkstra finds the expected multi-hop route, and pricing produces dynamic_price with distance-based differentiation. The demo also provides a smoke test for the complete pipeline.", "BodyCustom"), P("Output columns", "H2Custom"), table([[P("Column", "Small"), P("Description", "Small")], [P("route_distance_km", "Small"), P("Shortest distance from the origin; NaN if unreachable", "Small")], [P("predicted_demand", "Small"), P("Forecast quantity for product/city/date", "Small")], [P("transport_cost", "Small"), P("Distance multiplied by fuel assumptions", "Small")], [P("demand_multiplier", "Small"), P("Demand-based adjustment applied to unit price", "Small")], [P("dynamic_price", "Small"), P("Final recommended price rounded to two decimals", "Small")]], [55 * mm, 115 * mm]), P("Validation checklist for a real deployment", "H2Custom"), bullets(["Compare predicted demand with a time-based holdout, not only a random split.", "Check disconnected cities and missing coordinates before accepting a price.", "Back-test revenue, conversion, margin, cancellation, and delivery-cost impact.", "Keep a maximum price-change policy and a manual override.", "Version every model and every configuration used to produce a price.", "Do not expose internal model details or customer-sensitive information in public responses."]), PageBreak()]

    story += [P("7. One-minute explanation for the presentation", "H1Custom"), P("The system receives city coordinates and historical retail transactions. It uses a KD-tree to efficiently connect nearby cities, assigns Haversine distances as edge weights, and uses Dijkstra to find the shortest route from a distribution hub. In parallel, it aggregates sales by product, city, and month, then trains a Random Forest model to forecast demand. The pricing engine combines the route's transport cost with the demand multiplier and returns a dynamic price. The same pipeline runs through a batch CLI or a JSON API.", "Callout"), P("Recommended architecture diagram arrows", "H2Custom"), bullets(["Input files/API -> validation and normalization", "Validation -> KD-tree city graph", "KD-tree graph -> Dijkstra shortest paths", "Validation -> demand feature engineering and ML model", "Shortest paths + demand forecasts -> pricing engine", "Pricing engine -> CSV/API output", "Pricing decisions -> monitoring, audit, and policy review"]), P("Final handoff", "H2Custom"), P("The friend should draw the logical architecture, not only a flowchart. Include the data stores, algorithm modules, model training/inference boundary, configuration parameters, output consumers, and monitoring/audit path. For a class or hackathon presentation, the diagram can use the eight boxes shown in this guide; for production, add the database, scheduler, model registry, cache, API gateway, and authentication.", "BodyCustom")]

    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
