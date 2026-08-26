#!/usr/bin/env bash
#
# build-spruch-images.sh
# Builds two Docker images from the Dockerfiles in the two "spruch" folders:
#   - spruch-frontend
#   - spruch-backend
#
# Usage:
#   ./build-spruch-images.sh                # builds both with tag "latest"
#   ./build-spruch-images.sh v1.2.0         # builds both with tag "v1.2.0"
#   ./build-spruch-images.sh latest --no-cache   # extra args are passed to `docker build`
#
set -euo pipefail

# --- Configuration -----------------------------------------------------------
# Set these to the folders that contain each Dockerfile.
# (They default to folders named after the images, sitting next to this script.)
FRONTEND_DIR="./spruch-frontend"
BACKEND_DIR="./spruch-api"

# Image names (as requested)
FRONTEND_IMAGE="spruch-frontend"
BACKEND_IMAGE="spruch-backend"

# Tag: first argument, or "latest" if none given.
TAG="${1:-latest}"
# Any further arguments are passed straight through to `docker build`
# (e.g. --no-cache, --pull, --build-arg KEY=VALUE).
shift || true
EXTRA_ARGS=("$@")
# -----------------------------------------------------------------------------

# Make sure docker is installed and the daemon is reachable.
if ! command -v docker >/dev/null 2>&1; then
  echo "Error: 'docker' is not installed or not on your PATH." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Error: cannot talk to the Docker daemon. Is Docker running?" >&2
  exit 1
fi

# build_image <context_dir> <image_name>
build_image() {
  local dir="$1"
  local image="$2"

  if [[ ! -d "$dir" ]]; then
    echo "Error: folder '$dir' does not exist." >&2
    exit 1
  fi
  if [[ ! -f "$dir/Dockerfile" ]]; then
    echo "Error: no Dockerfile found in '$dir'." >&2
    exit 1
  fi

  echo ""
  echo ">>> Building ${image}:${TAG} from ${dir}"
  docker build -t "${image}:${TAG}" "${EXTRA_ARGS[@]}" "$dir"
  echo ">>> Done: ${image}:${TAG}"
}

build_image "$FRONTEND_DIR" "$FRONTEND_IMAGE"
build_image "$BACKEND_DIR"  "$BACKEND_IMAGE"

echo ""
echo "Both images built successfully:"
docker images \
  --filter "reference=${FRONTEND_IMAGE}:${TAG}" \
  --filter "reference=${BACKEND_IMAGE}:${TAG}"
