# Guía de Evaluación Rápida — ShieldGuard AI 🛡️
> **Para uso de Comités Evaluadores, Jurados de Emprendimiento (Corfo / Concursos) y Docencia.**  
> *Prueba interactiva del prototipo sin necesidad de instalar entornos de desarrollo (sin Node.js, Go ni Python).*

---

## 1. Resumen del Proyecto

**ShieldGuard AI** es un prototipo educativo para explorar señales de riesgo en transacciones simuladas y una hipótesis de apoyo a la revisión de reclamos por operaciones no autorizadas. La **Ley 20.009** regula responsabilidades y procedimientos de cancelación de cargos o restitución de fondos bajo condiciones y plazos legales; este prototipo no determina si hubo fraude, no atribuye responsabilidad y no reemplaza esos procedimientos.

* **Alcance de la demo:** las reglas deterministas evalúan transacciones ficticias y permiten cambiar y revertir el estado local de una tarjeta desde la consola. El servicio CatBoost es opcional y solo entrega una señal experimental en sombra. No se conecta a bancos, no autoriza ni rechaza pagos reales y no se ha validado con datos transaccionales reales.

---

## 2. Requisitos del Sistema

* **Sistema Operativo:** Windows 10 o Windows 11 (64-bit).
* **Navegador Web:** Chrome, Edge, Firefox, Brave o cualquier navegador moderno.
* **Instalación requerida:** **NINGUNA** si se distribuye el paquete precompilado completo. El ZIP debe contener `start_demo.bat`, `backend/shieldguard-backend.exe` y `backend/static/` con `index.html`, JavaScript, estilos y favicon. El frontend es servido desde esa carpeta; no está embebido dentro del ejecutable.

---

## 3. Instrucciones de Inicio Rápido

1. **Descarga y descompresión:**
   * Cuando se publique un paquete `.zip` de evaluación en *GitHub Releases*, extráelo en una carpeta de tu preferencia. Confirma que incluya el ejecutable y la carpeta `backend/static/`.
2. **Ejecución:**
   * Haz doble clic en el archivo:
     ```text
     start_demo.bat
     ```
3. **Acceso a la consola:**
   * Se abrirá la consola del servidor y el navegador predeterminado en:
     ```text
     http://localhost:8080
     ```
   * Verás la **Risk Console** (consola de analista de riesgo y ciberseguridad financiera) con el estado **`EN VIVO`** en verde.

---

## 4. Guía de Evaluación Interactiva (Paso a Paso)

Sigue este recorrido para verificar todas las capacidades operativas del sistema:

### Paso 1: Consola de monitoreo de la demo
* Observa el encabezado superior con las métricas globales:
  * **Total Procesado:** Transacciones analizadas continuamente.
  * **Pérdida Evitada:** contador demostrativo que suma el monto de alertas pendientes al cambiar su estado a congelado. No es una pérdida real verificada ni un ahorro atribuido a la Ley 20.009.
  * **Latencia Promedio:** el prototipo muestra un valor fijo de 1,42 ms; no mide la latencia real ni constituye garantía de rendimiento. Con ML habilitado, la consulta en sombra puede esperar hasta 110 ms antes de continuar con las reglas.
* En el panel lateral derecho verás el **feed continuo de transacciones** cotidianas simuladas (Supermercados Lider, Copec, Jumbo, Starbucks).

---

### Paso 2: Inyección de un escenario simulado
En la parte inferior de la consola encontrarás botones de pruebas para simular ataques habituales:

1. En la sección **Probar escenarios**, haz clic en:
   ```text
   [ Compra electrónica · $230.000 ]
   ```
2. **Resultado esperado con el perfil inicial:** aparecerá una alerta para **`•••• 4821`** con un score de reglas de **94/100**. Es un puntaje heurístico, no una probabilidad; puede variar si el perfil local persistido cambió.
3. **Señales de las reglas:** selecciona la alerta para revisar las señales registradas:
   * *Monto excede en 6.6x el promedio histórico del cliente ($35.000 CLP).*
   * *Compra eCommerce no presencial de alto valor.*
   * *Comercio en categoría sensible (MCC 5732: MercadoLibre Chile - Smart TV).*

---

### Paso 3: Congelamiento simulado
1. Con la alerta seleccionada, presiona:
   ```text
   [ Congelar tarjeta ]
   ```
2. **Resultado verificable:**
   * El estado de la tarjeta pasa de `PENDIENTE` a **`CONGELADO_PREVENTIVO`**.
   * El contador demostrativo aumenta por el monto de cada alerta pendiente de esa tarjeta que pasa a congelada; con una sola alerta de $230.000, aumenta en **`+$230.000 CLP`**.
   * Las evaluaciones posteriores de esa tarjeta en el motor local devuelven score 100. Esto no bloquea compras reales ni envía una orden a una red bancaria.

---

### Paso 4: Reversión del estado simulado
1. En la alerta congelada, haz clic en:
   ```text
   [ Revertir congelamiento ]
   ```
2. **Resultado verificable:**
   * El estado local de la tarjeta vuelve a no congelado.
   * El sistema incrementa **Ciclo Autopoiético** (`autopoiesisCycle`), que es solo un contador de demo: no reentrena CatBoost ni ajusta umbrales automáticamente.

---

### Paso 5: Comprobación de persistencia local tras reinicio
1. Cierra la ventana negra de la terminal de Windows para detener el sistema.
2. Vuelve a ejecutar `start_demo.bat`.
3. **Resultado esperado:** si el snapshot se guardó y sigue en su ubicación, el backend recupera contadores, perfiles, alertas y estados locales desde `backend/data/shieldguard-state.json`. El guardado usa un archivo temporal y `rename`; esta demo no ofrece garantías de durabilidad ante cualquier fallo de sistema ni sustituye una base de datos con respaldos.

---

## 5. Preguntas Frecuentes y Soporte para Evaluadores

* **¿Aviso de Windows SmartScreen al abrir el `.bat`?**  
  Al ser un binario compilado localmente sin firma comercial adquirida, Windows puede mostrar la pantalla azul protectora. Haz clic en *"Más información"* y luego en *"Ejecutar de todas formas"*.
* **¿El puerto 8080 está ocupado por otra aplicación?**  
  Puedes definir otra dirección en una terminal antes de arrancar:
  ```powershell
  $env:SHIELDGUARD_ADDR = ":8085"
  .\shieldguard-backend.exe
  ```
  Y abrir `http://localhost:8085` en tu navegador.
* **¿Dónde consultar los detalles de la arquitectura y la postulación Corfo?**
  * Arquitectura técnica y modelo ML: [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md)
  * Diagnóstico de fondos Start-Up Chile Build 13: [`docs/CORFO-CONVOCATORIAS.md`](docs/CORFO-CONVOCATORIAS.md)
  * Presentación ejecutiva: `ShieldGuard_AI_Presentacion_Ejecutiva.pptx`
