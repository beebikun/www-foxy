var preModalFn;

function showHideModal(el, show){
    var classes = getClass(el);
    if(show){
        el.style.display = 'block';
        setTimeout(function(){
            addClass(el, 'in');
            var div = document.createElement('div');
            addClass(div, 'modal-backdrop fade in');
            if(document.body != null) document.body.appendChild(div);
        }, 50);
    }else{
        removeClass(el, 'in');
        setTimeout(function(){
            el.style.display = 'none'
            removeEl('.modal-backdrop');
        }, 50);
    }
    el.setAttribute('aria-hidden', show ? false : true)
}



function clickModalA(a){
  //функция для onlick
    if(preModalFn) preModalFn(a);
    var id = a.getAttribute('href').slice(1);
    var modal = document.getElementById( trim(id) );
    if(modal) showHideModal(modal, true)
}

function initModal(){
    var modalClass = '.modal';

    //find and set all modal dismiss buttons
    node2array(document.querySelectorAll('[data-dismiss=modal]')).forEach(
        function(btn){
            btn.onclick = function(e){
                var modal = findParent(modalClass, this);
                if(modal) showHideModal(modal);
            }
         }
    );

    //find and set all modal open elements (<a>)
    node2array(document.querySelectorAll('[data-toggle=modal]')).forEach(
        function(a){
            a.onclick = function(){clickModalA(this);}
        }
    );

    //find and set all modal elements (<div class="modal">)
    node2array(document.querySelectorAll(modalClass)).forEach(
        function(modal){
            modal.onclick = function(e){
                if( ~e.target.className.split(' ').indexOf('modal') ) showHideModal(this)}
        }
    );
}