odoo.define('Vertiv.UserMenu', function (require) {
"use strict";

var rpc = require('web.rpc');
var config = require('web.config');
var core = require('web.core');
var framework = require('web.framework');
var Dialog = require('web.Dialog');
var Widget = require('web.Widget');
var user_menu = require('web.UserMenu');

var _t = core._t;
var QWeb = core.qweb;
var UserMenu = user_menu.include({
    template: 'UserMenu',

    start: function () {
        var self = this;
        var session = this.getSession();
        this.$el.on('click', '[data-menu]', function (ev) {
            ev.preventDefault();
            var menu = $(this).data('menu');
            self['_onMenu' + menu.charAt(0).toUpperCase() + menu.slice(1)]();
        });
        return this._super.apply(this, arguments).then(function () {
            var $avatar = self.$('.oe_topbar_avatar');
            if (!session.uid) {
                $avatar.attr('src', $avatar.data('default-src'));
                return Promise.resolve();
            }
            var topbar_name = session.name;
            if (config.isDebug()) {
                topbar_name = _.str.sprintf("%s (%s)", topbar_name, session.db);
            }
            self.$('.oe_topbar_name').text(topbar_name);
            var avatar_src = session.url('/web/image', {
                model:'res.users',
                field: 'image_128',
                id: session.uid,
            });
            var collab_avatar_src = avatar_src
            rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['vertiv_collab_reference_id',],
            }).then(function(url) {
                var username = session.username.split("@")[0]
                collab_avatar_src = url +'/avatar/'+ username
                $avatar.attr('src', collab_avatar_src);
            });

        });
    },


});

return UserMenu;

});
