odoo.define('remove_export_option.remove_export_option', function (require) {
"use strict";

var Sidebar = require('web.Sidebar');
var core = require('web.core');
var _t = core._t;
var _lt = core._lt;
var rpc = require('web.rpc');
    Sidebar.include({
        start: function () {
            var self = this;
            var def;
	    if (self.env.context.hide_project_payment_action_button)
            {

		def = rpc.query({
			'model': 'account.move',
			'method': 'get_all_action_ids',
			'args': [0],
			'kwargs': {context: {}},
	    	}).then(function(result) {
			self.items['other'] = $.grep(self.items['other'], function(i){
			     if (i && i.action)
			     {
				if (!(result.includes(i.action.id)))
				{
					return i;	
				}
		             }		
			     else
			     {
				return i;
		             }
		        });
                });
                return Promise.resolve(def).then(this._super.bind(this));
            }
        },
    });
});
