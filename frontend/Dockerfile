FROM node:20
ARG REACT_APP_VERSION
ENV REACT_APP_VERSION=$REACT_APP_VERSION

WORKDIR /app


COPY package.json package-lock.json ./
RUN npm install


COPY . .

EXPOSE 3000

CMD [ "npm","start"]

