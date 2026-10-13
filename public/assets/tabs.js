/* Abschnitts-Tabs auf Kartenseiten: antippen oder links/rechts wischen.
   Ohne JavaScript bleiben alle Abschnitte sichtbar (gut für SEO und Barrierefreiheit). */
(function(){
  var nav=document.querySelector('.secnav'); if(!nav) return;
  var links=[].slice.call(nav.querySelectorAll('a[data-sec]'));
  var secs=links.map(function(a){return document.getElementById(a.getAttribute('data-sec'));});
  if(!secs.length || secs.some(function(s){return !s;})) return;
  document.documentElement.classList.add('tabs-on');
  var cur=0;
  secs.forEach(function(s,i){
    var bar=document.createElement('div'); bar.className='tabnext';
    if(i>0){var p=document.createElement('a');p.href='#'+secs[i-1].id;p.className='btn ghost';p.textContent='← '+links[i-1].textContent;p.onclick=function(e){e.preventDefault();show(i-1,true);};bar.appendChild(p);}
    if(i<secs.length-1){var n=document.createElement('a');n.href='#'+secs[i+1].id;n.className='btn';n.textContent='Weiter: '+links[i+1].textContent+' →';n.onclick=function(e){e.preventDefault();show(i+1,true);};bar.appendChild(n);}
    s.appendChild(bar);
  });
  function show(i,scroll){
    if(i<0||i>=secs.length) return; cur=i;
    secs.forEach(function(s,j){s.classList.toggle('tab-hidden',j!==i);});
    links.forEach(function(a,j){a.classList.toggle('on',j===i);a.setAttribute('aria-selected',j===i?'true':'false');});
    var a=links[i]; nav.scrollTo({left:a.offsetLeft-nav.offsetWidth/2+a.offsetWidth/2,behavior:'smooth'});
    if(history.replaceState) history.replaceState(null,'','#'+secs[i].id);
    if(scroll){var y=nav.getBoundingClientRect().top+window.scrollY-70; if(window.scrollY>y) window.scrollTo({top:y,behavior:'smooth'});}
  }
  nav.setAttribute('role','tablist');
  links.forEach(function(a,i){a.setAttribute('role','tab');a.addEventListener('click',function(e){e.preventDefault();show(i,true);});});
  // Wischen
  var x0=null,y0=null;
  secs.forEach(function(s){
    s.addEventListener('touchstart',function(e){var t=e.touches[0];x0=t.clientX;y0=t.clientY;},{passive:true});
    s.addEventListener('touchend',function(e){ if(x0===null) return; var t=e.changedTouches[0],dx=t.clientX-x0,dy=t.clientY-y0; x0=null;
      if(Math.abs(dx)>60 && Math.abs(dx)>Math.abs(dy)*1.5){ if(e.target.closest&&e.target.closest('.tbl')) return; show(cur+(dx<0?1:-1),true);} },{passive:true});
  });
  function fromHash(){ var h=location.hash.slice(1), k=secs.findIndex(function(s){return s.id===h;}); if(k>=0 && k!==cur) show(k,true); return k; }
  window.addEventListener('hashchange',fromHash);
  var k0=secs.findIndex(function(s){return s.id===location.hash.slice(1);});
  show(k0>=0?k0:0,false);
})();
