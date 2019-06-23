all: 14.04-pcl1.8 14.04-pcl 16.04-pcl 18.04-pcl

14.04-pcl1.8: 14.04 Dockerfile.ros-ubuntu\:14.04-pcl1.8
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .

14.04-pcl: 14.04 Dockerfile.ros-ubuntu\:14.04-pcl
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .

14.04: Dockerfile.ros-ubuntu\:14.04
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .

16.04-pcl: 16.04 Dockerfile.ros-ubuntu\:16.04-pcl
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .

16.04: Dockerfile.ros-ubuntu\:16.04
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .

18.04-pcl: 18.04 Dockerfile.ros-ubuntu\:18.04-pcl
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .

18.04: Dockerfile.ros-ubuntu\:18.04
	docker build -t ros-ubuntu:$@ -f Dockerfile.ros-ubuntu:$@ .
