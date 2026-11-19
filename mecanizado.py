#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mecanizado.py - Tiempos de mecanizado y rugosidad (Ra / Rt) para torneado,
fresado y taladrado. Consola, solo biblioteca estandar.

Fuentes (todas las formulas llevan su referencia al imprimirse):
  [G] Groover, Principles of Modern Manufacturing, SI Version (WIE), 2016
      Ec. 18.1-18.4 (p.395-396) torneado | 18.7-18.11 (p.404-405) taladrado
      Ec. 18.13-18.20 (p.410-412) fresado | Ec. 20.1 (p.464), 20.2 y Fig. 20.2 (p.465)
  [S] Sandvik Coromant, catálogo Turning tools, Cutting data p. A278-A281 (vc)
  [K] Kalpakjian & Schmid, Manufacturing Engineering and Technology, 8a ed. SI
      Ec. 21.30 (p.664) Rt = f^2/8R | Def. de Rt, sec. 33.3 (p.1071)

Supuestos propios (marcados con * en la salida):
  * r_ai fuera del rango de la Fig. 20.2 (aprox. 9-137 m/min; aleaciones de
    facil mecanizado hasta 91,5 m/min): se toma el valor del extremo.
  * Rz objetivo: para el perfil ideal periodico de avance se toma Rz = Rt
    (todos los picos iguales). Sin correccion por material (no hay fuente).
  * Valores de la Fig. 20.2 digitalizados de la figura, error de lectura aprox. +-0,02.

Uso: python mecanizado.py   (Enter acepta el valor entre corchetes)
"""

import math
import sys
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# Groover Fig. 20.2 - relacion Ra real / Ra ideal vs vc [m/min]
# (datos General Electric; digitalizados de la figura)
# ---------------------------------------------------------------------------
FIG_20_2 = {
    "ductil": [(9, 2.46), (12, 2.37), (15, 2.29), (20, 2.16), (25, 2.05),
               (30.5, 1.93), (40, 1.75), (50, 1.59), (61, 1.46), (70, 1.37),
               (80, 1.31), (91.5, 1.24), (100, 1.20), (110, 1.16),
               (122, 1.12), (130, 1.09), (137, 1.07)],
    "fundicion": [(9, 1.77), (12, 1.73), (15, 1.69), (20, 1.65), (25, 1.60),
                  (30.5, 1.56), (40, 1.50), (50, 1.45), (61, 1.40),
                  (70, 1.37), (80, 1.33), (91.5, 1.29), (100, 1.27),
                  (110, 1.25), (122, 1.22), (130, 1.21), (137, 1.20)],
    "facil": [(9, 1.19), (12, 1.17), (15, 1.15), (20, 1.13), (25, 1.11),
              (30.5, 1.09), (40, 1.06), (50, 1.04), (61, 1.02), (91.5, 1.00)],
}
MATERIALES = {"1": ("ductil", "Metales dúctiles (aceros, Al, Cu...)"),
              "2": ("fundicion", "Fundiciones"),
              "3": ("facil", "Aleaciones de fácil mecanizado")}

# ---------------------------------------------------------------------------
# Sandvik Coromant, catalogo "Turning tools", General Turning - Cutting data,
# p. A278-A281. vc [m/min] para los 3 avances fn indicados. Con refrigerante.
# ---------------------------------------------------------------------------
VC_TORNEADO = [
    ("ISO P  acero - GC4325", "fn 0,1 / 0,4 / 0,8 mm/rev", [
        ("01.1", "No aleado C 0,10-0,25 %   125 HB", "510-345-245"),
        ("01.2", "No aleado C 0,25-0,55 %   150 HB", "455-305-215"),
        ("01.3", "No aleado C 0,55-0,80 %   170 HB", "425-290-205"),
        ("02.1", "Baja aleación, sin templar 180 HB", "460-305-215"),
        ("02.12", "Acero para rodamientos    210 HB", "395-265-190"),
        ("02.2", "Templado y revenido       275 HB", "255-180-140"),
        ("02.2", "Templado y revenido       350 HB", "205-145-110"),
        ("03.11", "Alta aleación, recocido   200 HB", "300-205-150"),
        ("03.21", "Acero de herramientas templ. 325 HB", "135-95-75"),
        ("06.1", "Acero fundido no aleado   180 HB", "240-180-130"),
        ("06.2", "Acero fundido baja aleac. 200 HB", "210-140-100"),
        ("06.3", "Acero fundido alta aleac. 225 HB", "185-125-90"),
    ]),
    ("ISO M  inoxidable - GC2025", "fn 0,2 / 0,4 / 0,6 mm/rev", [
        ("05.11", "Ferrítico/martensítico    200 HB", "225-175-130"),
        ("05.12", "Ferr./mart. PH            330 HB", "100-70-45"),
        ("05.13", "Ferr./mart. templado      330 HB", "115-80-55"),
        ("05.21", "Austenítico               180 HB", "190-145-110"),
        ("05.22", "Austenítico PH            330 HB", "100-70-55"),
        ("05.23", "Superaustenítico          200 HB", "130-100-75"),
    ]),
    ("ISO K  fundición - GC3210", "fn 0,2 / 0,4 / 0,6 mm/rev", [
        ("07.1", "Maleable ferrítica        130 HB", "385-315-265"),
        ("07.2", "Maleable perlítica        230 HB", "315-255-215"),
        ("08.1", "Gris, baja resistencia    180 HB", "445-360-305"),
        ("08.2", "Gris, alta resistencia    220 HB", "355-290-245"),
        ("09.1", "Nodular ferrítica         160 HB", "360-305-250"),
        ("09.2", "Nodular perlítica         250 HB", "325-275-225"),
        ("09.3", "Nodular martensítica      380 HB", "245-210-170"),
    ]),
    ("ISO N  no ferrosos - H10", "fn 0,15-0,8 mm/rev (vale para todo el rango)", [
        ("30.11", "Al forjado, no envejecido  60 HB", "2000 (2500-250)"),
        ("30.12", "Al forjado, envejecido    100 HB", "2000 (2500-250)"),
        ("30.41", "Al fundido 13-15 % Si     130 HB", "450 (560-55)"),
        ("30.42", "Al fundido 16-22 % Si     130 HB", "300 (375-38)"),
        ("33.1", "Cu de corte libre ≥1 % Pb 110 HB", "500 (630-65)"),
        ("33.2", "Latón, bronce ≤1 % Pb      90 HB", "500 (630-65)"),
        ("33.3", "Bronce, Cu electrolítico  100 HB", "300 (375-38)"),
    ]),
]


def ayuda_vc_torneado():
    print("\n  vc recomendada [m/min] - Sandvik 'Turning tools', p. A278-A281 (con refrigerante)")
    for grupo, feeds, filas in VC_TORNEADO:
        print(f"\n  {grupo}   ({feeds})")
        for cmc, mat, vc in filas:
            print(f"    {cmc:<6}{mat:<38}{vc}")
    print("\n  A mayor avance, menor vc. Otras calidades: ver catálogo.\n")


VC_ORIGEN = {"txt": None}   # ultima vc tomada de la tabla (para la salida)


def vc_por_codigo(s):
    """Si s es un codigo CMC de la tabla, devuelve la vc elegida; si no, None.
    'codigo valor' (ej. '30.11 1000'): usa el valor propio y deja el codigo como referencia."""
    partes = s.split()
    if len(partes) == 2:
        fila = next(((g, c, m, v) for g, fe, fs in VC_TORNEADO for c, m, v in fs if c == partes[0]), None)
        try:
            vc = float(partes[1])
        except ValueError:
            vc = 0
        if fila and vc > 0:
            g, c, m, v = fila
            VC_ORIGEN["txt"] = (f"vc = {vc:g} m/min (valor propio). Ref. Sandvik p. A278-A281: "
                                f"{c} {' '.join(m.split())}, {g.split(' - ')[1]}: {v}")
            print(f"  -> vc = {vc:g} m/min  (tabla para {c}: {v})")
            return vc
        return None
    filas = [(g, fe, c, m, v) for g, fe, fs in VC_TORNEADO for c, m, v in fs if c == s]
    if not filas:
        return None
    if len(filas) > 1:
        for i, (g, fe, c, m, v) in enumerate(filas, 1):
            print(f"    {i}) {c} {m}  {v}")
        k = input("  Cuál [1]: ").strip() or "1"
        filas = [filas[int(k) - 1]] if k.isdigit() and 1 <= int(k) <= len(filas) else filas[:1]
    g, fe, c, m, v = filas[0]
    base = v.split(" (")[0]
    vals = [float(x) for x in base.split("-")]
    if len(vals) == 1:
        vc, col = vals[0], fe
    else:
        fns = fe.replace("fn ", "").replace(" mm/rev", "").split(" / ")
        print(f"  {c} {m.strip()}:  " + "   ".join(f"{i}) fn {fn} -> {x:g}" for i, (fn, x) in enumerate(zip(fns, vals), 1)))
        k = input("  Avance de referencia [2]: ").strip() or "2"
        i = int(k) - 1 if k in ("1", "2", "3") else 1
        vc, col = vals[i], f"fn {fns[i]} mm/rev"
    VC_ORIGEN["txt"] = f"vc = {vc:g} m/min de Sandvik Turning tools p. A278-A281: {c} {' '.join(m.split())}, {g.split(' - ')[1]}, {col}"
    print(f"  -> vc = {vc:g} m/min")
    return vc


EJ_VC_TORNEADO = ["180          vc directa [m/min]",
                  "01.2         vc de la tabla Sandvik (pregunta el avance)",
                  "01.2 250     vc propia, el código queda como referencia",
                  "?            ver tabla de vc"]


def ayuda_sin_tabla():
    print("  (sin tabla de vc cargada para esta operación: usar catálogo del fabricante)")


# ---------------------------------------------------------------------------
# Sandvik ap / fn recomendados por placa (datos/sandvik_ap_fn.json)
# ---------------------------------------------------------------------------
def _cargar_placas():
    import json, os
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "sandvik_ap_fn.json")
    try:
        with open(ruta, encoding="utf-8") as fh:
            return json.load(fh)["placas"]
    except Exception:
        return {}


PLACAS = _cargar_placas()
PLACA = {"fila": None, "nombre": None}   # ultima placa reconocida


def buscar_placa(s):
    k = "".join(s.upper().split())
    fila = PLACAS.get(k)
    if fila:
        PLACA["fila"], PLACA["nombre"] = fila, k
        ap, fn = fila["ap"], fila["fn"]
        print(f"  -> {k}: ap rec {ap[0]:g} ({ap[1]:g}-{ap[2]:g}) mm | "
              f"fn rec {fn[0]:g} ({fn[1]:g}-{fn[2]:g}) mm/rev  [Sandvik, pág. PDF {fila['pdf']}]")
    return fila


# Sandvik "Turning tools", Code keys - General turning inserts, pos. 7 (pag. PDF 661)
RADIOS_ISO = [("01", 0.1), ("02", 0.2), ("04", 0.4), ("05", 0.5), ("08", 0.8),
              ("10", 1.0), ("12", 1.2), ("15", 1.5), ("16", 1.6), ("24", 2.4), ("32", 3.2)]


def ayuda_radio():
    print("\n  Radio de punta RE - código ISO de la placa, posición 7")
    print("  (Sandvik 'Turning tools', Code keys, General turning inserts)")
    print("    " + "   ".join(f"{c} = {r:g}" for c, r in RADIOS_ISO))
    print("  Ej.: CNMG 12 04 08 -> RE = 0,8 mm\n")


def radio_por_iso(s):
    """Acepta la designacion ISO completa (CNMG120408, CNMG 12 04 08, DCMT11T304...)."""
    import re
    m = re.match(r"^([A-Za-z]{4})\s*(\d{2})\s*([0-9Tt]\d)\s*(\d{2})", s)
    if not m:
        return None
    cod = m.group(4)
    r = dict(RADIOS_ISO).get(cod)
    if r is None:
        print(f"    -> código de radio {cod} no está en la tabla")
        return None
    print(f"  -> {m.group(1).upper()} {m.group(2)} {m.group(3).upper()} {cod}: RE = {r:g} mm")
    PLACA["fila"] = None
    if not buscar_placa(s) and "-" in s:
        print("    (placa no encontrada en la tabla de ap/fn de Sandvik)")
    return r


EJ_RADIO = ["0.8             radio en mm",
            "CNMG120408      designación ISO (toma el 08 -> 0,8 mm)",
            "CNMG120408-PF   con geometría: además muestra ap y fn de Sandvik",
            "?               ver códigos de radio"]


def ayuda_punta():
    print("  Groover SI, sec. 18.3 (p. 450): valor típico del ángulo de punta = 118°\n")


SRC_G = "Groover SI 2016"
SRC_K = "Kalpakjian 8a SI"


def r_ai(vc, mat):
    """Interpolacion lineal en Fig. 20.2. Devuelve (r, extrapolado)."""
    pts = FIG_20_2[mat]
    if vc <= pts[0][0]:
        return pts[0][1], vc < pts[0][0]
    if vc >= pts[-1][0]:
        return pts[-1][1], vc > pts[-1][0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= vc <= x1:
            return y0 + (y1 - y0) * (vc - x0) / (x1 - x0), False


# ---------------------------------------------------------------------------
# Entrada / salida
# ---------------------------------------------------------------------------
class Salida:
    def __init__(self):
        self.lineas = []

    def p(self, txt=""):
        print(txt)
        self.lineas.append(txt)

    def f(self, nombre, simb, sust, res, fuente):
        self.p(f"  {nombre:<14}{simb}")
        self.p(f"  {'':<14}= {sust}")
        self.p(f"  {'':<14}= {res}    [{fuente}]")

    def nota(self, txt):
        self.p(f"  * {txt}")


def pedir(txt, default=None, minimo=0.0, permitir_cero=False, ayuda=None,
          ejemplos=None, resolver=None):
    """ayuda: funcion que se llama con '?'. resolver: convierte texto especial
    (codigo de tabla, designacion ISO...) en numero; devuelve None si no aplica."""
    d = f" [{default}]" if default is not None else ""
    if ayuda and "?" not in txt:
        d += "  (? = lista)"
    if ejemplos:
        print("    ej.: " + ejemplos[0])
        for e in ejemplos[1:]:
            print("          " + e)
    while True:
        s = input(f"  {txt}{d}: ").strip().replace(",", ".")
        if s == "?" and ayuda:
            ayuda()
            continue
        if resolver and s:
            v = resolver(s)
            if v is not None:
                return v
        if s == "" and default is not None:
            return float(default)
        try:
            v = float(s)
        except ValueError:
            print("    -> no reconocido" + (" (? = ayuda)" if ayuda else ""))
            continue
        if v < minimo or (v == 0 and not permitir_cero):
            print("    -> fuera de rango")
            continue
        return v


def elegir(txt, opciones, default=None):
    for k, v in opciones.items():
        print(f"    {k}) {v if isinstance(v, str) else v[1]}")
    d = f" [{default}]" if default else ""
    while True:
        s = input(f"  {txt}{d}: ").strip().lower()
        if s == "" and default:
            s = default
        if s in opciones:
            return s


def pedir_nmax():
    s = input("  n máx. de la máquina [rpm] (Enter = sin límite): ").strip()
    try:
        return float(s.replace(",", ".")) if s else None
    except ValueError:
        return None


def nota_vc(out):
    if VC_ORIGEN["txt"]:
        out.p("  " + VC_ORIGEN["txt"])
        VC_ORIGEN["txt"] = None


def rpm(out, vc, D, nmax, ec):
    N = 1000 * vc / (math.pi * D)
    out.f("n", "= 1000·vc / (π·D)",
          f"1000·{vc:g} / (π·{D:g})", f"{N:.0f} rpm", f"{SRC_G}, Ec. {ec}")
    if nmax and N > nmax:
        vc_r = math.pi * D * nmax / 1000
        out.nota(f"n supera n máx -> n = {nmax:.0f} rpm, vc real = {vc_r:.1f} m/min")
        return nmax, vc_r
    return N, vc


# ---------------------------------------------------------------------------
# Rugosidad (herramienta de un filo con radio; o planeado con placas usando fz)
# ---------------------------------------------------------------------------
def bloque_rugosidad(out, vc, nombre_f="f", unidad_f="mm/rev"):
    """Pide radio, material y dato de rugosidad. Devuelve el avance."""
    print("\n  -- Rugosidad --")
    PLACA["fila"] = None
    re = pedir("Radio de punta rε [mm]", 0.8, ayuda=ayuda_radio,
               ejemplos=EJ_RADIO, resolver=radio_por_iso)
    mat = MATERIALES[elegir("Material", MATERIALES, "1")][0]
    modo = elegir("Dato", {"1": "Ra objetivo [µm]",
                           "2": "Rz objetivo [µm] *",
                           "3": f"Tengo el avance {nombre_f}"}, "1")
    r, extrap = r_ai(vc, mat)

    out.p("\n  RUGOSIDAD")
    if modo == "1":
        ra_obj = pedir("Ra objetivo [µm]", 1.6)
        out.f("r_ai", "Fig. 20.2", f"{mat}, vc = {vc:g} m/min",
              f"{r:.2f}", f"{SRC_G}, Fig. 20.2")
        f = math.sqrt(32 * re * (ra_obj / r) / 1000)
        out.f(f"{nombre_f} máx", "= √(32·rε·Ra/(r_ai·1000))",
              f"√(32·{re:g}·{ra_obj:g}/({r:.2f}·1000))",
              f"{f:.3f} {unidad_f}", f"{SRC_G}, Ec. 20.1 y 20.2 despejadas")
    elif modo == "2":
        rz_obj = pedir("Rz objetivo [µm]", 6.3)
        f = math.sqrt(8 * re * rz_obj / 1000)
        out.f(f"{nombre_f} máx", "= √(8·rε·Rz/1000)",
              f"√(8·{re:g}·{rz_obj:g}/1000)",
              f"{f:.3f} {unidad_f}", f"{SRC_K}, Ec. 21.30 despejada")
        out.nota("Rz = Rt del perfil ideal (supuesto). Valor ideal, sin corrección por material.")
    else:
        f = pedir(f"Avance {nombre_f} [{unidad_f}]", 0.2)
        out.f("r_ai", "Fig. 20.2", f"{mat}, vc = {vc:g} m/min",
              f"{r:.2f}", f"{SRC_G}, Fig. 20.2")

    if PLACA["fila"] and unidad_f == "mm/rev":
        fn = PLACA["fila"]["fn"]
        out.p(f"  Placa {PLACA['nombre']}: fn rec {fn[0]:g}, rango {fn[1]:g}-{fn[2]:g} mm/rev "
              f"[Sandvik pág. PDF {PLACA['fila']['pdf']}]")
        if not fn[1] <= f <= fn[2]:
            out.nota(f"f = {f:.3f} fuera del rango de la placa ({fn[1]:g}-{fn[2]:g}) - a criterio del usuario.")
    Ri = f ** 2 / (32 * re) * 1000
    Rt = f ** 2 / (8 * re) * 1000
    out.f("Ri (ideal)", "= f² / (32·rε)", f"{f:.3f}² / (32·{re:g})",
          f"{Ri:.2f} µm", f"{SRC_G}, Ec. 20.1")
    if modo != "2":
        out.f("Ra (estim.)", "= r_ai · Ri", f"{r:.2f} · {Ri:.2f}",
              f"{r * Ri:.2f} µm", f"{SRC_G}, Ec. 20.2")
    out.f("Rt (ideal)", "= f² / (8·rε)", f"{f:.3f}² / (8·{re:g})",
          f"{Rt:.2f} µm", f"{SRC_K}, Ec. 21.30")
    if extrap and modo != "2":
        out.nota(f"vc fuera del rango de la Fig. 20.2 -> r_ai del extremo ({r:.2f}).")
    out.p("  Límites: herramienta afilada; solo el radio genera la superficie; sin")
    out.p("  vibración, BUE ni desgaste (Groover 20.2). Rt ideal no corrige por material.")
    return f


# ---------------------------------------------------------------------------
# Operaciones
# ---------------------------------------------------------------------------
def n_silencioso(vc, D, nmax):
    N = 1000 * vc / (math.pi * D)
    if nmax and N > nmax:
        return nmax, math.pi * D * nmax / 1000, True
    return N, vc, False


def cilindrado(out):
    out.p("\n=== TORNEADO - CILINDRADO ===")
    Do = pedir("Diámetro inicial Do [mm]", 50)
    while True:
        Df = pedir("Diámetro final Df [mm]", Do - 4)
        if Df < Do:
            break
        print("    -> Df debe ser menor que Do")
    L = pedir("Longitud de corte L [mm]", 100)
    a = pedir("Recorrido en vacío, entrada + salida [mm]", 0, permitir_cero=True)
    nmax = pedir_nmax()
    prof = (Do - Df) / 2
    sob = pedir("Sobrematerial de acabado, radial [mm] (0 = todo en una pasada)",
                min(0.5, prof), permitir_cero=True)
    sob = prof if (sob == 0 or sob > prof) else sob
    desb = prof - sob

    pasadas = []                      # (tipo, D antes, ap, n, f, fr, Tm)
    if desb > 1e-9:
        print("\n  -- Desbaste --")
        print("    ej.: CNMG120408-PM   (Enter = sin placa)")
        pl = None
        while True:
            sp = input("  Placa de desbaste (ISO con geometría): ").strip()
            if not sp:
                break
            pl = buscar_placa(sp)
            if pl:
                break
            print("    -> no encontrada en la tabla de Sandvik (Enter para seguir sin placa)")
        apmax = pedir("ap máx por pasada [mm]", pl["ap"][0] if pl else 2)
        fd = pedir("Avance de desbaste f [mm/rev]", pl["fn"][0] if pl else 0.3)
        if pl:
            out.p(f"  Placa desbaste {PLACA['nombre']}: ap {pl['ap'][1]:g}-{pl['ap'][2]:g} mm, "
                  f"fn {pl['fn'][1]:g}-{pl['fn'][2]:g} mm/rev [Sandvik pág. PDF {pl['pdf']}]")
            if not (pl["ap"][1] <= apmax <= pl["ap"][2]) or not (pl["fn"][1] <= fd <= pl["fn"][2]):
                out.nota("ap o f de desbaste fuera del rango de la placa - a criterio del usuario.")
        vcd = pedir("vc desbaste [m/min]", 200, ayuda=ayuda_vc_torneado,
                    ejemplos=EJ_VC_TORNEADO, resolver=vc_por_codigo)
        nd = math.ceil(desb / apmax - 1e-9)
        ap = desb / nd
        out.p(f"\n  DESBASTE: {desb:g} mm radiales en {nd} pasada(s) de ap = {ap:.3f} mm")
        nota_vc(out)
        D = Do
        for i in range(nd):
            if i == 0:
                out.f("Df pasada", "= D − 2·ap", f"{D:g} − 2·{ap:.3f}",
                      f"{D - 2 * ap:.3f} mm", f"{SRC_G}, Ec. 18.2")
                N, vcr = rpm(out, vcd, D, nmax, "18.1")
            else:
                N, vcr, _ = n_silencioso(vcd, D, nmax)
            fr = N * fd
            tm = (L + a) / fr
            pasadas.append(("desbaste", D, ap, N, fd, fr, tm))
            D -= 2 * ap
        out.p("  n se recalcula en el diámetro de cada pasada (Ec. 18.1 con D de la pasada).")
        Dac = D
    else:
        Dac = Do

    print("\n  -- Acabado --")
    vca = pedir("vc acabado [m/min]", 200, ayuda=ayuda_vc_torneado,
                ejemplos=EJ_VC_TORNEADO, resolver=vc_por_codigo)
    out.p(f"\n  ACABADO: ap = {sob:.3f} mm, de Ø{Dac:.3f} a Ø{Df:g}")
    nota_vc(out)
    N, vca = rpm(out, vca, Dac, nmax, "18.1")
    f = bloque_rugosidad(out, vca)
    if PLACA["fila"]:
        apr = PLACA["fila"]["ap"]
        if not apr[1] <= sob <= apr[2]:
            out.nota(f"ap acabado = {sob:g} mm fuera del rango de la placa ({apr[1]:g}-{apr[2]:g}) - a criterio del usuario.")
    fr = N * f
    out.p("\n  TIEMPO (acabado)")
    out.f("fr", "= n · f", f"{N:.0f} · {f:.3f}", f"{fr:.1f} mm/min", f"{SRC_G}, Ec. 18.3")
    tm = (L + a) / fr
    out.f("Tm", "= (L + a) / fr", f"({L:g} + {a:g}) / {fr:.1f}",
          f"{tm:.3f} min = {tm * 60:.1f} s", f"{SRC_G}, Ec. 18.4")
    pasadas.append(("acabado", Dac, sob, N, f, fr, tm))

    out.p("\n  PASADAS")
    out.p(f"  {'#':>2}  {'tipo':<9}{'Ø antes':>9}{'ap':>7}{'n':>7}{'f':>7}{'fr':>8}{'Tm [s]':>9}")
    for i, (t, D, ap, N, ff, fr, tm) in enumerate(pasadas, 1):
        out.p(f"  {i:>2}  {t:<9}{D:>9.2f}{ap:>7.2f}{N:>7.0f}{ff:>7.3f}{fr:>8.1f}{tm * 60:>9.1f}")
    T = sum(p[6] for p in pasadas)
    out.p(f"  {'Total':<40}{T:>8.3f} min = {T * 60:.1f} s")
    if nmax and any(abs(p[3] - nmax) < 1e-6 for p in pasadas):
        out.nota(f"Pasadas con n = {nmax:.0f} rpm: limitadas por n máx (vc real menor).")
    out.p("  n calculada con el diámetro antes de cada pasada (Ec. 18.1, Groover usa Do).")
    out.p("  No incluye retornos en rápido ni cambios de herramienta.")
    return T


def refrentado(out):
    out.p("\n=== TORNEADO - REFRENTADO (n constante) ===")
    Do = pedir("Diámetro exterior Do [mm]", 50)
    Di = pedir("Diámetro interior Di [mm] (0 = macizo)", 0, permitir_cero=True)
    a = pedir("Recorrido en vacío, entrada + salida [mm]", 0, permitir_cero=True)
    vc = pedir("vc en Do [m/min]", 200, ayuda=ayuda_vc_torneado,
               ejemplos=EJ_VC_TORNEADO, resolver=vc_por_codigo)
    nmax = pedir_nmax()
    pas = pedir("Cantidad de pasadas", 1)
    out.p("\n  CORTE")
    nota_vc(out)
    N, vc = rpm(out, vc, Do, nmax, "18.1")
    f = bloque_rugosidad(out, vc)
    fr = N * f
    out.p("\n  TIEMPO")
    out.f("fr", "= n · f", f"{N:.0f} · {f:.3f}", f"{fr:.1f} mm/min", f"{SRC_G}, Ec. 18.3")
    L = (Do - Di) / 2
    Tm = (L + a) / fr * pas
    out.f("Tm", "= ((Do−Di)/2 + a) / fr · pas", f"({L:g} + {a:g}) / {fr:.1f} · {pas:g}",
          f"{Tm:.3f} min = {Tm * 60:.1f} s", f"{SRC_G}, Ec. 18.4 con L radial")
    out.p("  Límites: n constante calculada en Do. Con vc constante (G96) el tiempo")
    out.p("  real es menor; hacia el centro vc baja y r_ai (Fig. 20.2) empeora.")
    return Tm


def planeado(out):
    out.p("\n=== FRESADO - PLANEADO CON PLACAS ===")
    D = pedir("Diámetro de fresa D [mm]", 63)
    z = pedir("Número de dientes nt", 5)
    w = pedir("Ancho de la pieza w [mm]", 40)
    L = pedir("Longitud L [mm]", 150)
    pos = elegir("Posición de la fresa", {"1": "Centrada (Fig. 18.22a)",
                                          "2": "Desplazada a un lado (Fig. 18.22b)"}, "1")
    a = pedir("Recorrido en vacío, entrada + salida [mm]", 0, permitir_cero=True)
    vc = pedir("vc [m/min] (sin tabla cargada, ver catálogo)", 200)
    nmax = pedir_nmax()
    pas = pedir("Cantidad de pasadas", 1)
    out.p("\n  CORTE")
    N, vc = rpm(out, vc, D, nmax, "18.13")
    fz = bloque_rugosidad(out, vc, "fz", "mm/diente")
    out.p("  Groover: Ec. 20.1 aplicable al planeado con placas usando fz.")
    out.p("  No aplica a placas wiper. Supone todas las placas a igual altura.")
    fr = N * z * fz
    out.p("\n  TIEMPO")
    out.f("fr", "= n · nt · fz", f"{N:.0f} · {z:g} · {fz:.3f}",
          f"{fr:.1f} mm/min", f"{SRC_G}, Ec. 18.14")
    if pos == "1":
        if D > w:
            A = 0.5 * (D - math.sqrt(D ** 2 - w ** 2))
            out.f("A", "= 0,5·(D − √(D² − w²))", f"0,5·({D:g} − √({D:g}² − {w:g}²))",
                  f"{A:.2f} mm", f"{SRC_G}, Ec. 18.18")
        else:
            A = 0.5 * D
            out.f("A", "= 0,5·D  (D ≤ w)", f"0,5·{D:g}", f"{A:.2f} mm", f"{SRC_G}, Ec. 18.18")
    else:
        if w < D:
            A = math.sqrt(w * (D - w))
            out.f("A", "= √(w·(D − w))", f"√({w:g}·({D:g} − {w:g}))",
                  f"{A:.2f} mm", f"{SRC_G}, Ec. 18.19")
        else:
            A = 0.5 * D
            out.nota("w ≥ D: Ec. 18.19 no aplica; se toma A = 0,5·D.")
    Tm = (L + A + a) / fr * pas
    out.f("Tm", "= (L + A + a) / fr · pas", f"({L:g} + {A:.2f} + {a:g}) / {fr:.1f} · {pas:g}",
          f"{Tm:.3f} min = {Tm * 60:.1f} s", f"{SRC_G}, Ec. 18.20")
    return Tm


def periferico(out):
    out.p("\n=== FRESADO PERIFÉRICO (tangencial) ===")
    D = pedir("Diámetro de fresa D [mm]", 63)
    z = pedir("Número de dientes nt", 6)
    d = pedir("Profundidad de corte d [mm]", 3)
    L = pedir("Longitud L [mm]", 150)
    a = pedir("Recorrido en vacío, entrada + salida [mm]", 0, permitir_cero=True)
    vc = pedir("vc [m/min] (sin tabla cargada, ver catálogo)", 30)
    nmax = pedir_nmax()
    fz = pedir("Avance por diente fz [mm/diente]", 0.1)
    pas = pedir("Cantidad de pasadas", 1)
    out.p("\n  CORTE")
    N, vc = rpm(out, vc, D, nmax, "18.13")
    out.p("\n  TIEMPO")
    fr = N * z * fz
    out.f("fr", "= n · nt · fz", f"{N:.0f} · {z:g} · {fz:g}", f"{fr:.1f} mm/min", f"{SRC_G}, Ec. 18.14")
    A = math.sqrt(d * (D - d))
    out.f("A", "= √(d·(D − d))", f"√({d:g}·({D:g} − {d:g}))", f"{A:.2f} mm", f"{SRC_G}, Ec. 18.16")
    Tm = (L + A + a) / fr * pas
    out.f("Tm", "= (L + A + a) / fr · pas", f"({L:g} + {A:.2f} + {a:g}) / {fr:.1f} · {pas:g}",
          f"{Tm:.3f} min = {Tm * 60:.1f} s", f"{SRC_G}, Ec. 18.17")
    out.p("  Rugosidad: sin fórmula en la bibliografía cargada (Groover, Kalpakjian).")
    return Tm


def taladrado(out):
    out.p("\n=== TALADRADO ===")
    D = pedir("Diámetro de broca D [mm]", 10)
    th = pedir("Ángulo de punta θ [°] (? = valor típico)", 118, ayuda=ayuda_punta)
    tipo = elegir("Agujero", {"1": "Pasante", "2": "Ciego"}, "1")
    t = pedir("Espesor t [mm]" if tipo == "1" else "Profundidad a diámetro pleno d [mm]", 20)
    vc = pedir("vc [m/min] (sin tabla cargada, ver catálogo)", 25)
    nmax = pedir_nmax()
    f = pedir("Avance f [mm/rev]", 0.15)
    out.p("\n  CORTE")
    N, vc = rpm(out, vc, D, nmax, "18.7")
    out.p("\n  TIEMPO")
    fr = N * f
    out.f("fr", "= n · f", f"{N:.0f} · {f:g}", f"{fr:.1f} mm/min", f"{SRC_G}, Ec. 18.8")
    A = 0.5 * D * math.tan(math.radians(90 - th / 2))
    out.f("A", "= 0,5·D·tan(90 − θ/2)", f"0,5·{D:g}·tan(90 − {th:g}/2)",
          f"{A:.2f} mm", f"{SRC_G}, Ec. 18.10")
    Tm = (t + A) / fr
    ec = "18.9" if tipo == "1" else "18.11"
    out.f("Tm", "= (t + A) / fr", f"({t:g} + {A:.2f}) / {fr:.1f}",
          f"{Tm:.3f} min = {Tm * 60:.1f} s", f"{SRC_G}, Ec. {ec}")
    if tipo == "1":
        out.p("  Groover: en pasante la broca sale un poco más; el tiempo real es algo mayor.")
    return Tm


OPERACIONES = {
    "1": ("Torneado - cilindrado", cilindrado),
    "2": ("Torneado - refrentado", refrentado),
    "3": ("Fresado - planeado con placas", planeado),
    "4": ("Fresado periférico", periferico),
    "5": ("Taladrado", taladrado),
}


def main():
    out = Salida()
    hechas = []
    out.p(f"MECANIZADO - tiempos y rugosidad   {datetime.date.today():%d/%m/%Y}")
    while True:
        print("\n" + "-" * 60)
        for k, (n, _) in OPERACIONES.items():
            print(f"  {k}) {n}")
        print("  r) Resumen    g) Guardar .txt    q) Salir")
        op = input("  > ").strip().lower()
        if op in OPERACIONES:
            nombre, fn = OPERACIONES[op]
            try:
                tm = fn(out)
                hechas.append((nombre, tm))
            except (KeyboardInterrupt, EOFError):
                print("\n  (operación cancelada)")
        elif op == "r":
            resumen(out, hechas)
        elif op == "g":
            resumen(out, hechas)
            nom = f"mecanizado_{datetime.datetime.now():%Y%m%d_%H%M}.txt"
            with open(nom, "w", encoding="utf-8") as fh:
                fh.write("\n".join(out.lineas) + "\n")
            print(f"  Guardado: {nom}")
        elif op in ("q", "salir"):
            break


def resumen(out, hechas):
    out.p("\n=== RESUMEN (tiempo de corte, sin carga/descarga ni cambios) ===")
    tot = 0
    for i, (n, t) in enumerate(hechas, 1):
        out.p(f"  {i}. {n:<32}{t:8.3f} min  {t * 60:7.1f} s")
        tot += t
    out.p(f"  {'TOTAL':<35}{tot:8.3f} min  {tot * 60:7.1f} s")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
