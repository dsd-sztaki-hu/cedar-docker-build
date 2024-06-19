FROM node:alpine

WORKDIR /app

COPY package.json package-lock.json /app/

RUN npm install

COPY . /app

# must be the same as the port in the vite.config.js
EXPOSE 5173

CMD ["npm", "start"]