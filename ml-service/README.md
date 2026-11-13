# ShieldGuardAI ML service

Servicio privado opcional de inferencia CatBoost y pipeline de entrenamiento temporal. El primer modelo de demo usa etiquetas sintéticas; su score es exploratorio y no puede interpretarse como probabilidad real de fraude.

## Preparar el entorno

```powershell
cd ml-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Entrenar la demo reproducible

```powershell
python generate_demo_data.py
python train.py --scope synthetic
python service.py
```

El generador produce transacciones ficticias con una etiqueta dependiente de variables observables. Para ver el progreso por iteración se puede ejecutar `python train.py --scope synthetic --verbose`. El dataset y los artefactos se crean localmente y no se incluyen en Git.

El entrenamiento ordena las filas por `timestamp`, usa el primer 80% para ajustar y el último 20% como `eval_set` de CatBoost para early stopping. Luego calcula Average Precision y métricas a umbral 0,5 sobre ese mismo 20%. Por reutilizarse para detener el entrenamiento y reportar resultados, esa partición **no es un test independiente**: las métricas son diagnósticos del pipeline, no una estimación imparcial de generalización. Además, `average_precision()` es una implementación propia por ranking que no agrupa scores empatados como hace el cálculo estándar por umbrales; en datasets con muchos empates puede variar según el orden de filas. Antes de comunicar métricas, reemplazarla o contrastarla con una implementación estándar y separar cronológicamente entrenamiento, validación (early stopping) y test final, reservando este último sin usarlo para seleccionar iteraciones.

## Contrato para datos etiquetados autorizados

El CSV debe incluir `timestamp`, las variables `amount_clp`, `amount_vs_baseline`, `tx_count_card`, `minutes_since_last_tx`, `channel`, `mcc`, `city_changed` y una columna `label_fraud` adjudicada. `IsSuspicious` del simulador no se usa. No cargar PAN, CVV, nombres ni otros identificadores directos. `--scope approved_labeled` solo escribe esa etiqueta de alcance en los metadatos: el programa no verifica autorización, procedencia, anonimización ni calidad de adjudicación. La etiqueta no constituye evidencia de aprobación; úsala únicamente después de validar esos aspectos fuera del código.

```powershell
python train.py --data .\data\approved_transactions.csv --scope approved_labeled
```

## Endpoints

- `GET /health`
- `GET /internal/v1/model-info`
- `POST /internal/v1/predict` con `{ "features": { ... } }`

El servidor enlaza a `127.0.0.1:8090` por defecto y no implementa autenticación; es una frontera local de prototipo, no una configuración de producción. Go consulta el servicio solo si se configura `SHIELDGUARD_ML_URL`. Si el artefacto no existe o falla la inferencia, la demo conserva su evaluación por reglas y omite la señal ML.

## Limitaciones

- Un modelo entrenado con datos sintéticos solo demuestra el flujo entrenamiento→evaluación→inferencia.
- `experimentalScore` no está calibrado; no representa probabilidad bancaria.
- `reasonCodes` son reglas legibles de señales, no explicaciones causales ni SHAP.
- No hay reentrenamiento en línea, conexión bancaria ni bloqueo automático.
