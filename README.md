# ShieldGuardAI - Mauricio Muñoz

Prototipo demostrativo de una consola para revisar transacciones simuladas, explicar señales de riesgo y probar acciones de congelamiento reversible.

> **Alcance:** esta carpeta contiene un MVP educativo. El motor operativo usa reglas y ponderaciones deterministas. Incluye un servicio CatBoost experimental opcional, entrenable con datos sintéticos, que solo entrega una señal en sombra. No hay conexión bancaria ni validación con datos reales. Nada aquí debe usarse para tomar decisiones financieras.

## Qué incluye

- **Backend:** servidor Go que expone una API HTTP, transmite eventos por WebSocket y sirve el frontend compilado.
- **Motor de riesgo:** reglas heurísticas de monto, canal, MCC y ubicación. Conserva un promedio histórico simple para transacciones normales.
- **Modelo ML experimental opcional:** servicio privado Python/CatBoost con pipeline de generación sintética, entrenamiento temporal e inferencia en sombra. No modifica la decisión del motor de reglas y requiere entrenar un artefacto local. Consulta la [guía del servicio ML](ml-service/README.md).
- **Persistencia local:** snapshots JSON en `backend/data/shieldguard-state.json` para recuperar perfiles, alertas, últimas 100 transacciones, contadores, congelaciones y estado del simulador después de reiniciar.
- **Simulador:** genera transacciones normales y permite inyectar tres escenarios de prueba desde la consola.
- **Frontend:** consola Angular con alertas priorizadas por tarjeta, detalle de señales, congelamiento/reversa y controles del simulador.
- **Material de presentación:** `ShieldGuard_AI_Presentacion_Ejecutiva.pptx` y su generador `generate_deck.py`.
- **Referencia separada:** `references/cardflow-playground` es otro proyecto Go; no se compila ni ejecuta como parte de este MVP.

## Arquitectura y ruta de emprendimiento

- [Arquitectura actual y propuesta con CatBoost](docs/ARQUITECTURA.md).
- [Análisis de convocatorias Corfo vigentes al 13 de noviembre de 2026](docs/CORFO-CONVOCATORIAS.md).
- [Guía de ejecución para evaluadores sin instalación previa](RELEASE.md).

La arquitectura documenta qué está implementado y qué sigue planificado: el pipeline de entrenamiento e inferencia CatBoost está disponible para experimentación; no hay etiquetas bancarias confirmadas, integración bancaria, autenticación productiva o bloqueo real.

## Requisitos para desarrollo

- Go **1.26.5 o superior**, de acuerdo con la directiva `go` de `backend/go.mod`.
- Una versión de Node.js compatible con Angular CLI 18.2 y pnpm para compilar o ejecutar el frontend. Se recomienda pnpm porque el proyecto versiona `pnpm-lock.yaml`.
- Python 3.10+ solo si se desea ejecutar el microservicio experimental de ML.

> [!TIP]
> **¿Eres un evaluador, profesor o jurado?**  
> No necesitas instalar Go, Node.js ni Python si recibes el paquete precompilado de evaluación. Consulta [RELEASE.md](RELEASE.md); el ZIP debe incluir el lanzador, el binario Go y `backend/static/`.

## Ejecutar la demo en Windows

La opción más simple sirve el frontend compilado y la API en `http://localhost:8080`:

```bat
start_demo.bat
```

El script usa `backend/shieldguard-backend.exe` y el backend sirve los archivos de `backend/static/`. Ambos deben estar presentes. Si editas el código, vuelve a compilar el frontend, copiar sus archivos a `backend/static/` y compilar el backend antes de abrir esta opción.

Para ejecutar desde el código fuente y usar la recarga de Angular:

```powershell
# Terminal 1
cd backend
go run ./cmd/server

# Terminal 2
cd frontend
pnpm install --frozen-lockfile
pnpm start
```

Abre `http://localhost:4200`. El frontend de desarrollo se conecta al backend en el puerto `8080`.

## Entrenar y ejecutar el modelo ML experimental

El servicio ML es opcional. Sin `SHIELDGUARD_ML_URL`, la demo usa únicamente las reglas actuales. La señal CatBoost aparece en el detalle de alertas cuando el servicio responde, pero no cambia el nivel ni la acción operativa.

```powershell
# Terminal 1: preparar entorno, crear datos ficticios y entrenar
cd ml-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_demo_data.py
python train.py --scope synthetic

# Terminal 2: iniciar el modelo en localhost:8090
cd ml-service
.\.venv\Scripts\Activate.ps1
python service.py

# Terminal 3: iniciar el backend con puntuación en sombra
cd backend
$env:SHIELDGUARD_ML_URL = "http://127.0.0.1:8090"
go run ./cmd/server
```

Los datos generados y artefactos se guardan localmente bajo `ml-service/data` y `ml-service/artifacts`; no se deben subir. El entrenamiento ordena por fecha y tiene una opción `--verbose`, pero usa la partición final tanto para early stopping como para las métricas: esos resultados no son una evaluación independiente. Su función de Average Precision también requiere validación de empates antes de usarla en reportes. Además, el modelo de demostración se entrena con etiquetas sintéticas que dependen de sus variables, así que sus scores solo prueban el pipeline y **no son probabilidades ni evidencia de rendimiento antifraude real**. Para detalles del CSV, alcance y limitaciones de evaluación, consulta [ml-service/README.md](ml-service/README.md).

## Guía paso a paso para compilar desde el código fuente

El backend se compila como un binario Go que sirve la API, los WebSockets y los archivos estáticos del frontend. El frontend **no está embebido** en el binario: para ejecutar la demo se necesita también la carpeta `backend/static/` junto al ejecutable.

### 1. Compilar el Frontend (Angular 18)
```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm build
```
Los archivos estáticos generados se guardarán en `frontend/dist/frontend/browser/`.

### 2. Trasladar estáticos al directorio del Backend
Para que el servidor Go los sirva automáticamente:

**En Windows (PowerShell):**
```powershell
cd ../backend
if (!(Test-Path static)) { New-Item -ItemType Directory -Path static }
Remove-Item static\* -Recurse -Force
Copy-Item -Path "..\frontend\dist\frontend\browser\*" -Destination ".\static\" -Recurse -Force
```

**En Linux / macOS / WSL (Bash):**
```bash
cd ../backend
mkdir -p static
rm -rf static/*
cp -r ../frontend/dist/frontend/browser/* ./static/
```

### 3. Compilar el Backend unificado (Go)
```powershell
# En Windows (genera shieldguard-backend.exe):
go build -o shieldguard-backend.exe ./cmd/server

# En Linux / macOS (genera binario ejecutable):
go build -o shieldguard-backend ./cmd/server
```

### 4. Ejecución del binario resultante
```powershell
# En Windows:
.\shieldguard-backend.exe

# En Linux / macOS:
./shieldguard-backend
```
Abre tu navegador en `http://localhost:8080`. En tiempo de ejecución basta el backend y `static/`; Node.js solo se necesita para compilar el frontend.

## Funcionalidades de la consola

1. **Alertas:** presenta la alerta más reciente por tarjeta y ordena las tarjetas por score. El backend conserva hasta 20 alertas para esta demo.
2. **Detalle:** muestra monto, comercio, score y reglas que contribuyeron a la señal.
3. **Congelar y revertir (simulado):** actualiza el estado local de una tarjeta y retransmite el cambio a la interfaz. No envía instrucciones a un emisor o red de pagos.
4. **Pruebas de escenario:** inyecta una compra de electrónica, una compra desde otra ubicación o una compra de juego.
5. **Flujo simulado:** permite pausar o reanudar la generación automática de transacciones.

El score operativo no es una probabilidad calibrada. Los valores dependen de las reglas y del perfil; no se garantiza que coincidan con cifras de versiones anteriores del pitch. Si se habilita CatBoost, su resultado se conserva como señal experimental en sombra y no se mezcla con las reglas ni con las acciones. El backend guarda un snapshot local después de cada evaluación de transacción y acción sobre tarjetas. Si el archivo no existe, inicia con los perfiles de demostración; si existe pero está dañado o usa una versión desconocida, el servidor se detiene para evitar reemplazar los datos silenciosamente.

El directorio de datos se crea automáticamente dentro de `backend/data`. Puedes cambiar el archivo con la variable `SHIELDGUARD_DATA` (ruta absoluta o relativa al directorio de ejecución del backend). Haz copias de seguridad con el backend detenido. Esta persistencia JSON es adecuada para una demo de una sola instancia; no es una base de datos multiusuario ni está pensada para altas tasas de escritura. Para operar con instituciones y datos reales, se debe migrar a una base transaccional con controles de acceso, copias de seguridad y retención definidos.

## API de demostración

- `GET /api/health`: estado del servicio.
- `GET /api/alerts`: alertas de la sesión.
- `GET /api/stats`: métricas simuladas.
- `GET /api/simulator/status`: indica si el flujo está activo.
- `POST /api/cards/freeze`: congela una tarjeta.
- `POST /api/cards/unfreeze`: revierte el congelamiento.
- `POST /api/simulator/toggle`: pausa o reanuda el flujo.
- `POST /api/simulator/inject`: inyecta un escenario. Recibe `{"scenario":"AUTOFRAUDE_RETAIL"}`, `SIMULTANEO_ATM` o `MICRO_BURST`.
- `ws://localhost:8080/ws`: eventos de transacciones, alertas y métricas.

## Verificaciones

```powershell
cd backend
go test ./...
go vet ./...

cd ../frontend
pnpm build
```

`pnpm test` está configurado, pero actualmente falla porque no hay archivos `*.spec.ts` en `frontend/src` (`TS18003: No inputs were found`). El build de Angular sí se puede compilar. Los paquetes Go que aún no tienen pruebas se indican como `[no test files]`.

## Límites de seguridad

El servidor de demo no implementa autenticación ni autorización bancaria y permite solicitudes de origen cruzado. El proceso escucha en `:8080`, que puede exponerlo en otras interfaces del equipo. Úsalo solo en un entorno local controlado, con datos ficticios; no lo publiques en una red ni lo conectes a tarjetas reales.

Puedes cambiar el puerto de escucha para pruebas locales definiendo `SHIELDGUARD_ADDR` antes de arrancar el backend (por ejemplo, `127.0.0.1:8081`). El frontend unificado usa su mismo origen; `ng serve` en el puerto `4200` se conecta al backend de `8080`.

Antes de presentar o distribuir el pitch, confirma con el equipo que el nombre de la institución, el año académico y las referencias normativas coincidan entre este README y la presentación.
