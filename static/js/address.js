function initAddresses() {
  // Behavior for address building num input
  if(!numInput) return
  numInput.onkeydown = function(e){
      var code = e.keyCode || e.which;
      if(code==27){//esc
          this.blur();
          return
      }
      if(code==13){//enter
          return
      }
  }

  //Behavior in address street name input
  if(!streetInput) return
  var ul = streetTips.getElementsByTagName('ul')[0];

  streetInput.onblur = function(){
      setTimeout(function () {showHideElBlock(streetTips); }, 100)
  }

  streetInput.onkeydown = function(e){
      var code = e.keyCode || e.which;
      if(code==27){//esc
          this.blur();
          return
      }
      if(code==13){//enter
          var liActive = node2array(ul.getElementsByClassName('active'));
          if(liActive.length) streetInput.value = liActive[0].innerText || liActive[0].innerHTML;
          return
      }
      if(code == 40 || code == 38){//40 - arrow down; 38 - arrow up
          (function(isUp){
              var lis = node2array(ul.getElementsByTagName('li'));
              var liActive = lis.filter(function(li){return hasClass(li, 'active')});
              var liNext = (function(){
                  var fn = isUp ? 'previousElementSibling' : 'nextElementSibling';
                  return liActive.length ? liActive[0][fn] : null;;
              })();
              for (var i = liActive.length - 1; i >= 0; i--) {
                  removeClass(liActive[i], 'active');
              };
              addClass(liNext ? liNext : lis[0], 'active');
          })(code == 38 ? true : false);
      } else{
          var newval = streetInput.value;
          if(newval.length < 3) return;
          ul.innerHTML = '';
          request({
              path: 'street',
              query: {name: newval},
              success: function(data){
                  var streetsVal = 2, streetLen = data.length;
                  if(streetLen==0) return;
                  for (var i = streetLen > streetsVal ? streetsVal : (streetLen - 1); i >= 0; i--) {
                      var el = document.createElement('li'), name = data[i].name;
                      el.innerHTML = name;
                      el.onclick = function(){streetInput.value = name;}
                      ul.appendChild(el);
                  };
                  showHideElBlock(streetTips, true);
              }
          })
      }
  }
}