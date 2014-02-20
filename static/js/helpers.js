(function( $ ) {
	$.fn.apiHelper = function() {  
		var url = window.location.host + '/';
		var helper = {}
		helper.api = 'http://' + url + "api/"
		helper.street = helper.api + 'street';
		helper.markers = helper.api + 'markers-icons';
		helper.doit = helper.api + 'doit';
		helper.captcha = helper.api + 'captcha';
		helper.buildingSearch = helper.api + 'buildings/search';
		helper.bg = {};
		helper.bg.root = helper.api + 'bg/';
		helper.bg.limit = helper.bg.root + 'limit';
		return helper
	};

	$.fn.mapHelper = function(defaults) { 		
		var helper = new Object;
	  	var mapID = $(this).attr('id');
	  	helper.map = new DG.Map(mapID);
		helper.map.controls.add(new DG.Controls.Zoom());
	  	helper.defaults = defaults || {}
	  	helper.defaults.user = {lng:127.534884, lat:50.258376}
		helper.map.setCenter( new DG.GeoPoint(127.540081175, 50.2866410303),12);
		function createIcons(icons_list){	
			icons = {}		
			for(var i in icons_list){
				var icon = icons_list[i]
				if (icon.height>42){
					icon.width = icon.width*42/icon.height;
					icon.height = 42
				}
				icons[icon.name] = new DG.Icon(icon.path, new DG.Size(icon.width, icon.height))}
			return icons
		}
	  	
		
		helper.getPointIco = function(val){	
			if (val.ico) return helper.icons[val.ico]
			else return helper.icons.icoDefault
		};
		function attr_to_val(el, name_list, val){
			if(name_list.length){
				val = val || {}
				name = name_list.pop()
				newval = el.getAttribute(name);
				el.removeAttribute(name)
				if(name=='data-lat' || name=='data-lng') newval = parseFloat(newval.replace(',','.'))
				name = name.replace('data-','')
				val[name] = newval
				return attr_to_val(el, name_list, val)
			}
			else return val
		}
		helper.getMarkers = function(el_parents){
			var api = $().apiHelper();	
			$.getJSON(api.markers,{},
	        function(data){	        	
	        	if(!data.data || data.data.length==0) return;
	        	var icons = []
	        	$.each(data.data, function(k,val){icons.push(val)});
	        	helper.icons = createIcons(icons)
				helper.icons.icoNotFound = new DG.Icon('../static/img/markers/marker-icon-gray.png', new DG.Size(25, 41))
				var el_parents = el_parents || $("#simmularItems .some-item")
				$.each(el_parents, function(i, el){
					helper.createMarker(el);
				})
				if($("#simmularItemsLabel").length){
					$("#simmularItemsLabel").html( function(){
						var simular = $("#simmularItems").find(".some-item:visible").length;
						var result = $("#result").children().length;
						if(result && simular) return 'Возможно, вы искали:'	
						if(result && !simular) return ''
						if(!result && simular) return 'Ничего не найдено. Возможно, вы искали: '
						if(!result && !simular) return 'Ничего не найдено <i class="fa fa-frown-o fa-lg"></i>'
					});
					if($(numInputID).val()==''){$(numInputID).focus(); $("#simmularItemsLabel").html('Пожалуйста, укажите адрес')}
					if($(streetInputID).val()==''){$(streetInputID).focus(); $("#simmularItemsLabel").html('Пожалуйста, укажите адрес')}					
				}
	        })
		}
		helper.markerGroups = {};
		helper.createMarker = function(el){		
			var point = attr_to_val(el,['data-lat', 'data-lng', 'data-ico']);
			point.id = el.getAttribute('id')
			point.header = $(el).find(".some-item-date").html()
			point.cont = $(el).find(".some-item-body-title").html()
			point.footer = $(el).find(".some-item-body-text").html()  
			point.query = point.cont + point.footer.replace('<div><a data-toggle="modal" class="how-play-btn bold-a" href="#modal1 ">Как оплатить</a></div>','') + point.header
			var ico = helper.getPointIco(point);
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
			var payment = el.getAttribute('data-payment')
			if(payment==undefined){
				helper.map.markers.add(marker);
			}
			else{
				el.removeAttribute('data-payment')
				if(helper.markerGroups[payment]===undefined) helper.markerGroups[payment]=helper.map.markers.createGroup(payment);
				helper.map.markers.add(marker, payment);
			}
			marker.setIcon(ico);
			marker.val = point;
			$(el).click(function(e){
				if(e.clientY>400){
					helper.createCenter(marker)
					window.scrollTo(0, 0);
				}
			});
			if(el.getAttribute('id')=='result-item'){
				helper.createCenter(marker)
				$("#visible-result").click(function(e){
					if(e.clientY>400){
						helper.createCenter(marker)
						window.scrollTo(0, 0);
					}
				});
			}
			return {marker:marker, val:point}
		};				
		helper.createCenter = function (center){
			var map = helper.map
			if(center.user){
				groupMarkersCenter.getAll().map(function(m){
					m.hideBalloon()
					map.markers.remove(m)
				})				
				var centerMarker = helper.createMarker(center);
				map.markers.add(centerMarker)
				if(!center.user) centerMarker.setIcon(center.ico);
			}
			center.showBalloon()
			map.setCenter(center.lonlat,15);
			return center
		}
		helper.getLocation = function() {
			navigator.geolocation.getCurrentPosition(
				function(position){
					//Обработчик
					var val = {
						lat: position.coords.latitude, 
						lng: position.coords.longitude,
						user: true, ico:'',
						ico:icons.icoDefault,
						footer: '', header: '' , cont: 'Вы здесь'
					}			
					if(val.lat!=helper.defaults.user.lat && val.lng!=helper.defaults.user.lng) helper.getCenterPointVal(val)
				},
				function(err){
					//handle_error
					if (err.code == 1) {
					// пользователь сказал нет!
					}
				}
			);
		}
	    return helper
  	};

 	$.fn.domHelper = function(mapH, defaults) {
		var helper = {
			$bigParent: $(this),
	/*		createPointInMap: function(point){
				point.ico = mapH.getPointIco(point);
				var marker = mapH.createMarker(point);
				if(point.payment) mapH.map.markers.add(marker, defaults.markerGroups[point.payment].getName());
				else mapH.map.markers.add(marker);
				if(point.ico) marker.setIcon(point.ico);
				marker.val = point;
				return marker
			}*/
		}
		return helper
	};
})(jQuery);