#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${DATA_DIR:-/data}"
FILES_TTL_DAYS="${FILES_TTL_DAYS:-7}"

find "$DATA_DIR/files" -name "*.docx" -mtime +"$FILES_TTL_DAYS" -delete

