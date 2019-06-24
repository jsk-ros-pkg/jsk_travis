all: 12.04-base 14.04-pcl1.8 14.04-pcl 14.04-base 16.04-pcl 14.04-base 18.04-pcl 18.04-base

12.04-base: 12.04 Dockerfile.ros-ubuntu\:12.04-base
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

12.04: Dockerfile.ros-ubuntu\:12.04
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

14.04-pcl1.8: 14.04 Dockerfile.ros-ubuntu\:14.04-pcl1.8
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

14.04-pcl: 14.04 Dockerfile.ros-ubuntu\:14.04-pcl
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

14.04-base: 14.04 Dockerfile.ros-ubuntu\:14.04-base
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

14.04: Dockerfile.ros-ubuntu\:14.04
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

16.04-pcl: 16.04 Dockerfile.ros-ubuntu\:16.04-pcl
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

16.04-base: 16.04 Dockerfile.ros-ubuntu\:16.04-base
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

16.04: Dockerfile.ros-ubuntu\:16.04
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

18.04-pcl: 18.04 Dockerfile.ros-ubuntu\:18.04-pcl
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

18.04-base: 18.04 Dockerfile.ros-ubuntu\:18.04-base
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

18.04: Dockerfile.ros-ubuntu\:18.04
	echo "Building $@"
	docker build -t ros-ubuntu:$@ --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f Dockerfile.ros-ubuntu:$@ .

.PHONY: Dockerfile.ros-ubuntu\:12.04 Dockerfile.ros-ubuntu\:12.04-base \
        Dockerfile.ros-ubuntu\:14.04 Dockerfile.ros-ubuntu\:14.04-base Dockerfile.ros-ubuntu\:14.04-pcl Dockerfile.ros-ubuntu\:14.04-pcl1.8 \
        Dockerfile.ros-ubuntu\:16.04 Dockerfile.ros-ubuntu\:16.04-base Dockerfile.ros-ubuntu\:16.04-pcl \
        Dockerfile.ros-ubuntu\:18.04 Dockerfile.ros-ubuntu\:18.04-base Dockerfile.ros-ubuntu\:18.04-pcl
