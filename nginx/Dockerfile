FROM nginx:latest

# Update environment
RUN apt-get update && apt-get upgrade -y

# Add bash for boot cmd and vim
RUN apt-get install -y bash
RUN apt-get install -y vim

# Add nginx.config to container
COPY nginx.conf /etc/nginx/nginx.conf

# Add default.conf to container
COPY default.conf /etc/nginx/conf.d/default.conf

# Add proxy_params.conf to container
COPY proxy_params.conf /etc/nginx/proxy_params.conf

# set workdir
#WORKDIR /etc/nginx
#
#CMD ["nginx", "-g", "daemon off;"]
