# Consola ShieldGuardAI

Interfaz Angular del prototipo de gestión de alertas de ShieldGuardAI.

## Desarrollo local

Con el backend Go activo en `http://localhost:8080`:

```sh
pnpm install
pnpm start
```

La consola de desarrollo se abre en `http://localhost:4200`. El servicio Angular usa HTTP y WebSocket para consultar las alertas y controlar el simulador.

## Compilar y verificar

```sh
pnpm build
pnpm test
```

`pnpm build` genera el paquete en `dist/frontend/browser`. Para servirlo con el backend unificado, copia esos archivos a `backend/static` desde la raíz del proyecto.

## Alcance de la interfaz

La consola muestra el score calculado por reglas, las señales que lo explican y acciones contra datos simulados. El valor es una señal heurística del prototipo, no una probabilidad de fraude ni una decisión bancaria.
