#!/bin/bash

# TaskNest Docker Build and Push Script
# This script builds Docker images and pushes them to a container registry

set -e

echo "=========================================="
echo "TaskNest Docker Build and Push"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="${DOCKER_REGISTRY:-your-registry}"
VERSION="${VERSION:-latest}"
API_IMAGE="${REGISTRY}/tasknest-api:${VERSION}"
WORKER_IMAGE="${REGISTRY}/tasknest-worker:${VERSION}"

echo "Registry: $REGISTRY"
echo "Version: $VERSION"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed and running${NC}"

# Function to build image
build_image() {
    local dockerfile=$1
    local image=$2
    local context=${3:-.}

    echo ""
    echo "Building $image..."
    docker build -f $dockerfile -t $image $context
    echo -e "${GREEN}✓ Built $image${NC}"
}

# Function to push image
push_image() {
    local image=$1

    echo ""
    echo "Pushing $image..."
    docker push $image
    echo -e "${GREEN}✓ Pushed $image${NC}"
}

# Function to tag image
tag_image() {
    local source=$1
    local target=$2

    echo "Tagging $source as $target..."
    docker tag $source $target
}

# Step 1: Build API image
echo ""
echo "Step 1: Building API image..."
build_image "Dockerfile.api" "$API_IMAGE" "."

# Step 2: Build Worker image
echo ""
echo "Step 2: Building Worker image..."
build_image "Dockerfile.worker" "$WORKER_IMAGE" "."

# Step 3: Tag images with additional tags
if [ "$VERSION" != "latest" ]; then
    echo ""
    echo "Step 3: Tagging images..."
    tag_image "$API_IMAGE" "${REGISTRY}/tasknest-api:latest"
    tag_image "$WORKER_IMAGE" "${REGISTRY}/tasknest-worker:latest"
fi

# Step 4: Login to registry
echo ""
echo "Step 4: Logging in to registry..."
read -p "Do you need to login to the registry? (yes/no): " need_login
if [ "$need_login" = "yes" ]; then
    docker login $REGISTRY
    echo -e "${GREEN}✓ Logged in to registry${NC}"
fi

# Step 5: Push images
echo ""
read -p "Push images to registry? (yes/no): " push_confirm
if [ "$push_confirm" = "yes" ]; then
    echo "Step 5: Pushing images..."
    push_image "$API_IMAGE"
    push_image "$WORKER_IMAGE"

    if [ "$VERSION" != "latest" ]; then
        push_image "${REGISTRY}/tasknest-api:latest"
        push_image "${REGISTRY}/tasknest-worker:latest"
    fi

    echo ""
    echo -e "${GREEN}✓ All images pushed successfully!${NC}"
else
    echo -e "${YELLOW}⚠ Skipping push - images built locally only${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Build Summary"
echo "=========================================="
echo "API Image: $API_IMAGE"
echo "Worker Image: $WORKER_IMAGE"
echo ""
echo "To test locally:"
echo "  docker-compose up"
echo ""
echo "To deploy to Kubernetes:"
echo "  Update k8s/*.yaml with the correct image names"
echo "  Run: ./scripts/deploy.sh"
