#!/usr/bin/env bash
#
# Local artifact signing demo using endorctl for the Death Star Operations Platform.
# Builds a service image, signs it with Endor Labs, then verifies the signature.
#
# Usage:
#   ./scripts/sign-artifacts.sh                       # sign & verify gateway image
#   ./scripts/sign-artifacts.sh --service <name>      # sign a specific service
#   ./scripts/sign-artifacts.sh --image <ref>         # sign a pre-built image
#   ./scripts/sign-artifacts.sh --verify-only <ref>   # verify only
#   ./scripts/sign-artifacts.sh --jar <service>       # sign a JAR artifact
#   ./scripts/sign-artifacts.sh --revoke <ref>        # revoke a signature
#
set -euo pipefail

REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_OWNER="${IMAGE_OWNER:-endor-matt}"
IMAGE_NAME="${IMAGE_NAME:-death-star}"
OIDC_ISSUER="${OIDC_ISSUER:-https://token.actions.githubusercontent.com}"
REPO_REF="${REPO_REF:-refs/heads/main}"
SOURCE_REPO="${SOURCE_REPO:-endor-matt/death-star}"

SERVICES=(gateway weapons crew comms supply docking targeting lifesupport security-core)
DOCKERFILE_MAP=(
  "gateway:Dockerfile.gateway"
  "weapons:Dockerfile.weapons"
  "crew:Dockerfile.crew"
  "comms:Dockerfile.comms"
  "supply:Dockerfile.supply"
  "docking:Dockerfile.docking"
  "targeting:Dockerfile.targeting"
  "lifesupport:Dockerfile.lifesupport"
  "security-core:Dockerfile.security-core"
)

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { echo -e "${CYAN}[INFO]${RESET}  $*"; }
ok()    { echo -e "${GREEN}[OK]${RESET}    $*"; }
err()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
header(){ echo -e "\n${BOLD}── $* ──${RESET}\n"; }

usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --service <name>      Build and sign a specific service (${SERVICES[*]})"
  echo "  --image <ref>         Sign a pre-built image (registry/repo@sha256:...)"
  echo "  --verify-only <ref>   Verify an existing signature only"
  echo "  --jar <service>       Build and sign a service JAR (imperial-gateway|supply-chain)"
  echo "  --revoke <ref>        Revoke a signature"
  echo "  -h, --help            Show this help"
  exit 0
}

require_endorctl() {
  if ! command -v endorctl &>/dev/null; then
    info "endorctl not found, installing via npx..."
    npx -y endorctl --version
  fi
}

get_dockerfile() {
  local svc="$1"
  for entry in "${DOCKERFILE_MAP[@]}"; do
    local key="${entry%%:*}"
    local val="${entry#*:}"
    if [[ "$key" == "$svc" ]]; then
      echo "$val"
      return
    fi
  done
  err "Unknown service: $svc"
  exit 1
}

get_image_digest() {
  local image="$1"
  docker inspect --format='{{index .RepoDigests 0}}' "$image" 2>/dev/null \
    | cut -d@ -f2
}

sign_image() {
  local artifact="$1"
  header "Signing container image"
  info "Artifact: $artifact"

  endorctl artifact sign \
    --name "$artifact" \
    --source-repository-ref "$REPO_REF" \
    --source-repository "$SOURCE_REPO" \
    --source-repository-owner "$IMAGE_OWNER" \
    --certificate-oidc-issuer "$OIDC_ISSUER"

  ok "Image signed successfully"
}

verify_image() {
  local artifact="$1"
  header "Verifying artifact signature"
  info "Artifact: $artifact"

  endorctl artifact verify \
    --name "$artifact" \
    --certificate-oidc-issuer "$OIDC_ISSUER"

  ok "Signature verification passed"
}

revoke_signature() {
  local artifact="$1"
  header "Revoking artifact signature"
  info "Artifact: $artifact"

  endorctl artifact revoke-signature \
    --name "$artifact" \
    --source-repository-ref "$REPO_REF"

  ok "Signature revoked"
}

build_and_sign_service() {
  local svc="$1"
  local dockerfile
  dockerfile=$(get_dockerfile "$svc")

  header "Building $svc container"
  local tag="${REGISTRY}/${IMAGE_OWNER}/${IMAGE_NAME}/${svc}:latest"
  docker build -t "$tag" -f "infrastructure/docker/${dockerfile}" .
  info "Built: $tag"

  docker push "$tag"
  local digest
  digest=$(get_image_digest "$tag")
  local artifact="${REGISTRY}/${IMAGE_OWNER}/${IMAGE_NAME}/${svc}@${digest}"

  sign_image "$artifact"
  verify_image "$artifact"
}

build_and_sign_jar() {
  local svc="$1"
  header "Building $svc JAR"
  mvn -f "services/${svc}/pom.xml" clean package -DskipTests -q

  local jar_file
  jar_file=$(ls "services/${svc}/target/"*.jar | head -1)
  local jar_name
  jar_name=$(basename "$jar_file")
  local jar_sha
  jar_sha=$(sha256sum "$jar_file" | awk '{print $1}')
  local artifact="${jar_name}@sha256:${jar_sha}"

  info "JAR: $jar_name"
  info "SHA256: $jar_sha"

  header "Signing JAR artifact"
  endorctl artifact sign \
    --name "$artifact" \
    --source-repository-ref "$REPO_REF" \
    --source-repository "$SOURCE_REPO" \
    --source-repository-owner "$IMAGE_OWNER" \
    --certificate-oidc-issuer "$OIDC_ISSUER"

  ok "JAR signed: $artifact"

  header "Verifying JAR signature"
  endorctl artifact verify \
    --name "$artifact" \
    --certificate-oidc-issuer "$OIDC_ISSUER"

  ok "JAR signature verified"
}

# ── Main ──

require_endorctl

case "${1:-}" in
  -h|--help)
    usage
    ;;
  --service)
    [[ -z "${2:-}" ]] && { err "Missing service name"; exit 1; }
    build_and_sign_service "$2"
    ;;
  --image)
    [[ -z "${2:-}" ]] && { err "Missing image reference"; exit 1; }
    sign_image "$2"
    verify_image "$2"
    ;;
  --verify-only)
    [[ -z "${2:-}" ]] && { err "Missing artifact reference"; exit 1; }
    verify_image "$2"
    ;;
  --jar)
    [[ -z "${2:-}" ]] && { err "Missing service name"; exit 1; }
    build_and_sign_jar "$2"
    ;;
  --revoke)
    [[ -z "${2:-}" ]] && { err "Missing artifact reference"; exit 1; }
    revoke_signature "$2"
    ;;
  *)
    build_and_sign_service "gateway"
    ;;
esac
