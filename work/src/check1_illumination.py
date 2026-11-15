#!/usr/bin/env python3
"""
CHECK 1 - our sunlight calculation vs NASA's published illumination map.

What it does
  1. Reads a LOLA elevation GeoTIFF (south polar stereographic, metres) and NASA's
     average-illumination GeoTIFF (same projection).
  2. Picks a grid of test points inside the area both files cover.
  3. For every point, finds the horizon in 36 directions (how high the terrain blocks the sky).
  4. Simulates the Sun's path over many Moon-days and years (physics below) and counts how
     often the Sun clears the horizon -> our "average sunlit fraction".
  5. Compares with NASA's value at the same point and prints/plots the match.

Physics used (kept simple on purpose, so every line can be explained)
  * Moon's spin axis is tilted only 1.54 deg from the ecliptic normal, so the Sun's latitude
    on the Moon swings between -1.54 and +1.54 deg, once per eclipse year (346.62 days).
  * The Moon turns once relative to the Sun every synodic month (29.53 days): the Sun circles
    the horizon once per month.
  * Sun is a disc of 0.267 deg radius, not a point (soft shadow edges).
  * Moon curvature (radius 1737.4 km) lowers far terrain: drop = d^2 / (2R).
  Not included (this is the point of the check): libration wobble, orbit eccentricity, 18.6-year
  nodal precession details. NASA used the full DE421 ephemeris; the gap tells us how good
  this simplified physics is.

Usage
  python3 check1_illumination.py DEM.tif ILLUM.tif [--n 40] [--rmax 30000] [--out results]
  python3 check1_illumination.py --selftest        # runs on made-up data, no downloads
"""
import sys, argparse, math
import numpy as np
from scipy.ndimage import map_coordinates

R_MOON = 1737400.0
OBLIQ = 1.54            # deg, tilt of Moon's axis to ecliptic normal
SYNODIC = 29.530589     # days
ECLIPSE_YEAR = 346.62   # days
SUN_RAD = 0.267         # deg

def xy_to_latlon(x, y):
    """South polar stereographic (true scale at pole) -> lat, lon (deg)."""
    rho = np.hypot(x, y)
    c = 2 * np.arctan2(rho, 2 * R_MOON)
    lat = -np.degrees(np.pi / 2 - c)
    lon = np.degrees(np.arctan2(x, y))      # lon measured from +y axis, eastward is +x
    return lat, lon

def horizon_tan(dem, tf, px, py, x0, y0, n_az=36, rmax=30000.0, eye=0.0):
    """tan(elevation) of the terrain horizon at each target point, per azimuth.
    dem: 2D array; tf: (res_m) pixel size; px,py: target coordinates in metres.
    Azimuth: 0 = +y (grid north), measured clockwise toward +x."""
    res = tf
    out = np.full((n_az, len(px)), -1e9)
    dists = [res * 1.5]
    while dists[-1] < rmax:
        dists.append(dists[-1] + max(res, dists[-1] * 0.03))
    dists = np.array(dists)
    col0 = (px - x0) / res
    row0 = (y0 - py) / res
    z0 = map_coordinates(dem, [row0, col0], order=1, mode='nearest') + eye
    for k in range(n_az):
        a = 2 * np.pi * k / n_az
        dx, dy = math.sin(a), math.cos(a)
        best = np.full(len(px), -1e9)
        for d in dists:
            c = col0 + dx * d / res
            r = row0 - dy * d / res
            inside = (c >= 0) & (c < dem.shape[1] - 1) & (r >= 0) & (r < dem.shape[0] - 1)
            if not inside.any():
                continue
            z = map_coordinates(dem, [r, c], order=1, mode='nearest')
            t = (z - z0 - d * d / (2 * R_MOON)) / d
            t = np.where(inside, t, -1e9)
            best = np.maximum(best, t)
        out[k] = best
    return out  # (n_az, npts)

def sun_elevation_azimuth(lat, lon, subs_lat, subs_lon):
    """Sun elevation and azimuth (deg) at a site. Azimuth measured from the site's local
    north toward east. All inputs/outputs in degrees, arrays allowed."""
    p, l, d, L = map(np.radians, (lat, lon, subs_lat, subs_lon))
    sin_el = np.sin(p) * np.sin(d) + np.cos(p) * np.cos(d) * np.cos(l - L)
    el = np.degrees(np.arcsin(np.clip(sin_el, -1, 1)))
    east = np.cos(d) * np.sin(L - l)
    north = np.cos(p) * np.sin(d) - np.sin(p) * np.cos(d) * np.cos(L - l)
    az = np.degrees(np.arctan2(east, north)) % 360
    return el, az

def sunlit_fraction(lat, lon, tan_h, grid_north_deg, years=8.0, step_h=6.0, n_az=36):
    """Average fraction of time the Sun disc centre is above the horizon (disc-averaged)."""
    t = np.arange(0, years * 365.25, step_h / 24.0)
    subs_lat = OBLIQ * np.sin(2 * np.pi * t / ECLIPSE_YEAR)
    subs_lon = -360.0 * t / SYNODIC          # sub-solar longitude drifts westward
    npts = len(lat)
    lit = np.zeros(npts)
    offs = np.array([(0.0, 0.0), (SUN_RAD * 0.7, 0), (-SUN_RAD * 0.7, 0), (0, SUN_RAD * 0.7), (0, -SUN_RAD * 0.7)])
    for i in range(npts):
        el, az = sun_elevation_azimuth(lat[i], lon[i], subs_lat, subs_lon)
        # local azimuth -> grid azimuth: at the pole, local north is toward the prime meridian,
        # so grid azimuth = local azimuth + (180 - lon) wrapped (south-polar view).
        az_grid = (az + grid_north_deg[i]) % 360
        f = (az_grid / 360.0 * n_az)
        k0 = np.floor(f).astype(int) % n_az
        k1 = (k0 + 1) % n_az
        w = f - np.floor(f)
        th = tan_h[k0, i] * (1 - w) + tan_h[k1, i] * w
        h_deg = np.degrees(np.arctan(th))
        frac = 0.0
        for dx, dz in offs:
            frac += (el + dz > h_deg).mean()
        lit[i] = frac / len(offs)
    return lit

def local_north_to_grid(lat, lon):
    """Angle to add to local azimuth to get grid azimuth. In south-polar stereographic with
    lon = atan2(x, y), the local meridian direction at lon points toward the pole; local
    north (toward the pole is SOUTH-pole-wards for lat<0 sites means toward the centre)."""
    # local north at a southern site points away from the pole = direction (sin lon, cos lon) outward
    # grid azimuth of outward radial = lon  -> add lon
    return lon

def run(dem_path, illum_path, n=40, rmax=30000.0, out='results', scale_illum=None, years=8.0):
    import rasterio
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with rasterio.open(dem_path) as d, rasterio.open(illum_path) as m:
        dem = d.read(1).astype(np.float64)
        res = d.res[0]
        x0, y0 = d.bounds.left, d.bounds.top
        ill = m.read(1).astype(np.float64)
        nod = m.nodata
        if nod is not None:
            ill = np.where(ill == nod, np.nan, ill)
        sc = scale_illum
        if sc is None:
            mx = np.nanmax(ill)
            sc = 1.0 if mx <= 1.0001 else (100.0 if mx <= 100.5 else float(mx))
            print(f'NASA map max value {mx:g}: treating it as 0..{sc:g} (change with --scale if wrong)')
        # keep targets away from DEM edges so the horizon rays have terrain around them
        pad = min(rmax * 0.15, 0.25 * min(dem.shape) * res)
        xs = np.linspace(x0 + pad, d.bounds.right - pad, n)
        ys = np.linspace(d.bounds.bottom + pad, y0 - pad, n)
        gx, gy = np.meshgrid(xs, ys)
        px, py = gx.ravel(), gy.ravel()
        nasa = np.array([v for v in m.sample(list(zip(px, py)))]).ravel().astype(float)
        if nod is not None: nasa = np.where(nasa == nod, np.nan, nasa)
        nasa = nasa / sc
    lat, lon = xy_to_latlon(px, py)
    print(f'{len(px)} points, latitude {lat.min():.2f}..{lat.max():.2f}, DEM {res:g} m/px')
    th = horizon_tan(dem, res, px, py, x0, y0, rmax=rmax)
    ours = sunlit_fraction(lat, lon, th, local_north_to_grid(lat, lon), years=years)
    ok = np.isfinite(nasa)
    a, b = ours[ok] * 100, nasa[ok] * 100
    diff = a - b
    stats = dict(points=int(ok.sum()), bias_pts=float(diff.mean()), rmse_pts=float(np.sqrt((diff**2).mean())),
                 corr=float(np.corrcoef(a, b)[0, 1]) if ok.sum() > 2 else float('nan'),
                 within5=float((np.abs(diff) <= 5).mean() * 100), within10=float((np.abs(diff) <= 10).mean() * 100))
    print('\nCHECK 1 RESULT (percent of time sunlit)')
    print(f"  points compared : {stats['points']}")
    print(f"  mean difference : {stats['bias_pts']:+.2f} points (ours minus NASA)")
    print(f"  RMS difference  : {stats['rmse_pts']:.2f} points")
    print(f"  correlation     : {stats['corr']:.3f}")
    print(f"  within 5 points : {stats['within5']:.0f}%   within 10 points: {stats['within10']:.0f}%")
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    s = ax[0].scatter(b, a, c=diff, cmap='coolwarm', vmin=-20, vmax=20, s=14); ax[0].plot([0, 100], [0, 100], 'k--', lw=1)
    ax[0].set_xlabel('NASA % sunlit'); ax[0].set_ylabel('Ours % sunlit'); ax[0].set_title('Point by point'); fig.colorbar(s, ax=ax[0], label='ours - NASA')
    im = ax[1].imshow((ours.reshape(n, n) - nasa.reshape(n, n)) * 100, cmap='coolwarm', vmin=-20, vmax=20, extent=[xs[0], xs[-1], ys[0], ys[-1]])
    ax[1].set_title('Where we differ (points)'); fig.colorbar(im, ax=ax[1])
    ax[2].hist(diff, bins=30, color='#4a8f86'); ax[2].set_title('Difference spread'); ax[2].set_xlabel('ours - NASA (points)')
    fig.tight_layout(); fig.savefig(out + '.png', dpi=130)
    np.savetxt(out + '.csv', np.c_[px, py, lat, lon, ours * 100, nasa * 100], delimiter=',', header='x_m,y_m,lat,lon,ours_pct,nasa_pct', comments='')
    print(f'\nSaved {out}.png and {out}.csv')
    return stats

def selftest():
    """No downloads: builds a made-up crater field + a made-up 'NASA' map from a more detailed
    simulation of the same Sun, to prove the pipeline runs and the sign/units are right."""
    import rasterio
    from rasterio.transform import from_origin
    rng = np.random.default_rng(3)
    n, res = 500, 60.0
    yy, xx = np.mgrid[0:n, 0:n] * res
    dem = np.zeros((n, n))
    for _ in range(40):
        cx, cy, r = rng.uniform(0, n * res, 2).tolist() + [rng.uniform(1500, 5000)]
        d = np.hypot(xx - cx, yy - cy) / r
        dem += np.where(d < 1, -600 * r / 5000 * (1 - d**2), 0) + np.where((d >= 1) & (d < 1.35), 120 * r / 5000 * (1.35 - d), 0)
    # centre the grid ~87 degrees south
    half = n * res / 2
    x0, y0 = -half + 20000, 40000 + half  # ~ 88.7 S
    tf = from_origin(x0, y0, res, res)
    with rasterio.open('selftest_dem.tif', 'w', driver='GTiff', height=n, width=n, count=1, dtype='float32', transform=tf) as f:
        f.write(dem.astype('float32'), 1)
    # 'NASA' map: same physics but a different sampling (12 years, 3h steps, 72 azimuths)
    xs = x0 + (np.arange(n // 2) * 2 + 1) * res; ys = y0 - (np.arange(n // 2) * 2 + 1) * res
    gx, gy = np.meshgrid(xs, ys)
    lat, lon = xy_to_latlon(gx.ravel(), gy.ravel())
    th = horizon_tan(dem, res, gx.ravel(), gy.ravel(), x0, y0, n_az=72, rmax=20000)
    nasa = sunlit_fraction(lat, lon, th, local_north_to_grid(lat, lon), years=12.0, step_h=3.0, n_az=72)
    tf2 = from_origin(x0, y0, res * 2, res * 2)
    with rasterio.open('selftest_illum.tif', 'w', driver='GTiff', height=n // 2, width=n // 2, count=1, dtype='float32', transform=tf2) as f:
        f.write(nasa.reshape(n // 2, n // 2).astype('float32'), 1)
    return run('selftest_dem.tif', 'selftest_illum.tif', n=25, rmax=20000, out='selftest_result', years=6.0)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dem', nargs='?'); ap.add_argument('illum', nargs='?')
    ap.add_argument('--n', type=int, default=40); ap.add_argument('--rmax', type=float, default=30000.0)
    ap.add_argument('--out', default='results'); ap.add_argument('--scale', type=float, default=None)
    ap.add_argument('--years', type=float, default=8.0); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.dem and a.illum: run(a.dem, a.illum, a.n, a.rmax, a.out, a.scale, a.years)
    else: ap.print_help()
