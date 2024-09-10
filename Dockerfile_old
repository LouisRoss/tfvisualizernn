FROM node:22

LABEL version="1.0"
LABEL description="Node-based web page for visualizing Tensorflow Spiking Neural Network models."
LABEL maintainer = "Louis Ross <louis.ross@gmail.com"

WORKDIR /app

#COPY ["./package.json", "./package-lock.json", "/app/"]
COPY ["./package.json", "/app/"]

RUN ls
RUN ["npm", "install", "-g", "npm@10.8.3"]
#RUN npm install --production
RUN ["npm", "install"]


COPY . .

EXPOSE 3000

CMD ["npm", "start"]
