FROM node:14-alpine

WORKDIR /app

COPY gui/package.json ./gui/
RUN cd gui && npm install --production

COPY . .

RUN apk add --no-cache python3 py3-pip

EXPOSE 3000

CMD ["node", "gui/server.js"]
