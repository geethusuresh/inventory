
var Menu = new Class({
    Implements: [Options],
    options:{
    	'menu_class': '.menu'
    },
    initialize: function(element) {
        this.element = element;
        this.menus = $$(this.options.menu_class);
        this.menus.each(function(menu, index){
        	menu.addEvents({
        		'mouseenter': function(){
                    if(menu.getElement('ul')){
                        menu.getElement('ul').setStyle('display', 'block');
                    }        			
			    },
			    'mouseleave': function(){
			    	if(menu.getElement('ul')){
                        menu.getElement('ul').setStyle('display', 'none');
                    }
    			}        	
        	});
        });
    },
    
});

var DialogueModelWindow = new Class({
    Implements: [Options],
    options: {
        'pop_window': '#dialogue_popup',
        'overlay': '#overlay',
        'message_padding': '30px',
        'dialogue_popup_width': '400px',
        'left': ' 35%',
        'top': '20%',
        'height': 100,
        'content_div': ''
    },
    initialize: function(options) {
        window.scrollTo(0,0);
        this.setOptions(options);
        this.message = ""
        this.overlay = $$(this.options.overlay);
        this.pop_window = $$(this.options.pop_window);
        var height = $(document).height();
        this.set_overlay_height(height);
        this.set_message(this.message);
        this.hide_popup();
        this.close_pop_up = this.pop_window.getElement('.close_pop');       
        this.close_pop_up.addEvent('click', function(ev){
            ev.stop();
            this.hide_popup();
        }.bind(this));
        //this.set_left();
        this.set_top();
    },
    show_popup: function(){
        this.overlay.setStyle('display', 'block');
        this.pop_window.setStyle('width', this.options.dialogue_popup_width);
        this.pop_window.setStyle('height', this.options.height);
        this.pop_window.setStyle('display', 'block');
        // this.pop_window.morph({
        //     'width': this.options.dialogue_popup_width,
        //     'height': this.options.height,
        // });
    },  
    show_content: function(){       
        $$(this.options.content_div)[0].setStyle('display', 'block');
        this.show_popup();
    },
    hide_popup: function(){
        this.overlay.setStyle('display', 'none');
        this.pop_window.setStyle('display', 'none');
        if($$(this.options.content_div).length > 0)
            $$(this.options.content_div)[0].setStyle('display', 'none');
    },
    set_message: function(message){
        this.message = message;
        this.pop_window.getElement('.message').set('html', message);
        this.pop_window.getElement('.message').setStyle('padding', this.options.message_padding);
        this.show_popup();
    },
    set_overlay_height: function(height){
        this.overlay.setStyle('height', height+"px");
    },
    set_left: function(){
        this.pop_window.setStyle('left', this.options.left);
    },
    set_top: function(){
        this.pop_window.setStyle('margin-top', this.options.top);
    },  
});

window.addEvent('domready',function() {
	

	if($$('.menu_div').length > 0){
		new Menu($$('.menu_div')[0]);
	}

});

