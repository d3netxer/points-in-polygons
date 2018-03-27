# Points-in-Polygons

This python app counts the number of points inside polygons. It uses shapely, including making use of the shapely vectorize module. This app is built using docker.

build the docker container:
```
$ sudo docker build -t points-in-polygons-image .

$ sudo docker run -it points-in-polygons-image
```

This link (https://blog.bekt.net/p/docker-aws-credentials/) suggested for development to configure the AWS creds and then mounting the ~/.aws directory AND set the $HOME environment variable. 

This command mounts the ~/.aws directory AND set the $HOME environment variable, mounts the code directory so that the changes are reflected live without having to rebuild the docker image, and opens the bash shell:

```
$ sudo docker run -it -e "HOME=/home" -v $HOME/.aws:/home/.aws -v /home/vagrant/repos/docker_python_practice:/opt points-in-polygons-image /bin/bash
```

