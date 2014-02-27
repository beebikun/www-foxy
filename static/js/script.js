var mapH;
var menuSettings = { 
    hide : { h: 0, b: 'none'},
    normal: { h: 253, b: '1px solid #DADADA'}
};


/*--------------------//letsfox.html//------------------------*/



/*--------------------//payment-limit.html//------------------------*/


function enlargeLimit(){
    var data = new Object, inputs = document.getElementById('limit_form').getElementsByTagName('input');
    for (var i = inputs.length - 1; i >= 0; i--) {
        var el = inputs[i], name = el.getAttribute('name');
        if(name) data[name] = el.value
    }
    request({
        path: 'bglimit',
        post: true,
        data: data,
        success: function(data){document.getElementById('message').innerHTML = data.message}            
    });
}


/*--------------------------------------------*/

tagnameEach( 'table',  function(el){ addClass(el, "table table-bordered") } );
tagnameEach( 'img', function(el){ addClass(el, "img-responsive") });
tagnameEach( 'input', function(el){ el.setAttribute('autocomplete','off') }); //Если js отключен - то пусть хоть такая подсказка остается
node2array( document.getElementsByClassName('map') ).forEach(function(el){ showHideElBlock(el, true) });


function filterVisible(nodes){
    var vis = node2array(nodes).filter(function(el){return el.offsetWidth!==0});
    return vis.length ? vis[0] : undefined
}    
var streetInput = filterVisible(document.querySelectorAll('[name=street]'));
var numInput = filterVisible(document.querySelectorAll('[name=num]'));
var streetTips = document.getElementById('streetTips');    


(function(){
    //Open/close menu for mobile divices
    var mainMenu = document.getElementById('mainMenu');
    document.getElementById('collapseMenuBtn').onclick = function(e){
        window.scrollTo(0,0);
        var params = ( mainMenu.offsetHeight == menuSettings.normal.h ) ? menuSettings.hide : menuSettings.normal;
        animate(mainMenu, { height: params.h + 'px'}, 200);
        toggleClass(this, 'orange');
        toggleClass(document.getElementsByTagName('header')[0], 'static-header')
        toggleClass(mainMenu, 'static-header')
    }        
})();


(function(){
    //Hightigh a current content-menu item
    var contentmenu = document.getElementsByClassName('content-menu');
    var contentmenuEl = contentmenu.length ? node2array(contentmenu[0].getElementsByTagName('a')) : [];
    for (var i = contentmenuEl.length - 1; i >= 0; i--) {
        var a = contentmenuEl[i];
        if(a.getAttribute('href')==window.location.pathname) addClass(a, 'active');
    }        
})();


(function() {
	//Behavior in address building num input
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
})();


(function(){
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
            if(liActive.length) streetInput.value = liActive[0].innerText;
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
})();


$(document).ready(function(){
    (function(){
        //Find and set 2GisMap
        var mymap = document.getElementById('myMapId' )
        if( mymap ){
            function map_in_little_window(){
                var items = node2array(document.getElementById('simmularItems').getElementsByClassName('some-item')).length;
                if( window.innerWidth<712 && !items) showHideElBlock(mymap);
                else{
                    showHideElBlock(mymap, true);
                    if(window.mapH === undefined){
                        mapH = $(mymap).mapHelper()
                        mapH.getMarkers()
                    }
                }
            }
            map_in_little_window()
            window.onresize = map_in_little_window;
        }
    })();
})

