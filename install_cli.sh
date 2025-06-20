#!/bin/bash

set -e

REPO="vladimirpesic/juggler"
VERSION="1.0.0"
TARBALL="juggler-x86_64-unknown-linux-gnu.tar.bz2"
DOWNLOAD_URL="https://github.com/${REPO}/releases/download/v${VERSION}/${TARBALL}"
INSTALL_DIR="$HOME/.local/bin"
BINARY="juggler"

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required but not installed."
    exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
    echo "Error: tar is required but not installed."
    exit 1
fi

echo "Downloading ${TARBALL} from ${DOWNLOAD_URL}..."
curl -fsSL "${DOWNLOAD_URL}" -o "/tmp/${TARBALL}"

echo "Extracting ${TARBALL}..."
tar -xjf "/tmp/${TARBALL}" -C "/tmp"

echo "Installing ${BINARY} to ${INSTALL_DIR}..."
if [ -w "${INSTALL_DIR}" ]; then
    mv "/tmp/${BINARY}" "${INSTALL_DIR}/${BINARY}"
else
    echo "Need sudo to write to ${INSTALL_DIR}"
    sudo mv "/tmp/${BINARY}" "${INSTALL_DIR}/${BINARY}"
fi

chmod +x "${INSTALL_DIR}/${BINARY}"

rm "/tmp/${TARBALL}"

echo "${BINARY} v${VERSION} installed successfully!"
