/* Moon-frame physics: where the Sun and Earth are, as seen from any point on the Moon, at any date.
   Positions come from the astronomy-engine library (VSOP87 / ELP-based, about 1 arcminute).
   We only add the geometry that turns "directions in space" into "directions in the sky of a lunar site". */
(function(root){
var A=(typeof Astronomy!=='undefined')?Astronomy:require('astronomy-engine');
var RAD=Math.PI/180, DEG=180/Math.PI, I_INC=1.54242*RAD;   // tilt of the Moon's equator to the ecliptic
function wrap180(x){x=((x+180)%360+360)%360-180;return x}
function lonlat(v){return {lon:((Math.atan2(v.y,v.x)*DEG)+360)%360,lat:Math.atan2(v.z,Math.hypot(v.x,v.y))*DEG}}
/* Meeus ch.53: turn an ecliptic direction (as seen from the Moon's surface side) into a Moon-fixed latitude and longitude. */
function selen(lonDeg,latDeg,T){
  var F=(93.2720993+483202.0175273*T-0.0034029*T*T)*RAD, Om=(125.0445479-1934.1362891*T+0.0020754*T*T)*RAD;
  var W=lonDeg*RAD-Om,b=latDeg*RAD;
  var Aa=Math.atan2(Math.sin(W)*Math.cos(b)*Math.cos(I_INC)-Math.sin(b)*Math.sin(I_INC),Math.cos(W)*Math.cos(b));
  var l=wrap180((Aa-F)*DEG), sb=-Math.sin(W)*Math.cos(b)*Math.sin(I_INC)-Math.sin(b)*Math.cos(I_INC);
  return {lon:l,lat:Math.asin(Math.max(-1,Math.min(1,sb)))*DEG};
}
/* Sub-Earth and sub-solar points on the Moon at a date (JS Date). */
function state(date){
  var t=new A.AstroTime(date), T=t.tt/36525;     // tt = days since J2000 (TT)
  var m=A.Ecliptic(A.GeoMoon(t)).vec, s=A.Ecliptic(A.GeoVector('Sun',t,true)).vec;
  var ml=lonlat(m), earth=selen(ml.lon,ml.lat,T);
  var hm={x:m.x-s.x,y:m.y-s.y,z:m.z-s.z}, hl=lonlat(hm), sun=selen(hl.lon,hl.lat,T);
  return {earth:earth,sun:sun,distKm:Math.hypot(m.x,m.y,m.z)*149597870.7,time:t};
}
/* Elevation and azimuth (azimuth from local north, toward east) of a body whose sub-point is (subLat,subLon), seen from a lunar site. */
function look(lat,lon,subLat,subLon){
  var p=lat*RAD,l=lon*RAD,d=subLat*RAD,L=subLon*RAD;
  var sinEl=Math.sin(p)*Math.sin(d)+Math.cos(p)*Math.cos(d)*Math.cos(l-L);
  var east=Math.cos(d)*Math.sin(L-l), north=Math.cos(p)*Math.sin(d)-Math.sin(p)*Math.cos(d)*Math.cos(L-l);
  return {el:Math.asin(Math.max(-1,Math.min(1,sinEl)))*DEG,az:((Math.atan2(east,north)*DEG)+360)%360};
}
/* The Moon (and Sun) in the sky of a person on Earth. */
function moonFromEarth(date,latDeg,lonDeg){
  var obs=new A.Observer(latDeg,lonDeg,0),t=new A.AstroTime(date);
  function hz(body){var eq=A.Equator(body,t,obs,true,true),h=A.Horizon(t,obs,eq.ra,eq.dec,'normal');return {az:h.azimuth,el:h.altitude,ra:eq.ra,dec:eq.dec}}
  var ill=A.Illumination('Moon',t);
  return {moon:hz('Moon'),sun:hz('Sun'),phaseDeg:A.MoonPhase(t),fraction:ill.phase_fraction,distKm:ill.geo_dist*149597870.7,
          nextQuarter:A.SearchMoonQuarter(t)};
}
var P={state:state,look:look,moonFromEarth:moonFromEarth,selen:selen,wrap180:wrap180,Astronomy:A};
if(typeof module!=='undefined')module.exports=P;else root.MoonPhysics=P;
})(this);
