var mapH;
var menuSettings = {
    hide : { h: 0, b: 'none'},
    normal: { h: 253, b: '1px solid #DADADA'}
};
var streetInput = filterVisible(document.querySelectorAll('[name=street]'));
var numInput = filterVisible(document.querySelectorAll('[name=num]'));
var streetTips = document.getElementById('streetTips');

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
                if( window.mapH === undefined ) mapH = new M(mapId, numInput, streetInput);
            }
        }
        map_in_little_window();
        window.onresize = map_in_little_window;
    }
}

/*-----------------------------------------------------------*/


window.onload = function(){
    initMap();
    initModal();
    initAddresses();

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



/*--------------------//letsfox.html//------------------------*/
function createCaptcha(id){
    var captcha = document.getElementById(id);
    captcha.innerHTML = '';
    request({
        path: 'captcha',
        success: function(data){
            if(!data || data.length == 0) return;
            document.querySelectorAll('[name=captcha_key]').value = data.key;
            for (var i = 0; i < data.images.length; i++) {
                var val = data.images[i]
                captcha.innerHTML = [captcha.innerHTML, '<label class="btn btn-default mybtn">',
                                     '<input type="radio" name="captcha" value="', val.name, '">',
                                     '<img src="', val.src, '" >', '</label>'].join('');
            };
            initRadioButtons()
        }
    });
}

function doitOkBtnClick(e){
    var form = findParent('form', this);
    var data = new Object;
    var inputs = filterNodes(form.getElementsByTagName('input'),
                             function(input){return input.getAttribute('name')});

    inputs.forEach(function(input){
        var t = input.getAttribute('type');
        if(t !='radio' || (t =='radio' && input.parentNode.className.indexOf('active') >= 0) ){
            data[input.getAttribute('name')] = t == 'checkbox' ? input.checked : input.value
        }
    });
    node2array( document.querySelectorAll('.btn') ).forEach(function(el){el.setAttribute('disabled', true) });
    request({
        post: true,
        path: 'doit',
        data: data,
        success: function(data){
            node2array( document.querySelectorAll('.btn') ).forEach(function(el){
                el.removeAttribute('disabled')
            });
            node2array( document.querySelectorAll('.has-error') ).forEach(function(el){
                removeClass( el, 'has-error');
            });
            node2array( document.querySelectorAll('.help-error') ).forEach(function(el){showHideElBlock(el);});
            if(data.doit === undefined){
                for(var field in data){
                    var err = data[field];
                    var errInput = document.querySelector('[name=' + field + ']');
                    var formGroup =  findParent('.form-group', errInput);
                    addClass( formGroup, 'has-error');
                    var errText = formGroup.getElementsByClassName( 'help-error' )[0];
                    showHideElBlock(errText, true)
                    errText.innerText = err;
                }
            } else {
                showHideModal( document.getElementById('doit') );
                showHideModal( document.getElementById('doitOk'), true );
            }
            createCaptcha('captcha');
        }
    });
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
        success: function(data){document.getElementById('message').innerHTML = data.message}
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

/*---------------------------------//rates.html//-----------------------------*/


function initShapeHover() {
    var speed = 330,
        easing = mina.backout;

    [].slice.call ( document.querySelectorAll( '.shapehover-item' ) ).forEach( function( el ) {
        var svg = el.querySelector( 'svg' ), path = svg ? svg.querySelector('path') : null;
        if(!path) return
        var s = Snap( el.querySelector( 'svg' ) ), path = s.select( 'path' ),
            pathConfig = {
                from : path.attr( 'd' ),
                to : el.getAttribute( 'data-path-hover' )
            };
        el.setAttribute('data-state', 'in')

        function collapse(){
            removeClass(el, 'shapeHover-in')
            path.animate( { 'path' : pathConfig.from }, speed, easing );
        }

        function spread(){
            addClass(el, 'shapeHover-in')
            path.animate( { 'path' : pathConfig.to }, speed, easing );
        }

        el.addEventListener( 'click', function() {
            if(hasClass(el, 'shapeHover-in')) collapse()
            else spread()
        } );

        el.addEventListener( 'mouseenter', function() {
            spread()
        } );

        el.addEventListener( 'mouseleave', function() {
            collapse()
        } );

    } );
}

initShapeHover();
