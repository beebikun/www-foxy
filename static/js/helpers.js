function filterVisible(nodes, returnFull){
    var list = nodes instanceof Array ? nodes : node2array(nodes);
    var vis = list.filter(function(el){return el.offsetWidth!==0});
    return returnFull ? vis : vis.length ? vis[0] : undefined
}


function popAttribute(elem, attr){
    var val = elem.getAttribute(attr);
    elem.removeAttribute(name);
    return val;
}


function attrs2obj(elem, attrs_list, obj) { //covert needed elem attrs into obj; attrs_list = [[attr_name, fn || null], .. ]
    var obj = obj || new Object;
    var attr = attrs_list.pop(), name = attr[0], fn = attr[1] || function(val){return val};
    obj[name.replace('data-','')] = fn(popAttribute(elem, name));
    return attrs_list.length ? attrs2obj(elem, attrs_list, obj) : obj
};


function findParent(parentSellector, el, nodes){
    var parent = el.parentNode;
    var nodes = nodes || node2array(document.querySelectorAll(parentSellector));
    return nodes.filter(function(el){return el == parent}).length ? parent :
           parent != document ?    findParent(parentSellector, parent, nodes) :
           null
}


function removeEl(selector, parent){
    var parent = parent || document.body;
    node2array(document.querySelectorAll(selector)).forEach(function(el){
        parent.removeChild(el);
    });
}


function showhideEl(id, show){
    var el = typeof id == 'string' ? document.getElementById(id) : id;
    el.style.display = show ? 'inline-block' : 'none'
}


function showHideElBlock(id, show){
    var el = typeof id == 'string' ? document.getElementById(id) : id;
    el.style.display = show ? 'block' : 'none'
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


function filterNodes(nodes, fn){
    return node2array(nodes).filter( fn )
}


function node2array(nodes){
    return Array.prototype.slice.call(nodes)
}


function tagnameEach(tag, fn){
    node2array( document.getElementsByTagName(tag) ).forEach(fn)
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
        data = params.post ? params.data ? params.data : {} : null,
        query = params.post ? null : serialize( params.query ? params.query : {} );
    var _success = function(r){success(r.data)};
    function error(e){console.log(e)};
    if(method == 'GET') $.getJSON(path, query, _success, error)
    else $.post(path, data, _success, error)
}

/*----------------------------------------------------------------------------*/
var M = function(id, numInput, streetInput, prnts){
    this._init(id, numInput, streetInput, prnts)
}

M.prototype._init = function(id, num, street, prnts) {
    this.option = this._options()
    this.numInput = num;
    this.streetInput = street;
    this.el_parents = prnts || node2array(document.getElementById('simmularItems').getElementsByClassName('some-item'));
    this.map = new DG.Map(id);
    this.markerGroups = new Object;
    this.map.setCenter( this.option.zeroCenter, this.option.zeroZoom);
    this._setMarkers()
};

M.prototype.createMarker = function(src) {
    function _getFloat(val){
        return parseFloat(val.replace(',','.'))
    }

    var point = attrs2obj( src, [['data-lat', _getFloat], ['data-lng', _getFloat], ['data-ico', null]]);
    point.id = src.getAttribute('id')

    function _getChildHtml(childClass){
        return src.getElementsByClassName(childClass)[0].innerHTML
    }

    point.header = _getChildHtml("some-item-date");
    point.cont = _getChildHtml("some-item-body-title");
    point.footer = _getChildHtml("some-item-body-text");

    var cont = ['header', 'cont', 'footer']
    for (var i = 0; i < cont.length; i++) {
        var el = point[cont[i]], indx = el.indexOf('data-toggle="modal"');
        if( indx >= 0 )
            point[cont[i]] = el.slice(0, indx) + ' onclick="clickModalA(this)" ' + el.slice(indx);
    };

    point.query = point.cont + point.header;

    var ico = this.getPointIco(point);
    var marker = new DG.Markers.MarkerWithBalloon({
        balloonOptions: {
            headerContentHtml: '<div class="markerHeader">' + point.header +'</div>',
            contentHtml: '<div class="markerCont">' + point.cont +'</div>',
            footerContentHtml: '<div class="markerFooter">' + point.footer +'</div>',
            contentSize: new DG.Size(155, 35)
        },
        // Местоположение на которое указывает маркер:
        geoPoint: new DG.GeoPoint(point.lng,point.lat),
        hoverIcon: ico,
        clickIcon: ico,
    });

    var payment = src.getAttribute('data-payment');
    if(payment === undefined){
        this.map.markers.add(marker);
    }
    else{
        src.removeAttribute('data-payment')
        if(this.markerGroups[payment] === undefined) this.markerGroups[payment] = this.map.markers.createGroup(payment);
        this.map.markers.add(marker, payment);
    }

    marker.setIcon(ico);

    marker.val = point;

    var self = this;
    function _clickEL(e){
        if(e.clientY>400){
            self.createCenter(marker);
            window.scrollTo(0, 0);
        }
    }

    src.onclick = _clickEL

    if(src.getAttribute('id') == 'result-item'){
        this.createCenter(marker)
        document.getElementById('visible-result').onclick = _clickEL
    }
    return {marker: marker, val: point}
};

M.prototype._setMarkers = function() {
    var self = this;
    var data = Icons.data;
    self.icons = new Object;
    for (var i = 0; i < data.length; i++) {
        var ico = data[i]
        if (ico.height>42){
            ico.width = ico.width*42/ico.height;
            ico.height = 42
        }
        self.icons[ico.name] = new DG.Icon( ico.path, new DG.Size(ico.width, ico.height) )
    };
    self.icons.icoNotFound = new DG.Icon(window.location.origin + '/static/img/markers/marker-icon-gray.png', new DG.Size(25, 41))
    self.el_parents.forEach(function(elem){
        //create markers for each source elements from bottoms of site (items in #simmularItems)
        self.createMarker(elem)
    });
    var alterTextLabel = document.getElementById('simmularItemsLabel');
    if( alterTextLabel ){
        alterTextLabel.innerHTML = (function(){
            if( !self.numInput || !self.streetInput) return 'Пожалуйста, укажите адрес';
            var simular = self.el_parents.filter(function(el) {
                return el.getAttribute('is-result') == 'false';
            }).length;
            var result = self.el_parents.filter(function(el) {
                return el.getAttribute('is-result') == 'true';
            }).length;
            if(result && simular) return 'Возможно, вы искали:'
            if(result && !simular) return ''
            if(!result && simular) return 'Ничего не найдено. Возможно, вы искали: '
            if(!result && !simular) return 'Ничего не найдено <i class="fa fa-frown-o fa-lg"></i>'
        })();
    }
};

M.prototype._options = function() {
    return {
        zeroUser: {lng:127.534884, lat:50.258376},
        zeroCenter: new DG.GeoPoint(127.540081175, 50.2866410303),
        zeroZoom: 12,
    }
};

M.prototype.getPointIco = function(val) {
    if (!this.icons) return;
    if (val.ico && this.icons[val.ico]) return this.icons[val.ico];
    return this.icons.icoDefault;
};

M.prototype.createCenter = function(center) {
    center.showBalloon()
    this.map.setCenter(center.lonlat, 15);
};

/*----------------------------------------------------------------------------*/
