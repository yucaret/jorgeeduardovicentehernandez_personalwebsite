FROM node:14

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY package*.json .

RUN npm install

RUN npm install express

COPY . .

EXPOSE 3000

CMD ["node", "src/index.js"]