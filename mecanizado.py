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


def ayuda_sin_tabla():
    print("  (sin tabla de vc cargada para esta operación: usar catálogo del fabricante)")


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


def pedir(txt, default=None, minimo=0.0, permitir_cero=False, ayuda=None):
    d = f" [{default}]" if default is not None else ""
    if ayuda:
        d += "  <- ? = tabla | código (01.2) | código + valor (01.2 250)"
    while True:
        s = input(f"  {txt}{d}: ").strip().replace(",", ".")
        if s == "?" and ayuda:
            ayuda()
            continue
        if ayuda is ayuda_vc_torneado:
            v = vc_por_codigo(s)
            if v is not None:
                return v
        if s == "" and default is not None:
            return float(default) if default != "" else None
        try:
            v = float(s)
        except ValueError:
            print("    -> número inválido")
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
    re = pedir("Radio de punta rε [mm]", 0.8)
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
def cilindrado(out):
    out.p("\n=== TORNEADO - CILINDRADO ===")
    D = pedir("Diámetro inicial Do [mm]", 50)
    L = pedir("Longitud de corte L [mm]", 100)
    a = pedir("Recorrido en vacío, entrada + salida [mm]", 0, permitir_cero=True)
    vc = pedir("vc [m/min]", 200, ayuda=ayuda_vc_torneado)
    nmax = pedir_nmax()
    pas = pedir("Cantidad de pasadas", 1)
    out.p("\n  CORTE")
    nota_vc(out)
    N, vc = rpm(out, vc, D, nmax, "18.1")
    f = bloque_rugosidad(out, vc)
    fr = N * f
    out.p("\n  TIEMPO")
    out.f("fr", "= n · f", f"{N:.0f} · {f:.3f}", f"{fr:.1f} mm/min", f"{SRC_G}, Ec. 18.3")
    Tm = (L + a) / fr * pas
    out.f("Tm", "= (L + a) / fr · pasadas", f"({L:g} + {a:g}) / {fr:.1f} · {pas:g}",
          f"{Tm:.3f} min = {Tm * 60:.1f} s", f"{SRC_G}, Ec. 18.4")
    return Tm


def refrentado(out):
    out.p("\n=== TORNEADO - REFRENTADO (n constante) ===")
    Do = pedir("Diámetro exterior Do [mm]", 50)
    Di = pedir("Diámetro interior Di [mm] (0 = macizo)", 0, permitir_cero=True)
    a = pedir("Recorrido en vacío, entrada + salida [mm]", 0, permitir_cero=True)
    vc = pedir("vc en Do [m/min]", 200, ayuda=ayuda_vc_torneado)
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
    th = pedir("Ángulo de punta θ [°]", 118)
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
