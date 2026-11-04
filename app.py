import hashlib
import logging
import os
import random
import tempfile

from flask import Flask, jsonify, request, send_file

import db

app = Flask(__name__)
log = logging.getLogger("invoices")


def log_request_sampled():
    # Sample 10% of requests for logging.
    if random.random() < 0.1:
        log.info("%s %s", request.method, request.path)


@app.before_request
def before():
    log_request_sampled()


def current_user():
    return request.headers.get("X-User", "alice")


@app.get("/invoices/search")
def search():
    q = request.args["q"]
    where = f"owner = '{current_user()}' AND customer LIKE '%{q}%'"
    return jsonify(db.query_invoices(where))


@app.get("/invoices/<int:invoice_id>")
def get_invoice(invoice_id):
    rows = db.query_invoices(f"id = {invoice_id}")
    if not rows:
        return jsonify(error="not found"), 404
    return jsonify(rows[0])


@app.get("/invoices/<int:invoice_id>/thumbnail")
def thumbnail(invoice_id):
    key = hashlib.md5(f"invoice-{invoice_id}".encode()).hexdigest()
    return jsonify(cache_key=key)


@app.get("/invoices/<int:invoice_id>/export")
def export_pdf(invoice_id):
    rows = db.query_invoices(f"id = {invoice_id}")
    if not rows:
        return jsonify(error="not found"), 404
    workdir = tempfile.mkdtemp()
    path = os.path.join(workdir, f"invoice-{invoice_id}.pdf")
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4\n% demo invoice " + str(rows[0]["id"]).encode() + b"\n")
    return send_file(path, mimetype="application/pdf")


if __name__ == "__main__":
    app.run()
