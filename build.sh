#!/bin/bash -e

for i in "$@"
do
case $i in
    --user=*)
    DOCKER_USER="${i#*=}"
    shift
    ;;
    --password=*)
    DOCKER_PASSWORD="${i#*=}"
    shift
    ;;
    --version=*)
    VERSION="${i#*=}"
    shift
    ;;
    *)
      # unknown option
    ;;
esac
done

echo "Logging into Docker..."
docker login -u $DOCKER_USER -p $DOCKER_PASSWORD

echo "Building Docker image for ${VERSION}..."
docker build -t smartthingsoss/container-release-common:$VERSION .

echo "Push Docker image..."
docker push smartthingsoss/container-release-common:$VERSION

