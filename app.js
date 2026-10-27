/* PRO iURE – výber služby (rámček sa len zvýrazní), logo tmavé/červené, menu na mobile */
(function(){
  var tiles=[].slice.call(document.querySelectorAll('.tile')),dets=[].slice.call(document.querySelectorAll('.det'));
  tiles.forEach(function(t){t.addEventListener('click',function(e){
    e.preventDefault();
    var was=t.classList.contains('sel'),id='s-'+t.dataset.open;
    tiles.forEach(function(x){x.classList.toggle('sel',!was&&x===t);x.setAttribute('aria-expanded',String(!was&&x===t))});
    dets.forEach(function(d){d.classList.toggle('on',!was&&d.id===id)});
    if(!was){var d=document.getElementById(id);d.scrollIntoView({behavior:'smooth',block:'nearest'});d.focus({preventScroll:true})}
  })});
  var lb=document.getElementById('logo-farba');
  if(lb)lb.addEventListener('click',function(){
    var o=!document.querySelector('.logo').classList.contains('or');
    document.querySelectorAll('.logo').forEach(function(l){l.classList.toggle('or',o)});
    lb.textContent=o?'Logo: prepnúť na tmavé':'Logo: prepnúť na červené';
  });
  var b=document.querySelector('.burger'),n=document.getElementById('menu');
  if(b&&n){
    b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',String(o))});
    n.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('open');b.setAttribute('aria-expanded','false')}});
  }
})();
