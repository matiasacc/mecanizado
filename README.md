# mecanizado

Tiempos de mecanizado y rugosidad (Ra / Rt) por consola. Python 3, solo biblioteca estándar.

```
python mecanizado.py
```

Operaciones: torneado (cilindrado, refrentado), fresado (planeado con placas, periférico) y taladrado.
Cada resultado muestra fórmula, valores reemplazados y fuente.

## Fuentes

- Groover, *Principles of Modern Manufacturing*, SI Version (WIE), 2016
  - Ec. 18.1–18.4 (torneado), 18.7–18.11 (taladrado), 18.13–18.20 (fresado)
  - Ec. 20.1, 20.2 y Fig. 20.2 (rugosidad ideal y real)
- Kalpakjian & Schmid, *Manufacturing Engineering and Technology*, 8ª ed. SI
  - Ec. 21.30 (Rt = f²/8R), sec. 33.3 (definición de Rt)

- Sandvik Coromant, catálogo *Turning tools*, Cutting data p. A278–A281
  - vc recomendada (escribir `?` en vc de torneado)

## Supuestos (marcados con * en la salida)

- Fig. 20.2 digitalizada (±0,02). Fuera de rango (≈9–137 m/min) se toma el valor del extremo.
- Rz objetivo: Rz = Rt del perfil ideal, sin corrección por material.
- Refrentado con n constante calculada en Do.
- Fresado periférico: sin fórmula de rugosidad en la bibliografía cargada.
