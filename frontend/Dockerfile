FROM node:20-alpine

WORKDIR /app

# Primero los manifiestos: así la capa de instalación solo se invalida cuando
# cambian las dependencias, no con cada cambio de código.
COPY package.json ./
RUN npm install

COPY . /app

EXPOSE 5173

# Tres pasos, en orden:
#   1. `npm install` solo si el volumen de node_modules vino vacío.
#   2. `svelte-kit sync` SIEMPRE: genera `.svelte-kit/tsconfig.json`, que
#      `tsconfig.json` extiende. Es un archivo derivado, no versionado, y sin
#      él Vite falla con "Cannot find base config file".
#   3. El servidor de desarrollo.
CMD ["sh", "-c", "[ -d node_modules/svelte ] || npm install; npx svelte-kit sync; npm run dev"]
