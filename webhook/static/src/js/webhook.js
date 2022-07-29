odoo.define('portal.portal_webhook', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
const Dialog = require('web.Dialog');
const {_t, qweb} = require('web.core');
const ajax = require('web.ajax');
const session = require('web.session');


publicWidget.registry.selectAll = publicWidget.Widget.extend({
    selector: '.o_portal_webhook_select_all',
    events: {
        'click': '_onClick',
    },
    _onClick: function () {
        var $checkboxes = this.$el.closest('table').find('tbody input[type="checkbox"]');
        $checkboxes.prop('checked', this.el.checked);
        // console.log($checkboxes.prop('checked'));
    }
});

publicWidget.registry.deleteSubscription = publicWidget.Widget.extend({
    selector: '.o_portal_webhook_delete_subscription',
    events: {
        'click': '_onClick',
    },
    _onClick: function () {
        var $checkboxes = $(".checkbox");
        const subscriptions_to_be_deleted = [];
        for (var i = 0; i < $checkboxes.length; i++) {
            if ($checkboxes[i].checked) {
                subscriptions_to_be_deleted.push(parseInt($checkboxes[i].id));
                
            }
        }
        this._rpc({
            model: 'webhook_subscription',
            method: 'unlink',
            args: [subscriptions_to_be_deleted],
        }).then( () => {
            window.location = window.location;
        });
    }
});

publicWidget.registry.newSubscription = publicWidget.Widget.extend({
    selector: '.o_portal_new_subscription',
    events: {
        click: '_onClick'
    },
    async _onClick(e){
        e.preventDefault();
        console.log("ASDASD");
        await ajax.loadXML('/webhook/static/src/xml/webhook.xml', qweb);
        this._rpc({
            model: 'base.automation',
            method : 'search_read',
            domain : [
                ['is_webhook','=','True'],
            ]
        }).then( (webhooks) => {
            console.log(webhooks);
            var dialog = new Dialog(self, {
                title : _t('Edit Subscription'),
                $content: qweb.render('webhook.new_subscription',
                {
                    webhooks : webhooks
                }
                ), 
                buttons: [{text: _t('Confirm'), classes: 'btn-primary', close: true, click: async () => {
                    var new_webhook_id = dialog.el.querySelector('[name="webhook_id"]').value;
                    var new_webhook_url = dialog.el.querySelector('[name="webhook_url"]').value;
                    this._rpc({
                        model: 'webhook_subscription',
                        method: 'create',
                        args: [{"webhook":new_webhook_id,"webhook_url": new_webhook_url}],
                    }).then( () => {
                        window.location = window.location;
                    });
                }}, {text: _t('Discard'), close: true}]
            });
            dialog.opened(() => {
                const new_webhook_id = dialog.el.querySelector('[name="webhook_id"]');
                const new_webhook_url = dialog.el.querySelector('[name="webhook_url"]');
                new_webhook_id.addEventListener('input', (e) => { 
                    console.log(e.target.value);
                });
                new_webhook_url.addEventListener('input', (e) => { 
                    console.log(e.target.value);
                });
            })
            dialog.open();    
        });
    }
            
});

publicWidget.registry.editSubscription = publicWidget.Widget.extend({
    selector: '.o_portal_edit_subscription',
    events: {
        click: '_onClick'
    },
    async _onClick(e){
        e.preventDefault();
        console.log("Clicked!");
        console.log(this.target.id);
        await ajax.loadXML('/webhook/static/src/xml/webhook.xml', qweb);
        this._rpc({
            model: 'webhook_subscription',
            method : 'search_read',
            domain : [
                ['id','=',parseInt(this.target.id)]
            ]
        }).then( (webhook_subscription) => {
            const originally_subscribed_webhook_id = webhook_subscription[0].webhook[0];
            const originally_subscribed_url = webhook_subscription[0].webhook_url;
            this._rpc({
                model: 'base.automation',
                method : 'search_read',
                domain : [
                    ['is_webhook','=','True'],
                    ['id','=',originally_subscribed_webhook_id]
                ]
            }).then((originally_subscribed_webhook) => {
                originally_subscribed_webhook = originally_subscribed_webhook[0];
                this._rpc({
                    model: 'base.automation',
                    method : 'search_read',
                    domain : [
                        ['is_webhook','=','True'],
                        ['id','!=',originally_subscribed_webhook.id]
                    ]
                }).then( (webhooks) => {
                    var dialog = new Dialog(self, {
                        title : _t('Edit Subscription'),
                        $content: qweb.render('webhook.edit_subscription',
                        {
                            webhooks : webhooks,
                            originally_subscribed_webhook : originally_subscribed_webhook,
                            originally_subscribed_url : originally_subscribed_url
                        }
                        ), 
                        buttons: [{text: _t('Confirm'), classes: 'btn-primary', close: true, click: async () => {
                            var new_webhook_id = dialog.el.querySelector('[name="webhook_id"]').value;
                            var new_webhook_url = dialog.el.querySelector('[name="webhook_url"]').value;
                            this._rpc({
                                model: 'webhook_subscription',
                                method: 'edit_subscription',
                                args: [parseInt(this.target.id), new_webhook_id, new_webhook_url],
                            }).then( () => {
                                window.location = window.location;
                            });
                        }}, {text: _t('Discard'), close: true}]
                    });
                    dialog.opened(() => {
                        const new_webhook_id = dialog.el.querySelector('[name="webhook_id"]');
                        const new_webhook_url = dialog.el.querySelector('[name="webhook_url"]');
                        new_webhook_id.addEventListener('input', (e) => { 
                            console.log(e.target.value);
                        });
                        new_webhook_url.addEventListener('input', (e) => { 
                            console.log(e.target.value);
                        });
                    })
                    dialog.open();    
                });
            })
            
        })
        
    }
});
});
