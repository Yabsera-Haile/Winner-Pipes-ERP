odoo.define('search_panel_toggle.SPanel',function (require) {
"use strict";

	const AbstractView = require('web.AbstractView');
	var ListView = require("web.ListView");
	var Dialog = require("web.Dialog");
	var core = require("web.core");
	var view_dialogs = require("web.view_dialogs");
	var QWeb = core.qweb;
	var view_registry = require('web.view_registry');
	var select_create_controllers_registry = require('web.select_create_controllers_registry');
	var _t = core._t;
	const utils = require('web.utils');	
	const SearchPanel = require("web/static/src/js/views/search_panel.js");
    utils.patch(SearchPanel,"Mongrov.search.panel", {
        mounted() {
			this._super(...arguments);
			let self = this;
			let $el = $(this.el);
			let $toggleButton = $el.siblings('button.btn-search-panel-toggle');
			if('width' in this.props){
				$el.css('flex-basis',this.props.width+"px");
			}
			if($toggleButton.length){
				return;
			}
	       	let $hideButton = QWeb.render("SearchPanel.HideButton",this);
	       	let $buttonEl = $(document.createDocumentFragment());
	       	$buttonEl.append($hideButton);	       	       
	       	$buttonEl.find('button.btn-search-panel-toggle').click(function(){
				if($el.hasClass('o_hidden')){
					self.do_show();
					$(this).removeClass('fa-caret-right show-panel').addClass('fa-caret-left hide-panel');;
				}else{
					self.do_hide();
					$(this).addClass('fa-caret-right show-panel').removeClass('fa-caret-left hide-panel');
				}
			 }); 
	       $el.after($buttonEl);
		},
		
		do_hide(){
			if (this.el) {
            	$(this.el).addClass('o_hidden');
        	}

		},
		do_show() {
			if (this.el) {
				$(this.el).removeClass('o_hidden');
			}
    	},
        
    });
 
   

});