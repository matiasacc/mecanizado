# mecanizado

Tiempos de mecanizado y rugosidad (Ra / Rt) por consola. Python 3, solo biblioteca estándar.

```
python mecanizado.py
```

Operaciones: torneado (cilindrado, refrentado), fresado (planeado con placas, periférico) y taladrado.
Cada resultado muestra fórmula, valores reemplazados y fuente.

## Ejemplo

Cilindrado de Ø50 a Ø40 × 100 mm en acero 01.2 (C 0,25–0,55 %), desbaste con CNMG120408-PM, acabado con CNMG120408-PF a Ra 1,6 µm y vc propia de 280 m/min.

```
C:\Users\matias\mecanizado> python mecanizado.py
MECANIZADO - tiempos y rugosidad   19/11/2026

------------------------------------------------------------
  1) Torneado - cilindrado
  2) Torneado - refrentado
  3) Fresado - planeado con placas
  4) Fresado periférico
  5) Taladrado
  r) Resumen    g) Guardar .txt    q) Salir
  > 1

════ TORNEADO - CILINDRADO ═══════════════════════════════════
  Diámetro inicial Do [mm] [50]: 50
  Diámetro final Df [mm] [46.0]: 40
  Longitud de corte L [mm] [100]: 100
  Recorrido en vacío, entrada + salida [mm] [0]: 2
  n máx. de la máquina [rpm] (Enter = sin límite): 3000
  Sobrematerial de acabado, radial [mm] (0 = todo en una pasada) [0.5]: 0.5

  -- Desbaste --
    ej.: CNMG120408-PM   (Enter = sin placa)
  Placa de desbaste (ISO con geometría): CNMG120408-PM
  -> CNMG120408-PM: ap rec 3 (0.5-5.5) mm | fn rec 0.3 (0.15-0.5) mm/rev  [Sandvik, pág. PDF 287]
  ap máx por pasada [mm] [3.0]: 
  Avance de desbaste f [mm/rev] [0.3]: 
    ej.: 180          vc directa [m/min]
          01.2         vc de la tabla Sandvik (pregunta el avance)
          01.2 250     vc propia, el código queda como referencia
          ?            ver tabla de vc
  vc desbaste [m/min] [200]  (? = lista): 01.2
  01.2 No aleado C 0,25-0,55 %   150 HB:  1) fn 0,1 -> 455   2) fn 0,4 -> 305   3) fn 0,8 -> 215
  Avance de referencia [2]: 2
  -> vc = 305 m/min

  ┌─ DESBASTE: 4.5 mm radiales en 2 pasada(s) de ap = 2.250 mm ────────────────────┐
  │ vc = 305 m/min    [Sandvik p. A278-A281: 01.2, GC4325, fn 0,4 mm/rev]          │
  │ Placa CNMG120408-PM: ap 0.5-5.5 mm, fn 0.15-0.5 mm/rev  [Sandvik pág. PDF 287] │
  │ Df pasada     = D − 2·ap                                                       │
  │               = 50 − 2·2.250                                                   │
  │               = 45.500 mm    [Groover SI 2016, Ec. 18.2]                       │
  │ n             = 1000·vc / (π·D)                                                │
  │               = 1000·305 / (π·50)                                              │
  │               = 1942 rpm    [Groover SI 2016, Ec. 18.1]                        │
  │ n se recalcula en el diámetro de cada pasada (Ec. 18.1 con D de la pasada).    │
  └────────────────────────────────────────────────────────────────────────────────┘

  -- Acabado --
    ej.: 180          vc directa [m/min]
          01.2         vc de la tabla Sandvik (pregunta el avance)
          01.2 250     vc propia, el código queda como referencia
          ?            ver tabla de vc
  vc acabado [m/min] [200]  (? = lista): 01.2 280
  -> vc = 280 m/min  (tabla para 01.2: 455-305-215)

  ┌─ ACABADO: ap = 0.500 mm, de Ø41.000 a Ø40 ──────────────────────────────────────────────┐
  │ vc = 280 m/min (valor propio)    [ref. Sandvik p. A278-A281: 01.2, GC4325: 455-305-215] │
  │ n             = 1000·vc / (π·D)                                                         │
  │               = 1000·280 / (π·41)                                                       │
  │               = 2174 rpm    [Groover SI 2016, Ec. 18.1]                                 │
  └─────────────────────────────────────────────────────────────────────────────────────────┘

  -- Rugosidad --
    ej.: 0.8             radio en mm
          CNMG120408      designación ISO (toma el 08 -> 0,8 mm)
          CNMG120408-PF   con geometría: además muestra ap y fn de Sandvik
          ?               ver códigos de radio
  Radio de punta rε [mm] [0.8]  (? = lista): CNMG120408-PF
  -> CNMG 12 04 08: RE = 0.8 mm
  -> CNMG120408-PF: ap rec 0.4 (0.3-1.5) mm | fn rec 0.2 (0.1-0.4) mm/rev  [Sandvik, pág. PDF 287]
    1) Metales dúctiles (aceros, Al, Cu...)
    2) Fundiciones
    3) Aleaciones de fácil mecanizado
  Material [1]: 1
    1) Ra objetivo [µm]
    2) Rz objetivo [µm] *
    3) Tengo el avance f
  Dato [1]: 1
  Ra objetivo [µm] [1.6]: 1.6

  ┌─ RUGOSIDAD ───────────────────────────────────────────────────────────────────┐
  │ r_ai          Fig. 20.2                                                       │
  │               = ductil, vc = 280 m/min                                        │
  │               = 1.07    [Groover SI 2016, Fig. 20.2]                          │
  │ f máx         = √(32·rε·Ra/(r_ai·1000))                                       │
  │               = √(32·0.8·1.6/(1.07·1000))                                     │
  │               = 0.196 mm/rev    [Groover SI 2016, Ec. 20.1 y 20.2 despejadas] │
  │ Placa CNMG120408-PF: fn rec 0.2, rango 0.1-0.4 mm/rev [Sandvik pág. PDF 287]  │
  │ Ri (ideal)    = f² / (32·rε)                                                  │
  │               = 0.196² / (32·0.8)                                             │
  │               = 1.50 µm    [Groover SI 2016, Ec. 20.1]                        │
  │ Ra (estim.)   = r_ai · Ri                                                     │
  │               = 1.07 · 1.50                                                   │
  │               = 1.60 µm    [Groover SI 2016, Ec. 20.2]                        │
  │ Rt (ideal)    = f² / (8·rε)                                                   │
  │               = 0.196² / (8·0.8)                                              │
  │               = 5.98 µm    [Kalpakjian 8a SI, Ec. 21.30]                      │
  │ * vc fuera del rango de la Fig. 20.2 -> r_ai del extremo (1.07).              │
  │ Límites: herramienta afilada; solo el radio genera la superficie; sin         │
  │ vibración, BUE ni desgaste (Groover 20.2). Rt ideal no corrige por material.  │
  └───────────────────────────────────────────────────────────────────────────────┘

  ┌─ TIEMPO (acabado) ────────────────────────────────────────────────┐
  │ fr            = n · f                                             │
  │               = 2174 · 0.196                                      │
  │               = 425.3 mm/min    [Groover SI 2016, Ec. 18.3]       │
  │ Tm            = (L + a) / fr                                      │
  │               = (100 + 2) / 425.3                                 │
  │               = 0.240 min = 14.4 s    [Groover SI 2016, Ec. 18.4] │
  └───────────────────────────────────────────────────────────────────┘

  ┌─ PASADAS ────────────────────────────────────────────────────────────────────┐
  │  #  tipo       Ø antes     ap      n      f      fr   Tm [s]                 │
  │  1  desbaste     50.00   2.25   1942  0.300   582.5     10.5                 │
  │  2  desbaste     45.50   2.25   2134  0.300   640.1      9.6                 │
  │  3  acabado      41.00   0.50   2174  0.196   425.3     14.4                 │
  │ Total                                      0.574 min = 34.5 s                │
  │ n calculada con el diámetro antes de cada pasada (Ec. 18.1, Groover usa Do). │
  │ No incluye retornos en rápido ni cambios de herramienta.                     │
  └──────────────────────────────────────────────────────────────────────────────┘

------------------------------------------------------------
  1) Torneado - cilindrado
  2) Torneado - refrentado
  3) Fresado - planeado con placas
  4) Fresado periférico
  5) Taladrado
  r) Resumen    g) Guardar .txt    q) Salir
  > r

  ┌─ RESUMEN - tiempo de corte, sin carga/descarga ni cambios ──┐
  │ 1. Torneado - cilindrado              0.574 min     34.5 s  │
  │ TOTAL                                 0.574 min     34.5 s  │
  └─────────────────────────────────────────────────────────────┘

  > q
```

## Fuentes

- Groover, *Principles of Modern Manufacturing*, SI Version (WIE), 2016
  - Ec. 18.1–18.4 (torneado), 18.7–18.11 (taladrado), 18.13–18.20 (fresado)
  - Ec. 20.1, 20.2 y Fig. 20.2 (rugosidad ideal y real)
- Kalpakjian & Schmid, *Manufacturing Engineering and Technology*, 8ª ed. SI
  - Ec. 21.30 (Rt = f²/8R), sec. 33.3 (definición de Rt)

- Sandvik Coromant, catálogo *Turning tools*, Cutting data p. A278–A281
  - vc recomendada (escribir `?` en vc de torneado)
  - ap y fn recomendados por placa, p. A282 en adelante → `datos/sandvik_ap_fn.json` (extracción automática, ~95 % de las placas). Se usa escribiendo la designación con geometría, ej. `CNMG120408-PM`.

## Supuestos (marcados con * en la salida)

- Fig. 20.2 digitalizada (±0,02). Fuera de rango (≈9–137 m/min) se toma el valor del extremo.
- Rz objetivo: Rz = Rt del perfil ideal, sin corrección por material.
- Refrentado con n constante calculada en Do.
- Fresado periférico: sin fórmula de rugosidad en la bibliografía cargada.
