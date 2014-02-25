var mapH;
var menuSettings = { 
    hide : { h: 0, b: 'none'},
    normal: { h: 253, b: '1px solid #DADADA'}
};

function showhideEl(id, show){
    var el = typeof id == 'string' ? document.getElementById(id) : id;
    el.getElementById(id).style.display = show ? 'inline-block' : 'none'
}

function showHideElBlock(id, show){
    var el = typeof id == 'string' ? document.getElementById(id) : id;
    el.style.display = show ? 'inline-block' : 'none'
}

function trim(str){
    return str.trim ? str.trim() : str.replace(/^\s+|\s+$/g, '');
}

function splitWords(str){
    return trim(str).split(/\s+/);
}

function getClass(el) {
    return el.className.baseVal === undefined ? el.className : el.className.baseVal;
}

function setClass(el, name) {
    if (el.className.baseVal === undefined) {
        el.className = name;
    } else {
        el.className.baseVal = name;
    }
}

function hasClass(el, name) {
    if (el.classList !== undefined) {
        return el.classList.contains(name);
    }
    var className = getClass(el);
    return className.length > 0 && new RegExp('(^|\\s)' + name + '(\\s|$)').test(className);
}

function addClass(id, name){
    var el = typeof id == 'string' ? document.getElementById(id) : id;
    if (el.classList !== undefined) {
        var classes = splitWords(name);
        for (var i = 0, len = classes.length; i < len; i++) {
            el.classList.add(classes[i]);
        }
    } else if (!hasClass(el, name)) {
        var className = getClass(el);
        setClass(el, (className ? className + ' ' : '') + name);
    }
}

function removeClass (el, name) {
    if (el.classList !== undefined) {
        el.classList.remove(name);
    } else {
        setClass(el, trim((' ' + getClass(el) + ' ').replace(' ' + name + ' ', ' ')));
    }
}


function toggleClass(el, name){
    if(hasClass(el, name)) removeClass(el, name)
    else addClass(el, name)
}


function animate(el, params, duration) {
    var s = 10;
    function _animate(fn) {  
        var start = new Date; // сохранить время начала 
        var timer = setInterval(function() {
            // вычислить сколько времени прошло
            var progress = (new Date - start) / duration;
            if (progress > 1) progress = 1;
            // отрисовать анимацию
            fn(progress);
            if (progress == 1) clearInterval(timer); // конец
          }, s); // по умолчанию кадр каждые 10мс
    }
    var style = window.getComputedStyle(el);
    for(var p in params){
    	var start = parseInt(style[p]);
        var dif = parseInt(params[p])- start;
        _animate(function(progress){        	
        	var newval = start + dif*progress;
            el.style[p] =  newval + 'px';
        });
    }
}


function request(params){
    function serialize(obj){
        var str = new Array;
        for(var p in obj){
            if (obj.hasOwnProperty(p)) str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        }
        return str.join("&");
    }
    var path = params.path ? api[params.path] : '', success = params.success, error = params.error, method = params.post ? 'POST' : 'GET',
        data = params.post ? params.data ? params.data : {} : null;
    var xhr = new XMLHttpRequest();
    if(error===undefined)var error = function(e){console.log(e.data)};
    xhr.open(method, path, true);
    if(data){
        xhr.setRequestHeader('X-CSRF-Token', data.csrfmiddlewaretoken);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        var data = serialize(data);
    }     
    //xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.onerror = error;
    xhr.onload = function(e){
        try{var r = eval("("+xhr.responseText+")");}
        catch(e){var r = {'exception': e}}
        finally{
            if(r.exception===undefined&&(xhr.status==200||xhr.status==201)) var obj = {fn:success, r:r.data}
            else var obj = {fn:error, r:r}
            if(obj.fn) obj.fn(obj.r);
        }
    };
    xhr.send(data);
    /*$.post( path, data, success);*/
}

function getStreets(name){

}

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

function node2array(nodes){
    return Array.prototype.slice.call(nodes)
}

function tagnameEach(tag, fn){
    node2array( document.getElementsByTagName(tag) ).forEach(fn)
}

$(document).ready(function(){
    tagnameEach( 'table',  function(el){ addClass(el, "table table-bordered") } );
    tagnameEach( 'img', function(el){ addClass(el, "img-responsive") });
    tagnameEach( 'input', function(el){ el.setAttribute('autocomplete','off') }); //Если js отключен - то пусть хоть такая подсказка остается
    node2array( document.getElementsByClassName('.map') ).forEach(function(el){ showHideElBlock(el, true) });

    (function(){
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
	    var contentmenu = document.getElementsByClassName('content-menu'), contentmenuEl = contentmenu ? node2array(contentmenu[0].getElementsByTagName('a')) : [];
	    for (var i = contentmenuEl.length - 1; i >= 0; i--) {
	        var a = contentmenuEl[i];
	        if(a.getAttribute('href')==window.location.pathname) addClass(a, 'active')
	    }    	
    })();


    (function(){
    	var mymap = document.getElementById('myMapId' )
	    if( mymap ){
	        function map_in_little_window(){
	        	var items = node2array(document.getElementById('simmularItems').getElementsByClassName('some-item')).length;
	            if( $(window).width()<712 && !items) showHideElBlock(mymap);
	            else{
	                showHideElBlock(mymap, true);
	                if(window.mapH === undefined){
	                    mapH = $(mymap).mapHelper()
	                    mapH.getMarkers()
	                }
	            }
	        }
	        map_in_little_window()
	        $(window).resize(function(){map_in_little_window()})
	    }    	
    })();


    function filterVisible(nodes){
        var vis = node2array(nodes).filter(function(el){return el.offsetWidth!==0})
        return vis.length ? vis[0] : undefined
    }

    var api = $().apiHelper();
    var $streetInput = $(streetInputID); var $numInput = $(numInputID); var $streetTips = $(streetTipsID);
    var streetInput = filterVisible(document.querySelectorAll('[name=street]'));
    var numInput = filterVisible(document.querySelectorAll('[name=num]'));
    var streetTips = document.getElementById('streetTips');    

    (function() {
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
		if(!streetInput) return
		function ruleTipsWithArrow(code){
	        var tips = streetTipsID + ' ul .active';
	        var first = streetTipsID + ' ul li:first-child';
	        if ($(tips).next().length) {$(tips).next().addClass('active').end().removeClass('active');}
	        else {
	            $(tips).removeClass('active');
	            $(first).addClass('active');
	        }
	    }
	    streetInput.onkeydown = function(e){
	        var code = e.keyCode || e.which;
	        if(code==27){//esc
	            $(this).blur();
	            return
	        }
	        if(code==13){//enter
	            var $active = $(streetTipsID + ' ul .active')
	            if($active.length){
	                $streetInput.val($active.text())
	                if(!$numInput.val()){
	                    $numInput.focus();
	                    return
	                }
	            }
	            return
	        }
	        if(code==40){//arrow down
	            ruleTipsWithArrow(40);
	        }
	        else if(code==38){//arrow up
	            ruleTipsWithArrow(38);
	        }
	        else{
	            var newval = $streetInput.val();
	            if(newval.length<3) return;
	            $streetTips.find('ul').empty();
	            $.getJSON(api.street,{name:newval},
	                function(data){
	                    if(data.data.length==0) return;
	                var street_names = data.data.slice(0,2)
	                    $.each(street_names, function(key, val){
	                        var elemID = 'streetID_' + key.toString()
	                        var elem = '<li id="' + elemID + '">'+ val.name + '</li>'                    
	                        $streetTips.find('ul').append(elem)
	                        document.getElementById(elemID).onclick = function(){streetInput.value = val.name;}
	                    })
	                    $streetTips.show();
	                });
	          }        
	    }

	    streetTips.onblur = function(){
	        setTimeout(function () {$streetTips.hide() }, 100)
	    }
	})();

})

