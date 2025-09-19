#!/bin/bash

# Help function
usage() {
    echo "Usage: $0 -u <github_username> -r <repository_name> -t <tag> [-h]"
    echo "  -u: GitHub username"
    echo "  -r: Repository name"
    echo "  -t: Image tag (default: latest)"
    echo "  -h: Show this help message"
    exit 1
}

# Error handling function
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Default values
TAG="latest"

# Parse arguments
while getopts "u:r:t:h" opt; do
    case ${opt} in
        u )
            GITHUB_USERNAME=$OPTARG
            ;;
        r )
            REPOSITORY_NAME=$OPTARG
            ;;
        t )
            TAG=$OPTARG
            ;;
        h )
            usage
            ;;
        \? )
            echo "Invalid option: $OPTARG" 1>&2
            usage
            ;;
    esac
done

# Check required arguments
if [[ -z "$GITHUB_USERNAME" || -z "$REPOSITORY_NAME" ]]; then
    handle_error "GitHub username and repository name are required"
fi

# Verify CR_PAT is set
if [[ -z "$CR_PAT" ]]; then
    handle_error "CR_PAT environment variable is not set. Please export your GitHub Container Registry token as CR_PAT."
fi

# Login to GitHub Container Registry
echo "$CR_PAT" | docker login ghcr.io -u msanyam --password-stdin || handle_error "Docker login to ghcr.io failed"


# Build Docker image for linux/amd64 platform
echo "Building Docker image for linux/amd64..."
docker buildx build --platform linux/amd64 -t "$REPOSITORY_NAME" . || handle_error "Docker build failed"

# Tag and push the image with platform
FULL_IMAGE_PATH="ghcr.io/$GITHUB_USERNAME/$REPOSITORY_NAME:$TAG"
echo "Pushing image to GitHub Container Registry..."
docker buildx build --platform linux/amd64 -t "$FULL_IMAGE_PATH" . --push || handle_error "Docker build and push failed"

echo "Docker image successfully pushed to $FULL_IMAGE_PATH"