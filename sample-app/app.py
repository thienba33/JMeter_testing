#!/usr/bin/env python3
"""
Ung dung web mau (System Under Test) cho bai kiem thu hieu nang JMeter.
Chi dung thu vien chuan cua Python - khong can cai them goi nao.

Chay:  python3 sample-app/app.py            # cong 8089
       PORT=9000 python3 sample-app/app.py  # doi cong

Cac endpoint:
  GET  /                        Trang chu (HTML)
  GET  /api/health              Kiem tra trang thai
  GET  /api/products            Danh sach san pham (phan trang ?page=&size=)
  GET  /api/products/{id}       Chi tiet san pham
  GET  /api/products/search?q=  Tim kiem san pham theo ten
  GET  /api/users               Danh sach nguoi dung
  GET  /api/users/{id}          Chi tiet nguoi dung
  POST /api/orders              Tao don hang moi  -> 201
"""
import json
import os
import random
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

random.seed(42)

CATEGORIES = ["Dien thoai", "Laptop", "Tai nghe", "Dong ho", "May anh", "Phu kien"]
PRODUCTS = [
    {"id": i, "name": f"San pham {i:03d} - {random.choice(CATEGORIES)}",
     "category": random.choice(CATEGORIES),
     "price": random.randrange(100_000, 50_000_000, 10_000),
     "stock": random.randrange(0, 500)}
    for i in range(1, 101)
]
USERS = [
    {"id": i, "name": f"Nguoi dung {i:02d}", "email": f"user{i}@example.com",
     "role": random.choice(["customer", "admin", "seller"])}
    for i in range(1, 51)
]
ORDERS = []
_next_order_id = 1


def find(items, item_id):
    return next((x for x in items if x["id"] == item_id), None)


class Handler(BaseHTTPRequestHandler):
    server_version = "SampleShop/1.0"

    def log_message(self, fmt, *args):  # tat log mac dinh cho gon terminal
        pass

    def _send(self, code, payload, content_type="application/json; charset=utf-8"):
        body = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path, qs = parsed.path.rstrip("/") or "/", parse_qs(parsed.query)

        if path == "/":
            self._send(200, "<html><head><title>Sample Shop</title></head>"
                            "<body><h1>Sample Shop - Ung dung mau cho kiem thu JMeter</h1>"
                            "<p>Xem API tai /api/products, /api/users, /api/health</p></body></html>",
                       "text/html; charset=utf-8")
        elif path == "/api/health":
            self._send(200, {"status": "UP", "products": len(PRODUCTS), "users": len(USERS), "orders": len(ORDERS)})
        elif path == "/api/products":
            page, size = int(qs.get("page", [1])[0]), int(qs.get("size", [20])[0])
            start = (page - 1) * size
            self._send(200, {"page": page, "size": size, "total": len(PRODUCTS),
                             "data": PRODUCTS[start:start + size]})
        elif path == "/api/products/search":
            q = qs.get("q", [""])[0].lower()
            time.sleep(0.02)  # mo phong xu ly tim kiem ton thoi gian hon tra cuu thong thuong
            result = [p for p in PRODUCTS if q in p["name"].lower() or q in p["category"].lower()]
            self._send(200, {"keyword": q, "total": len(result), "data": result[:20]})
        elif path.startswith("/api/products/"):
            item = find(PRODUCTS, int(path.rsplit("/", 1)[1])) if path.rsplit("/", 1)[1].isdigit() else None
            self._send(200, item) if item else self._send(404, {"error": "Khong tim thay san pham"})
        elif path == "/api/users":
            self._send(200, {"total": len(USERS), "data": USERS})
        elif path.startswith("/api/users/"):
            item = find(USERS, int(path.rsplit("/", 1)[1])) if path.rsplit("/", 1)[1].isdigit() else None
            self._send(200, item) if item else self._send(404, {"error": "Khong tim thay nguoi dung"})
        else:
            self._send(404, {"error": "Duong dan khong ton tai"})

    def do_POST(self):
        global _next_order_id
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") == "/api/orders":
            length = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                return self._send(400, {"error": "JSON khong hop le"})
            if "productId" not in data or "quantity" not in data:
                return self._send(400, {"error": "Thieu productId hoac quantity"})
            product = find(PRODUCTS, int(data["productId"]))
            if not product:
                return self._send(404, {"error": "Khong tim thay san pham"})
            order = {"id": _next_order_id, "productId": product["id"],
                     "quantity": int(data["quantity"]),
                     "total": product["price"] * int(data["quantity"]), "status": "CREATED"}
            _next_order_id += 1
            ORDERS.append(order)
            self._send(201, order)
        else:
            self._send(404, {"error": "Duong dan khong ton tai"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8089"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Sample Shop dang chay tai http://127.0.0.1:{port}  (Ctrl+C de dung)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung server.")
