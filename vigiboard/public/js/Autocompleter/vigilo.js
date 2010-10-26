Autocompleter.Request.VigiloJSON = new Class({

    Extends: Autocompleter.Request,

    options: {
        resVar: 'results'
    },

    initialize: function(el, url, options) {
        this.parent(el, options);
        this.request = new Request.JSON($merge({
            'url': url,
            'link': 'cancel'
        }, this.options.ajaxOptions)).addEvent('onComplete', this.queryResponse.bind(this));
    },

    queryResponse: function(response) {
        this.parent();
        this.update(response[this.options.resVar]);
    }

});
