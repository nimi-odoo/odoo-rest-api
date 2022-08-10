odoo.define('portal.portal_webhook', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const {_t, qweb} = require('web.core');
    const ajax = require('web.ajax');
    const session = require('web.session');

    // Open a dialog that contains logs for a subscription
    publicWidget.registry.viewLogs = publicWidget.Widget.extend({
        selector: '.o_portal_webhook_view_logs',
        events: {
            'click': '_onClick',
        },
        async _onClick(e){
            e.preventDefault();
            await ajax.loadXML('/webhook/static/src/xml/webhook.xml', qweb);
            const webhook_subscription_id = parseInt(this.target.id);
            const webhook_subscription_logs = await this._rpc({
                model: 'webhook_log',
                method : 'search_read',
                domain : [
                    ['webhook_subscription','=',webhook_subscription_id],
                    ['subscriber','=',session.user_id]
                ]
            });
        
            var dialog = new Dialog(self, {
                title : _t('View logs'),
                width: 'auto',
                maxWidth: 600,
                autoOpen : false,
                resizable : false,
                modal : true,
                $content: qweb.render('webhook.view_logs',{webhook_subscription_logs : webhook_subscription_logs}) ,
                buttons: [{text: _t('Close'), close: true}]});
            const this_ptr = this;
            dialog.opened(async function () {
                var detail_buttons = $(".o_portal_webhook_view_log");

                // Open a dialog that contains details for selected log
                detail_buttons.click(async (e) => {
                    const webhook_subscription_log_id = parseInt(e.target.id);
                    await this_ptr._rpc({
                        model: 'webhook_log',
                        method : 'search_read',
                        domain : [
                            ['id','=',webhook_subscription_log_id],
                            ['subscriber','=',session.user_id]
                        ]
                    }).then( (webhook_subscription_log) => {
                        console.log(webhook_subscription_log);
                        var log_detail_dialog = new Dialog(self, {
                            title : _t('View log'),
                            modal : true,
                            $content: qweb.render('webhook.view_log',{webhook_subscription_log : webhook_subscription_log[0]}) ,
                            buttons: [{text: _t('Close'), close: true}]
                        });

                        // Active, deactivate list-group-items
                        log_detail_dialog.opened(function () {
                            $(".list-group-item-action").click(function(e) {
                                console.log(e);
                                e.preventDefault()
                                $(".list-group-item-action").removeClass("text-white");
                                $(".list-group-item-action").addClass("text-primary");
                                $(".list-group-item-action").removeClass("active");

                                $(e.target).removeClass("text-primary");
                                $(e.target).addClass("text-white");
                                $(e.target).addClass("active");

                                $(".tab-pane").removeClass("active");
                                $($(e.target)[0].hash).tab('show');
                             });
                        });

                        log_detail_dialog.open();
                    } )

                })
            });

            dialog.open();
        }
    });

    // Select All functionality for webhook subscription table
    publicWidget.registry.selectAll = publicWidget.Widget.extend({
        selector: '.o_portal_webhook_select_all',
        events: {
            'click': '_onClick',
        },
        _onClick: function () {
            var $checkboxes = this.$el.closest('table').find('tbody input[type="checkbox"]');
            $checkboxes.prop('checked', this.el.checked);
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
            
            await ajax.loadXML('/webhook/static/src/xml/webhook.xml', qweb);
            this._rpc({
                model: 'base.automation',
                method : 'search_read',
                domain : [
                    ['is_webhook','=','True'],
                ]
            }).then( (webhooks) => {
                var dialog = new Dialog(self, {
                    title : _t('New Subscription'),
                    $content: qweb.render('webhook.edit_subscription',
                    {
                        webhooks : webhooks,
                        originally_subscribed_url : ""
                    }
                    ), 
                    buttons: [{text: _t('Confirm'), classes: 'btn-primary', close: false, click: async () => {
                        var new_webhook_id = dialog.el.querySelector('[name="webhook_id"]').value;
                        var new_webhook_url = dialog.el.querySelector('[name="webhook_url"]').value;
                        var new_description = dialog.el.querySelector('[name="description"]').value;
                        if (!isValidHttpUrl(new_webhook_url)){
                            dialog.el.querySelector('[name="webhook_url"]').classList.add('is-invalid');
                            dialog.el.querySelector('[name="webhook_url"]').setCustomValidity(_t("Invalid URL"));
                            dialog.el.querySelector('[name="webhook_url"]').reportValidity();
                        } else {
                            this._rpc({
                                model: 'webhook_subscription',
                                method: 'create',
                                args: [{"webhook":new_webhook_id,"webhook_url": new_webhook_url,"description":new_description}],
                            }).then( (r) => {
                                dialog.close();
                                window.location = window.location;

                            });
                        }
                    }}, {text: _t('Discard'), close: true}]
                });
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

            await ajax.loadXML('/webhook/static/src/xml/webhook.xml', qweb);
            this._rpc({
                model: 'webhook_subscription',
                method : 'search_read',
                domain : [
                    ['id','=',parseInt(this.target.id)]
                ]
            }).then( (webhook_subscription) => {
                // Since we're editing an existing record,
                // We initially want to display existing field values for the record.
                const originally_subscribed_webhook_id = webhook_subscription[0].webhook[0];
                const originally_subscribed_url = webhook_subscription[0].webhook_url;
                const original_description = webhook_subscription[0].description;
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
                                originally_subscribed_url : originally_subscribed_url,
                                original_description : original_description
                            }
                            ), 
                            buttons: [{text: _t('Confirm'), classes: 'btn-primary', close: false, click: async () => {
                                var new_webhook_id = dialog.el.querySelector('[name="webhook_id"]').value;
                                var new_webhook_url = dialog.el.querySelector('[name="webhook_url"]').value;
                                var new_description = dialog.el.querySelector('[name="description"]').value;

                                // Check if webhook callback url that user provided is valid or not.
                                if (!isValidHttpUrl(new_webhook_url)){
                                    dialog.el.querySelector('[name="webhook_url"]').classList.add('is-invalid');
                                    dialog.el.querySelector('[name="webhook_url"]').setCustomValidity(_t("Invalid URL"));
                                    dialog.el.querySelector('[name="webhook_url"]').reportValidity();
                                } else {
                                    var vals =
                                    {
                                    "webhook":new_webhook_id,
                                    "webhook_url": new_webhook_url,
                                    "description":new_description
                                    }
                                    this._rpc({
                                        model: 'webhook_subscription',
                                        method: 'write',
                                        args: [parseInt(this.target.id), vals],
                                    }).then( () => {
                                        dialog.close();
                                        window.location = window.location;
                                    });
                                }

                            }}, {text: _t('Discard'), close: true}]
                        });
                        dialog.open();    
                    });
                })
                
            })
            
        }
    });

    function isValidHttpUrl(string) {
        let url;

        try {
            url = new URL(string);
        } catch (_) {
            return false;
        }

    return url.protocol === "http:" || url.protocol === "https:";
    }


// end of webhook.js
});
