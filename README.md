# Points-in-Polygons

Tested with Ubuntu 16.04.

## Dependencies

### Install Docker CE for Ubuntu:
https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce-1

### Install AWS CLI:
#### Install PIP: ```sudo apt install python-pip```
#### Install AWS CLI: ```pip install awscli --upgrade --user```

This python app counts the number of points inside polygons. It uses shapely, including making use of the shapely vectorize module. This app is built using docker.

build the docker container:
```
$ sudo docker build -t points-in-polygons-image .
```

This link (https://blog.bekt.net/p/docker-aws-credentials/) suggested for development to configure the AWS creds and then mounting the ~/.aws directory AND set the $HOME environment variable. 

This command mounts the ~/.aws directory AND set the $HOME environment variable, mounts the code directory so that the changes are reflected live without having to rebuild the docker image, and opens the bash shell:

```
$ sudo docker run -it -e "HOME=/home" -v $HOME/.aws:/home/.aws -v /home/vagrant/repos/docker_python_practice:/opt points-in-polygons-image /bin/bash
```

