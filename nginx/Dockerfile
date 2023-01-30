FROM nginx:latest

# Update environment
RUN apt update && apt upgrade -y

# Add bash for boot cmd and vim
RUN apt-get install -y bash
RUN apt-get install -y vim

# Add nginx.config to container
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Add nginx.conf to container
RUN rm /etc/nginx/conf.d/default.conf
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf
# COPY start.sh /etc/start.sh

# set workdir
WORKDIR /etc/nginx

CMD ["nginx", "-g", "daemon off;"]
