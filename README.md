# points-in-polygons

Tested with Ubuntu 16.04. This app is built using docker.

## Dependencies

### Install Docker CE for Ubuntu:
https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce-1

### Install AWS CLI:
#### Install PIP: ```sudo apt install python-pip```
#### Install AWS CLI: ```pip install awscli --upgrade --user```

This python app counts the number of points inside polygons. It uses shapely and makes use of the shapely vectorize module. 

build the docker container:
```
$ sudo docker build -t points-in-polygons-image .
```

This link (https://blog.bekt.net/p/docker-aws-credentials/) suggested for development to configure the AWS creds and then mounting the ~/.aws directory AND set the $HOME environment variable. 

This example command mounts the ~/.aws directory AND set the $HOME environment variable, mounts the code directory so that the changes are reflected live without having to rebuild the docker image, and opens the bash shell:

```
$ sudo docker run -it -e "HOME=/home" -v $HOME/.aws:/home/.aws -v "$PWD:/opt" points-in-polygons-image /bin/bash
```

now once you are inside the docker container you can run the script manually:
```
$python pointsinpolygons.py
```

### Configuration

The intent is to creat a cronjob that will run the docker run command evertime the ec2 instance reboots or starts-up. 

I had difficulty getting crontab to work running docker with sudo. Therefore I had to add the default ubuntu user to the docker group:



Edit your crontab file with this command:   ```crontab -e```

and add this line to itL
```
@reboot sh /opt/points-in-polygons/startup_script.sh
```

It will reference the startup_script.sh in this repo. The startup script runs docker in the background and will write the output file in the data directory.


### metrics
Processed over 2 million points in all worldwide country polygons in 237 seconds on a t2.medium instance.
