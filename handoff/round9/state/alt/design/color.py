"""Colour gates, ported verbatim from the repo's tests/card.mjs (contrast 7458-7485, deuteranope + Lab dE 7668-7770)."""
import math

def hexrgb(h):
    n = int(h[1:], 16); return ((n >> 16) & 255, (n >> 8) & 255, n & 255)

def _lum(c):  # WCAG relative luminance (card.mjs:7480 uses the 0.03928 threshold)
    f = lambda v: (v/255)/12.92 if v/255 <= 0.03928 else (((v/255)+0.055)/1.055)**2.4
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2])

def contrast(a, b):
    la, lb = _lum(hexrgb(a)), _lum(hexrgb(b)); hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def _g(v):
    v /= 255; return v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4

def _ug(v):
    v = min(1.0, max(0.0, v)); return 255*(12.92*v if v <= 0.0031308 else 1.055*v**(1/2.4) - 0.055)

def deuter(c):
    R, G, B = (_g(x) for x in c)
    L = 17.8824*R + 43.5161*G + 4.11935*B
    S = 0.0299566*R + 0.184309*G + 1.46709*B
    M = 0.494207*L + 1.24827*S
    return (_ug(0.080944*L - 0.130504*M + 0.116721*S), _ug(-0.0102485*L + 0.0540194*M - 0.113615*S),
            _ug(-0.000365294*L - 0.00412163*M + 0.693513*S))

def lab(c):
    r, g, b = (_g(x) for x in c)
    X = (0.4124*r + 0.3576*g + 0.1805*b)/0.95047; Y = 0.2126*r + 0.7152*g + 0.0722*b; Z = (0.0193*r + 0.1192*g + 0.9505*b)/1.08883
    f = lambda t: math.cbrt(t) if t > 0.008856 else 7.787*t + 16/116
    X, Y, Z = f(X), f(Y), f(Z); return (116*Y-16, 500*(X-Y), 200*(Y-Z))

def dE(a, b):
    A, B = lab(a), lab(b); return math.dist(A, B)

def deut_dE(h1, h2):
    return dE(deuter(hexrgb(h1)), deuter(hexrgb(h2)))
