var mapH;
var street;
var num;
var templateLoadFn;
/*--------------------Buttons Section----------------*/

function initRadioButtons(){
	//Превращает все нужные кнопки в радио
    node2array(document.querySelectorAll('[type=radio]')).forEach(function(input){
        var btnGroup = findParent('[data-toggle="buttons"]', input);
        var label = findParent('.btn', input);
        var labels = node2array(btnGroup.getElementsByClassName('btn'))
        input.onclick = function(){
            labels.forEach(function(el){removeClass(el, 'active')})
            addClass(label, 'active')
        }
    });
}
/*------------------Map Section-----------------*/

function initMap(){
    //Find and set 2GisMap
    var mapId = 'myMapId';
    var mymap = document.getElementById(mapId);
    if( mymap ){
        function map_in_little_window(){
            var items = node2array(document.getElementById('simmularItems').getElementsByClassName('some-item')).length;
            if( window.innerWidth<712 && !items){
                showHideElBlock(mymap)
            } else{
                showHideElBlock(mymap, true);
                if( window.mapH === undefined ) mapH = new M(mapId, num, street);
            }
        }
        map_in_little_window();
        window.onresize = map_in_little_window;
    }
}

/*-----------------------------------------------------------*/


window.onload = function(){
    if (templateLoadFn) {
        templateLoadFn();
    }
    initMap();
    initModal();

    tagnameEach( 'table',  function(el){ addClass(el, "table table-bordered") } );
    tagnameEach( 'img', function(el){ addClass(el, "img-responsive") });
    // Если js отключен - то пусть хоть такая подсказка остается
    tagnameEach( 'input', function(el){ el.setAttribute('autocomplete','off') });


    (function(){
        // Open/close menu for mobile divices
        var body = document.getElementsByTagName('body')[0];
        document.getElementById('collapseMenuBtn').onclick = function(e){
            //window.scrollTo(0,0);
            toggleClass( body, 'unwrap' );
        }
    })();


    (function(){
        // Highlight a current content-menu item
        var contentmenu = document.getElementsByClassName('content-menu');
        var contentmenuEl = contentmenu.length ? node2array(contentmenu[0].getElementsByTagName('a')) : [];
        var path = window.location.pathname;
        for (var i = contentmenuEl.length - 1; i >= 0; i--) {
            var a = contentmenuEl[i];
            if(a.getAttribute('href')==path) addClass(a, 'active');
        }
    })();
}



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
        success: function(data){
            document.getElementById('message').innerHTML = data.message
        }
    });
}


/*--------------------//payment-terminal.html//------------------------*/

function selectPayment(){
    if( window.mapH === undefined ) return
    function showHideGroup(group, show){
        for (var i = group.getAll.length - 1; i >= 0; i--) {
            var val = group.getAll[i].val;
            showhideEl(val.id, show)
        };
        if(show) group.show();
        else group.hide();
    }
    var payment = this.options[this.selectedIndex].value;
    if( payment ){
        for(var name in mapH.markerGroups){
            if(mapH.markerGroups.hasOwnProperty(name))
                showHideGroup( mapH.markerGroups[name], name == payment );
        }
    } else{
        for (var name in mapH.markerGroups){
            showHideGroup(mapH.markerGroups[name], true)
        };
    }
}


function searchPaymentTermonal(e){
    if( window.mapH === undefined ) return
    var code = e.keyCode || e.which;
    if( code==27 ){/*esc*/
        this.blur();
        return
    }
    var key = this.value, markersList = mapH.map.markers.getAll();
    function showHideMarker(m, show){
        showhideEl(m.val.id, show);
        if(show) m.show();
        else m.hide();
    }
    for (var i = markersList.length - 1; i >= 0; i--) {
        var m = markersList[i];
        if(key.length>2){
            var key = key.toLowerCase(), query = m.val.query.toLowerCase();
            if( !(query.indexOf(key)+1) ) showHideMarker(m);
            else showHideMarker(m, true)
        } else{
            showHideMarker(m, true)
        }
    };
}

