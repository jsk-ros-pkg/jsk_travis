DOCKER_BUILD_ARGS=--build-arg CACHEBUST=$(shell date +%Y%m%d)

all: 12.04-base 14.04-base 14.04-base 18.04-base 20.04-base \
     14.04-pcl 16.04-pcl 18.04-pcl 20.04-pcl \
     14.04-pcl1.8

12.04-base: 12.04 Dockerfile.ros-ubuntu\:12.04-base
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

12.04: Dockerfile.ros-ubuntu\:12.04
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

14.04-pcl1.8: 14.04 Dockerfile.ros-ubuntu\:14.04-pcl1.8
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

14.04-pcl: 14.04 Dockerfile.ros-ubuntu\:14.04-pcl
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

14.04-base: 14.04 Dockerfile.ros-ubuntu\:14.04-base
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

14.04: Dockerfile.ros-ubuntu\:14.04
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

16.04-pcl: 16.04 Dockerfile.ros-ubuntu\:16.04-pcl
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

16.04-base: 16.04 Dockerfile.ros-ubuntu\:16.04-base
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

16.04: Dockerfile.ros-ubuntu\:16.04
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

18.04-pcl: 18.04 Dockerfile.ros-ubuntu\:18.04-pcl
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

18.04-base: 18.04 Dockerfile.ros-ubuntu\:18.04-base
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

18.04: Dockerfile.ros-ubuntu\:18.04
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

20.04-pcl: 20.04 Dockerfile.ros-ubuntu\:20.04-pcl
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

20.04-base: 20.04 Dockerfile.ros-ubuntu\:20.04-base
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

20.04: Dockerfile.ros-ubuntu\:20.04
	echo "Building $@"
	DOCKER_BUILDKIT=1 docker build -t ros-ubuntu:$@ $(DOCKER_BUILD_ARGS) -f Dockerfile.ros-ubuntu:$@ .

.PHONY: Dockerfile.ros-ubuntu\:12.04 Dockerfile.ros-ubuntu\:12.04-base \
        Dockerfile.ros-ubuntu\:14.04 Dockerfile.ros-ubuntu\:14.04-base Dockerfile.ros-ubuntu\:14.04-pcl Dockerfile.ros-ubuntu\:14.04-pcl1.8 \
        Dockerfile.ros-ubuntu\:16.04 Dockerfile.ros-ubuntu\:16.04-base Dockerfile.ros-ubuntu\:16.04-pcl \
        Dockerfile.ros-ubuntu\:18.04 Dockerfile.ros-ubuntu\:18.04-base Dockerfile.ros-ubuntu\:18.04-pcl \
        Dockerfile.ros-ubuntu\:20.04 Dockerfile.ros-ubuntu\:20.04-base Dockerfile.ros-ubuntu\:20.04-pcl
