FROM nginx:latest

# Update environment
RUN apt update && apt upgrade -y

# Add bash for boot cmd and vim
RUN apt-get install -y bash
RUN apt-get install -y vim

# Add nginx.conf to container
# COPY config/default.conf /etc/nginx/conf.d/default.conf
# COPY start.sh /app/start.sh

# set workdir
# WORKDIR /app/nginx

# CMD ["nginx", "-g", "'daemon off';"]
