"""Minimal JSON API for pricing requests."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import pandas as pd

from .pricing import price_transactions


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/price":
            self.send_error(404)
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            result = price_transactions(pd.DataFrame(body["cities"]), pd.DataFrame(body["transactions"]), body["origin"])
            payload = {"rows": result.fillna(0).to_dict(orient="records"), "metrics": result.attrs.get("demand_metrics", {})}
            encoded = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        except Exception as exc:
            self.send_error(400, str(exc))


def main():
    print("Pricing API listening on http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()


if __name__ == "__main__":
    main()
