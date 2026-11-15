#version 300 es
precision highp float; precision highp int; precision highp sampler2D;
out vec4 oc;
uniform vec2 uRes;
uniform sampler2D uFine, uCoarse, uEarth;
uniform vec3 uCam, uF, uR, uU, uSun, uE, uC1, uC2, uC3, uB1, uB2, uB3;
uniform float uTan, uExp, uShine, uEarthRad, uZmax;
const float MR = 1737400.;
const float SUNR = 0.00466;           // tan of solar disc radius (0.267 deg)

/* ---------- real ground: LOLA 5 m grid (mirrored beyond the edge) ---------- */
float mir(float u, float L){ float t = mod(u, 2.*L); return t < L ? t : 2.*L - t; }
float hF(vec2 p){
  vec2 u = vec2(mir((p.x + 15000.)*0.2 - 0.5, 1599.), mir((-8000. - p.y)*0.2 - 0.5, 1599.));
  ivec2 i = min(ivec2(floor(u)), ivec2(1598)); vec2 f = u - vec2(i);
  float a = texelFetch(uFine, i, 0).r, b = texelFetch(uFine, i + ivec2(1,0), 0).r;
  float c = texelFetch(uFine, i + ivec2(0,1), 0).r, d = texelFetch(uFine, i + ivec2(1,1), 0).r;
  return mix(mix(a,b,f.x), mix(c,d,f.x), f.y);
}
float hC(vec2 p){
  vec2 u = vec2(mir((p.x + 15000.)*0.05 - 0.5, 399.), mir((-8000. - p.y)*0.05 - 0.5, 399.));
  ivec2 i = min(ivec2(floor(u)), ivec2(398)); vec2 f = u - vec2(i);
  float a = texelFetch(uCoarse, i, 0).r, b = texelFetch(uCoarse, i + ivec2(1,0), 0).r;
  float c = texelFetch(uCoarse, i + ivec2(0,1), 0).r, d = texelFetch(uCoarse, i + ivec2(1,1), 0).r;
  return mix(mix(a,b,f.x), mix(c,d,f.x), f.y);
}
float H(vec2 p, float t){
  if (t < 700.) return hF(p);
  if (t > 1200.) return hC(p);
  return mix(hF(p), hC(p), (t - 700.)/500.);
}

/* ---------- generated small-scale surface (below the 5 m the data can see) ---------- */
uint pcg(uint v){ uint s = v*747796405u + 2891336453u; uint w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u; return (w >> 22u) ^ w; }
uint hh(ivec2 c, uint salt){ return pcg(uint(c.x)*1597334677u ^ pcg(uint(c.y)*3812015801u + salt)); }
float u01(uint h){ return float(h) * (1./4294967296.); }
float fadeF(float dia, float pf){ return smoothstep(1.2*pf, 3.5*pf, dia); }

vec3 craters(vec2 p, float size, uint salt, float prob, float fade){
  vec3 acc = vec3(0.);
  if (fade <= 0.) return acc;
  vec2 q = p/size - 0.5; ivec2 c0 = ivec2(floor(q));
  for (int j = 0; j < 2; j++) for (int i = 0; i < 2; i++){
    ivec2 c = c0 + ivec2(i, j); uint h = hh(c, salt);
    if (u01(h) > prob) continue;
    vec2 ctr = (vec2(c) + 0.5 + (vec2(u01(pcg(h+1u)), u01(pcg(h+2u))) - 0.5)*0.4)*size;
    float r = size*(0.13 + 0.17*u01(pcg(h+3u)));
    vec2 dv = p - ctr; float dist = length(dv); float d = dist/r;
    if (d > 1.9) continue;
    float D = 0.19*r*(0.45 + u01(pcg(h+4u)));
    float bowl = 0., dbd = 0.;
    if (d < 1.){ bowl = -D*(1. - d*d); dbd = 2.*D*d; }
    float e = exp(-pow((d - 1.)/0.32, 2.));
    float rim = 0.42*D*e, drim = rim*(-2.*(d - 1.)/0.1024);
    vec2 g = dist > 1e-4 ? dv/dist*(dbd + drim)/r : vec2(0.);
    acc += vec3(bowl + rim, g)*fade;
  }
  return acc;
}
vec3 rocks(vec2 p, float fade){
  vec3 acc = vec3(0.);
  if (fade <= 0.) return acc;
  const float S = 1.7;
  vec2 q = p/S - 0.5; ivec2 c0 = ivec2(floor(q));
  for (int j = 0; j < 2; j++) for (int i = 0; i < 2; i++){
    ivec2 c = c0 + ivec2(i, j); uint h = hh(c, 91u);
    if (u01(h) > 0.34) continue;
    vec2 ctr = (vec2(c) + 0.5 + (vec2(u01(pcg(h+1u)), u01(pcg(h+2u))) - 0.5)*0.6)*S;
    float u = u01(pcg(h+3u)); float r = 0.05 + 0.30*u*u*u;
    vec2 dv = p - ctr; float dist = length(dv); float d = dist/r;
    if (d >= 1.) continue;
    float w = max(1. - d*d, 0.03);
    float hgt = 0.9*r*pow(w, 0.55), dh = 0.9*r*0.55*pow(w, -0.45)*(-2.*d);
    vec2 g = dist > 1e-4 ? dv/dist*dh/r : vec2(0.);
    acc += vec3(hgt, g)*fade;
  }
  return acc;
}
vec3 vnoise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f*f*f*(f*(f*6. - 15.) + 10.), du = 30.*f*f*(f*(f - 2.) + 1.);
  float a = u01(hh(ivec2(i), 7u)), b = u01(hh(ivec2(i) + ivec2(1,0), 7u));
  float c = u01(hh(ivec2(i) + ivec2(0,1), 7u)), d = u01(hh(ivec2(i) + ivec2(1,1), 7u));
  float k1 = b - a, k2 = c - a, k4 = a - b - c + d;
  return vec3(a + k1*u.x + k2*u.y + k4*u.x*u.y - 0.5, du*vec2(k1 + k4*u.y, k2 + k4*u.x));
}
/* returns (height, d/dx, d/dz) of the generated micro-relief; pf = metres per pixel here */
vec3 detail(vec2 p, float pf){
  vec3 d = vec3(0.);
  d += craters(p, 16., 11u, 0.42, fadeF(9., pf));
  d += craters(p, 6.,  23u, 0.50, fadeF(3.6, pf));
  d += craters(p, 2.4, 37u, 0.55, fadeF(1.5, pf));
  d += rocks(p, fadeF(0.45, pf));
  float f1 = fadeF(2.2, pf), f2 = fadeF(0.8, pf), f3 = fadeF(0.3, pf);
  vec3 n1 = vnoise(p/2.2), n2 = vnoise(p/0.8 + 13.), n3 = vnoise(p/0.3 + 7.);
  d += vec3(n1.x*0.10, n1.yz*0.10/2.2)*f1;
  d += vec3(n2.x*0.035, n2.yz*0.035/0.8)*f2;
  d += vec3(n3.x*0.012, n3.yz*0.012/0.3)*f3;
  return d;
}

/* ---------- sky ---------- */
vec3 stars(vec3 rd){
  vec3 q = rd*230.; ivec3 ci = ivec3(floor(q));
  uint h = pcg(uint(ci.x)*73856093u ^ pcg(uint(ci.y)*19349663u ^ pcg(uint(ci.z)*83492791u)));
  if (u01(h) > 0.05) return vec3(0.);
  vec3 pos = vec3(ci) + 0.2 + 0.6*vec3(u01(pcg(h+1u)), u01(pcg(h+2u)), u01(pcg(h+3u)));
  float d = length(q - pos); float b = u01(pcg(h+4u)); b = b*b*b;
  return vec3(0.8 + 0.2*u01(pcg(h+5u)), 0.85, 1.)*b*smoothstep(0.16, 0.0, d)*0.55;
}
float cloudN(vec2 p){
  float s = 0., a = 0.5;
  for (int i = 0; i < 4; i++){ s += a*(vnoise(p + float(i)*17.).x + 0.5); p *= 2.1; a *= 0.5; }
  return s;
}
vec3 earthPix(vec3 rd){
  float cs = dot(rd, uE);
  float sr = sin(uEarthRad);
  vec3 pp = rd - uE*cs; float r = length(pp)/(sr*cs);
  if (cs < 0. || r >= 1.5) return vec3(-1.);
  float rr = min(r, 1.);
  vec3 n = normalize(pp + 1e-9)*rr - uE*sqrt(max(1. - rr*rr, 0.));
  vec3 a = vec3(dot(n, uC1), dot(n, uC2), dot(n, uC3));
  vec3 ef = a.x*uB1 + a.y*uB2 + a.z*uB3;
  float lat = asin(clamp(ef.z, -1., 1.)), lon = atan(ef.y, ef.x);
  vec2 uv = vec2(lon/6.28318530718 + 0.5, 0.5 - lat/3.14159265359);
  vec3 tex = pow(texture(uEarth, uv).rgb, vec3(2.2));
  float cl = smoothstep(0.46, 0.74, cloudN(uv*vec2(36., 18.)));
  tex = mix(tex, vec3(0.9, 0.92, 0.95), cl*0.85);
  float ndl = dot(n, uSun);
  float lam = smoothstep(-0.12, 0.45, ndl)*0.75 + max(ndl, 0.)*0.45;   // soft terminator from the atmosphere
  float mu = max(dot(n, -uE), 0.);
  float limb = pow(1. - mu, 2.5);
  vec3 col = tex*lam*4.2 + vec3(0.18, 0.42, 1.0)*limb*smoothstep(-0.1, 0.5, ndl)*1.6;
  float cov = 1. - smoothstep(0.992, 1.008, r);
  /* thin glow around the lit edge */
  float lim = max(dot(normalize(pp + 1e-9), normalize(uSun - uE*dot(uSun, uE) + 1e-9)), 0.);
  float halo = exp(-(r - 1.)*26.)*step(1., r)*(0.25 + 0.75*lim)*0.3*smoothstep(-0.9, 0.3, dot(uSun, -uE)*-1. + 0.2);
  return col*cov + vec3(0.35, 0.6, 1.0)*halo*(1. - cov);
}

void main(){
  vec2 fc = gl_FragCoord.xy;
  vec2 ndc = (fc - 0.5*uRes)/uRes.y*2.;
  vec3 rd = normalize(uF + uR*(ndc.x*uTan) + uU*(ndc.y*uTan));
  float pxAng = 2.*uTan/uRes.y;
  vec3 ro = uCam;
  vec3 col = vec3(0.);

  float t = 0.4, tPrev = 0.; bool hit = false;
  for (int i = 0; i < 480; i++){
    vec3 p = ro + rd*t;
    vec2 dxz = p.xz - ro.xz;
    float h = H(p.xz, t) - dot(dxz, dxz)/(2.*MR);
    float dy = p.y - h;
    if (dy < 0.){ hit = true; break; }
    if (rd.y > 0. && p.y > uZmax + 5.) break;
    tPrev = t;
    t += max(0.018*t + 0.25, 0.45*dy);
    if (t > 26000.) break;
  }
  if (hit){
    float a = tPrev, b = t;
    for (int k = 0; k < 8; k++){
      float m = 0.5*(a + b); vec3 p = ro + rd*m; vec2 dxz = p.xz - ro.xz;
      if (p.y < H(p.xz, m) - dot(dxz, dxz)/(2.*MR)) b = m; else a = m;
    }
    t = 0.5*(a + b);
    vec3 P = ro + rd*t; vec2 dxz = P.xz - ro.xz;
    float pf = max(t*pxAng, 0.002);
    float sp = t < 650. ? 5. : 20.;
    float hE = H(P.xz + vec2(sp, 0.), t), hW = H(P.xz - vec2(sp, 0.), t);
    float hN = H(P.xz + vec2(0., sp), t), hS = H(P.xz - vec2(0., sp), t);
    vec2 sl = vec2(hE - hW, hN - hS)/(2.*sp);                    // macro slope from real data
    float h0 = H(P.xz, t);
    vec3 dt = vec3(0.);
    if (t < 450.) dt = detail(P.xz, pf);
    vec2 slope = sl + dt.yz;
    vec3 upL = normalize(vec3(-dxz.x/MR, 1., -dxz.y/MR));       // local vertical at that spot
    vec3 n = normalize(vec3(-slope.x, 1., -slope.y));
    n = normalize(n + (upL - vec3(0., 1., 0.)));
    float sunUp = dot(uSun, upL);
    vec2 sh = normalize(uSun.xz + 1e-6);
    float tanEl = sunUp/sqrt(max(1. - sunUp*sunUp, 1e-6));
    /* long shadows from the real terrain (soft edge = real width of the solar disc) */
    float occ = -1.;
    float y0 = h0 + dt.x;
    float ts = 1.5;
    for (int i = 0; i < 260; i++){
      vec2 q = P.xz + sh*ts;
      float hq = H(q, t + ts) - ts*ts/(2.*MR);
      occ = max(occ, (hq - h0)/ts);
      if (occ > tanEl + 0.02) break;
      if (h0 + ts*tanEl > uZmax + 20.) break;
      ts += max(0.9, 0.022*ts);
      if (ts > 22000.) break;
    }
    float lit = clamp(0.5 + (tanEl - occ)/(2.*SUNR), 0., 1.);
    /* small shadows from rocks and crater rims */
    float mlit = 1.;
    if (t < 200. && lit > 0.){
      float sg = dot(sl, sh);
      float mo = -1e3;
      float fz = pf;
      for (int i = 0; i < 9; i++){
        float s = 0.14*pow(1.55, float(i));
        float dh = detail(P.xz + sh*s, pf).x - dt.x;
        mo = max(mo, dh/s + sg);
      }
      mlit = clamp(0.5 + (tanEl - mo)/(2.*0.012), 0., 1.);
    }
    lit *= mlit;
    float ndl = max(dot(n, uSun), 0.);
    float ndv = max(dot(n, -rd), 0.03);
    float ndlG = max(dot(normalize(vec3(-sl.x, 1., -sl.y)), uSun), 0.);
    float phase = acos(clamp(dot(uSun, -rd), -1., 1.));
    float surge = 1. + 0.9*exp(-phase/0.10);
    /* regolith brightness: mostly diffuse with a Lommel-Seeliger edge, plus the opposition surge */
    float f = (0.55*ndl + 0.45*ndl/(ndl + ndv + 1e-3))*surge;
    vec3 nl = vec3(vnoise(P.xz/9.).x, vnoise(P.xz/1.3 + 5.).x, vnoise(P.xz/0.35 + 3.).x);
    float v = 0.82 + 0.28*(nl.x*0.6 + nl.y*0.3 + nl.z*0.2)*2.;
    v *= 1. + 1.4*clamp(dt.x, -0.25, 0.25)*0.25;
    vec3 alb = vec3(0.52, 0.45, 0.385)*v;
    float amb = uShine*(0.55 + 0.45*n.y);
    col = alb*(f*lit*1.0 + amb);
    col *= uExp;
  } else {
    col = stars(rd);
    vec3 e = earthPix(rd);
    if (e.x >= 0.) col += e;
    col = col*1.0;
    float sc = dot(rd, uSun);
    if (uSun.y > -0.02){
      float ang = acos(clamp(sc, -1., 1.));
      float disc = 1. - smoothstep(0.00466, 0.0052, ang);
      float glow = 0.5*exp(-ang/0.012) + 0.12*exp(-ang/0.06);
      col += vec3(1., 0.98, 0.93)*(disc*40. + glow)*0.5;
    }
  }
  col *= 1.0;
  /* tone: soft shoulder, then display gamma */
  col = vec3(1.) - exp(-col*1.25);
  col = pow(col, vec3(1./2.2));
  float dn = fract(sin(dot(fc, vec2(12.9898, 78.233)))*43758.5453);
  col += (dn - 0.5)/255.;
  oc = vec4(col, 1.);
}
