#!/usr/bin/env python3

from __future__ import annotations

import html
import logging
import os
import secrets
import subprocess
import tempfile
from http import HTTPStatus
from pathlib import Path

from flask import Flask, Response, make_response, request
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} doit être un entier, valeur reçue: {raw!r}") from exc


BINARY = Path(
    os.environ.get(
        "IMAGEDVIO_BINARY",
        os.environ.get("RAW_ECHO_BINARY", str(Path(__file__).with_name("ImageDVIO"))),
    )
).resolve()
BIND = os.environ.get("IMAGEDVIO_BIND", os.environ.get("RAW_ECHO_BIND", "0.0.0.0"))
PORT = _env_int("IMAGEDVIO_PORT", _env_int("RAW_ECHO_PORT", 8080))
MAX_FILES = _env_int("IMAGEDVIO_MAX_FILES", 8)
MAX_REQUEST_BYTES = _env_int("IMAGEDVIO_MAX_REQUEST_BYTES", 8 * 1024 * 1024)
PARSER_TIMEOUT = _env_int("IMAGEDVIO_TIMEOUT", 8)
MAX_OUTPUT_CHARS = _env_int("IMAGEDVIO_MAX_OUTPUT_CHARS", 256 * 1024)

BASE_SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Opener-Policy": "same-origin",
}

PAGE_TEMPLATE = open("index.html", "r").read()

def render_page(body: str, nonce: str) -> bytes:
    page = PAGE_TEMPLATE.replace("__MAX_FILES__", str(MAX_FILES)).replace("__NONCE__", nonce).replace("__BODY__", body)
    return page.encode("utf-8")


def build_security_headers(nonce: str | None = None) -> dict[str, str]:
    headers = dict(BASE_SECURITY_HEADERS)
    if nonce is None:
        headers["Content-Security-Policy"] = "default-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    else:
        headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            f"style-src 'nonce-{nonce}'; "
            f"script-src 'nonce-{nonce}'; "
            "connect-src 'self'; "
            "form-action 'self'; "
            "base-uri 'none'; "
            "frame-ancestors 'none'"
        )
    return headers


def form_body() -> str:
    return """
<div class="panel">
  <form action="/upload" method="post" enctype="multipart/form-data" data-upload-form>
    <input id="images" class="visually-hidden" type="file" name="images" multiple accept=".png,.jpg,.jpeg,.dvqi">
    <div class="layout">
      <section class="stack">
        <div>
          <h2>Dépôt D'Images</h2>
          <label class="dropzone" for="images" data-dropzone>
            <span class="drop-badge">Glisser-déposer actif</span>
            <div class="drop-copy">
              <strong>Déposez vos fichiers dans cette zone.</strong>
              <p>Vous pouvez aussi cliquer pour parcourir vos dossiers. La liste ci-dessous représente l'ordre réel envoyé au parseur et reste modifiable avant validation.</p>
            </div>
            <div class="drop-meta">
              <span>Formats acceptés : PNG, JPEG, DVQI</span>
              <span>Lot : jusqu'à 8 fichiers</span>
            </div>
          </label>
          <div class="button-row mt-1">
            <button type="button" class="ghost-button" data-browse-files>Parcourir</button>
            <button type="button" class="ghost-button" data-clear-queue>Vider la file</button>
          </div>
          <p class="status-line" data-status></p>
          <div class="queue" data-queue></div>
          <noscript>
            <p>Ce portail fonctionne mieux avec JavaScript activé. Sans lui, utilisez le sélecteur de fichiers pour choisir tout le lot en une fois.</p>
          </noscript>
        </div>
      </section>
      <aside class="stack">
        <div class="meta-grid">
          <div class="meta-card">
            <strong>Options De Traitement</strong>
            <label class="checkbox checkbox-spaced">
              <input type="checkbox" name="include_probe" value="1" checked>
              <span>Afficher aussi les métadonnées du parseur</span>
            </label>
            <p>Le lot est envoyé tel quel au binaire natif ImageDVIO, sans réinterprétation côté navigateur.</p>
          </div>
        </div>
        <div class="button-row">
          <button type="submit" data-submit>Lancer l'analyse</button>
        </div>
      </aside>
    </div>
  </form>
</div>
"""


def _trim_output(value: str) -> str:
    if len(value) <= MAX_OUTPUT_CHARS:
        return value
    return value[:MAX_OUTPUT_CHARS] + f"\n[sortie tronquée à {MAX_OUTPUT_CHARS} caractères]"


def result_body(argv: list[str], stdout: str, stderr: str, returncode: int) -> str:
    escaped_argv = html.escape(" ".join(argv))
    escaped_stdout = html.escape(_trim_output(stdout))
    escaped_stderr = html.escape(_trim_output(stderr))
    return f"""
<div class="panel">
  <div class="button-row mb-1">
    <a class="ghost-button" href="/">Nouvel envoi</a>
  </div>
  <div class="meta-grid mb-1">
    <div class="meta-card">
      <strong>Commande Lancée</strong>
      <p><code>{escaped_argv}</code></p>
    </div>
    <div class="meta-card">
      <strong>Code Retour</strong>
      <p>{returncode}</p>
    </div>
  </div>
  <div class="result-grid">
    <div>
      <h2>Sortie Standard</h2>
      <pre>{escaped_stdout}</pre>
    </div>
    <div>
      <h2>Sortie D'Erreur</h2>
      <pre>{escaped_stderr}</pre>
    </div>
  </div>
</div>
"""


def apply_security_headers(response: Response, nonce: str | None = None) -> Response:
    for key, value in build_security_headers(nonce).items():
        response.headers[key] = value
    return response


def page_response(body: str, status: HTTPStatus = HTTPStatus.OK) -> Response:
    nonce = secrets.token_urlsafe(16)
    response = make_response(render_page(body, nonce), int(status))
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return apply_security_headers(response, nonce)


def text_response(payload: str, status: HTTPStatus = HTTPStatus.OK) -> Response:
    response = make_response(payload, int(status))
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return apply_security_headers(response)


def collect_uploaded_files() -> list:
    """Retourne les fichiers dans l'ordre voulu par l'interface.

    L'UI JavaScript envoie slot0, slot1, ... pour garantir l'ordre après
    réorganisation. Le champ historique images reste accepté pour compatibilité
    et pour le mode sans JavaScript.
    """
    ordered = []
    duplicate_slots: list[str] = []
    for slot_index in range(MAX_FILES):
        key = f"slot{slot_index}"
        values = [item for item in request.files.getlist(key) if item and item.filename]
        if len(values) > 1:
            duplicate_slots.append(key)
        if values:
            ordered.append(values[0])

    if duplicate_slots:
        raise ValueError("slot de fichier dupliqué: " + ", ".join(duplicate_slots))

    if ordered:
        return ordered

    return [item for item in request.files.getlist("images") if item and item.filename]


def materialize_uploads(file_items: list, temp_dir: Path) -> list[str]:
    temp_paths: list[str] = []
    for index, storage in enumerate(file_items):
        original_name = Path(storage.filename or "").name
        safe_name = secure_filename(original_name) or f"upload-{index}.bin"
        out_path = temp_dir / f"{index:02d}-{safe_name}"
        storage.save(out_path)
        temp_paths.append(str(out_path))
    return temp_paths


def decode_process_output(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return value.decode("utf-8", errors="replace")


def run_parser(argv: list[str]) -> tuple[str, str, int, HTTPStatus]:
    try:
        proc = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=PARSER_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = decode_process_output(exc.stdout)
        stderr = decode_process_output(exc.stderr) + "\ndélai d'exécution du parseur dépassé"
        return stdout, stderr, 124, HTTPStatus.GATEWAY_TIMEOUT
    except OSError as exc:
        return "", f"impossible de lancer le parseur: {exc}", 126, HTTPStatus.INTERNAL_SERVER_ERROR

    return decode_process_output(proc.stdout), decode_process_output(proc.stderr), proc.returncode, HTTPStatus.OK


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES
    app.config["MAX_FORM_PARTS"] = MAX_FILES + 8
    app.logger.setLevel(logging.INFO)

    @app.get("/")
    def index() -> Response:
        return page_response(form_body())

    @app.get("/healthz")
    def healthz() -> Response:
        if not BINARY.is_file():
            return text_response(f"binaire ImageDVIO introuvable: {BINARY}\n", HTTPStatus.SERVICE_UNAVAILABLE)
        if not os.access(BINARY, os.X_OK):
            return text_response(f"binaire ImageDVIO non exécutable: {BINARY}\n", HTTPStatus.SERVICE_UNAVAILABLE)
        return text_response("ok\n")

    @app.post("/upload")
    def upload() -> Response:
        if not BINARY.is_file() or not os.access(BINARY, os.X_OK):
            return page_response(
                result_body([str(BINARY)], "", f"binaire ImageDVIO introuvable ou non exécutable: {BINARY}", 126),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        try:
            file_items = collect_uploaded_files()
        except ValueError as exc:
            return page_response(result_body(["(aucune commande)"], "", str(exc), 1), HTTPStatus.BAD_REQUEST)

        if not file_items:
            return page_response(
                result_body(["(aucune commande)"], "", "aucun fichier n'a été envoyé", 1),
                HTTPStatus.BAD_REQUEST,
            )
        if len(file_items) > MAX_FILES:
            return page_response(
                result_body(["(aucune commande)"], "", "trop de fichiers envoyés", 1),
                HTTPStatus.BAD_REQUEST,
            )

        argv = [str(BINARY)]
        if request.form.get("include_probe"):
            argv.append("--probe")

        with tempfile.TemporaryDirectory(prefix="imagedvio-") as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            argv.extend(materialize_uploads(file_items, temp_dir))
            stdout, stderr, returncode, status = run_parser(argv)

        return page_response(result_body(argv, stdout, stderr, returncode), status)

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error: RequestEntityTooLarge) -> Response:
        return page_response(
            result_body(["(aucune commande)"], "", "requête trop volumineuse", 1),
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )

    @app.errorhandler(404)
    def not_found(_error) -> Response:  # type: ignore[no-untyped-def]
        return page_response(
            result_body(["(aucune commande)"], "", "ressource introuvable", 404),
            HTTPStatus.NOT_FOUND,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=BIND, port=PORT)
