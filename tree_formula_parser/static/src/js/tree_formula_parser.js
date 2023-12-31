/**
 * Created by vladimir on 12/12/17.
 */
odoo.define('tree_formula_parser.tree_formula_parser', function(require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var formats = require('web.formats');
var pyeval = require('web.pyeval');
var session = require('web.session');
var utils = require('web.utils');
var data_manager = require('web.data_manager');

var View = require('web.View');
var ListView = require('web.ListView');
var DataExport = require('web.DataExport');
var Sidebar = require('web.Sidebar');
var Pager = require('web.Pager');

var _lt = core._lt;

var TreeFormulaParser = ListView.extend({
    _template: 'TreeFormulaParserView',
    display_name: _lt("Tree Formula Parser"),
    icon: 'fa-list-ul',
    defaults: _.extend({}, View.prototype.defaults, {
        // records can be selected one by one
        selectable: true,
        // list rows can be deleted
        deletable: false,
        // whether the column headers should be displayed
        header: true,
        // display addition button, with that label
        addable: _lt("Create"),
        // whether the list view can be sorted, note that once a view has been
        // sorted it can not be reordered anymore
        sortable: true,
        // whether the view rows can be reordered (via vertical drag & drop)
        reorderable: true,
        action_buttons: true,
        //whether the editable property of the view has to be disabled
        disable_editable_mode: false,
        import_enabled: true,
    }),

    init: function() {
        this._super.apply(this, arguments);
    },

    do_load_state: function(state, warm) {
    	return this._super.apply(this, arguments);
    },

    load_list: function() {
        var self = this;
        return this._super.apply(this, arguments);
    },

    reload_content: synchronized(function () {
        var self = this;
        this.setup_columns(this.fields_view.fields, this.grouped);
        this.$('tbody .o_list_record_selector input').prop('checked', false);
        this.records.reset();
        var reloaded = $.Deferred();
        this.groups.render(function () {
            if (self.dataset.index === null) {
                if (self.records.length) {
                    self.dataset.index = 0;
                }
            } else if (self.dataset.index >= self.records.length) {
                self.dataset.index = self.records.length ? 0 : null;
            }
            self.load_list().then(function () {
                if (!self.grouped && self.display_nocontent_helper()) {
                    self.no_result();
                }
                reloaded.resolve();
            });
        });
        this.do_push_state({
            min: this.current_min,
            limit: this._limit
        });
        return reloaded.promise();
    }),

});

core.view_registry.add('tree_formula_parser', TreeFormulaParser);

function synchronized(fn) {
    var fn_mutex = new utils.Mutex();
    return function () {
        var obj = this;
        var args = _.toArray(arguments);
        return fn_mutex.exec(function () {
            if (obj.isDestroyed()) { return $.when(); }
            return fn.apply(obj, args);
        });
    };
}

return TreeFormulaParser;

});