var mapH;
var menuSettings = { 
	hide : { h: 0, b: 'none'},
	normal: { h: 253, b: '1px solid #DADADA'}
};

$(document).ready(function(){
	$("table").addClass("table table-bordered")
	$("img").addClass("img-responsive")
	$(".map").show()
	$("input").attr('autocomplete','off'); //Если js отключен - то пусть хоть такая подсказка остаетцо
	$("#collapseMenuBtn").click(function(){
		$(window).scrollTop(0);
		var params = ( $("#mainMenu").height() == (menuSettings.normal.h-1) ) ? menuSettings.hide : menuSettings.normal;
		$("#mainMenu").animate( { height: params.h + 'px'}, 200/*, function(){
			$( "header" ).css( 'border-bottom', params.b );
		} */);
		$(this).toggleClass('orange');
		$('header, #mainMenu').toggleClass('static-headeer')
	});
	$.each($(".content-menu").children('a'), function(i, a){if(a.getAttribute('href')==window.location.pathname) $(a).addClass('active')});

	if($("#myMapId").length){
		function map_in_little_window(){
			if($(window).width()<712&&!$("#simmularItems .some-item").length) $("#myMapId").hide()
			else{
				$("#myMapId").show();
				if(window.mapH===undefined){
					mapH = $("#myMapId").mapHelper()
					mapH.getMarkers()
				}
			}
		}
		map_in_little_window()
		$(window).resize(function(){map_in_little_window()})				
	}




	var api = $().apiHelper();
	var $streetInput = $(streetInputID); var $numInput = $(numInputID); var $streetTips = $(streetTipsID);

	function ruleTipsWithArrow(code){
		var tips = streetTipsID + ' ul .active';
		var first = streetTipsID + ' ul li:first-child';
		if ($(tips).next().length) {$(tips).next().addClass('active').end().removeClass('active');}
	    else {
	        $(tips).removeClass('active');
	        $(first).addClass('active');
	    }
	}
	$numInput.keydown(function(e){
		var code = e.keyCode || e.which;
		if(code==27){//esc
			$(this).blur();
			return
		}
		if(code==13){//enter
			return
		}
	})
	$streetInput
	.keydown(function(e){		
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
			        	$('#'+elemID).click(function(){$streetInput.val(val.name)})
			        })
			        $streetTips.show();
  		  	});
  		}
	  
	})
	.blur(function(){setTimeout(function () {$streetTips.hide() }, 100) })

        $("iframe").not(":has([src])").each(function () {

	   var ifrm = this;

	   var ifrm = (ifrm.contentWindow) ? ifrm.contentWindow : (ifrm.contentDocument.document) ? ifrm.contentDocument.document : ifrm.contentDocument;

	  // ifrm.document.open();
	  // ifrm.document.write( this.getAttribute("alt") );
	  // ifrm.document.close();

	});

})

