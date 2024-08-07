/**
 * JQuery MultiDraggable Plugin
 *
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 *
 * Written by Sudheer Someshwara <sudheer.someshwara@gmail.com>
 *
 * MultiDraggable is a jQuery plugin which extends jQuery UI Draggable to add multi drag and live functionality.
 *
 **/
(function ($, undefined) {
    $.fn.multiDraggable = function (opts) {
        var initLeftOffset = []
            , initTopOffset = [];
        return this.each(function () {
            $(this).on("mouseover", function () {
                if (!$(this).data("init")) {
                    $(this).data("init", true).draggable(opts, {
                        start: function (event, ui) {
                            const pos = $(this).position();
                            $.each($(opts.group) || {}, function (key, value) {
                                $(value).addClass('ui-draggable-dragging');
                                const elemPos = $(value).position();
                                initLeftOffset[key] = elemPos.left - pos.left;
                                initTopOffset[key] = elemPos.top - pos.top;
                            });
                            opts.startNative ? opts.startNative() : {};
                        },
                        drag: function (event, ui) {
                            const pos = $(this).offset();
                            $.each($(opts.group) || {}, function (key, value) {
                                $(value).offset({
                                    left: pos.left + initLeftOffset[key],
                                    top: pos.top + initTopOffset[key]
                                });
                            });
                            opts.dragNative ? opts.dragNative() : {};
                        },
                        stop: function (event, ui) {
                            const pos = $(this).offset();
                            $.each($(opts.group) || {}, function (key, value) {
                                $(value).removeClass('ui-draggable-dragging');
                                $(value).offset({
                                    left: pos.left + initLeftOffset[key],
                                    top: pos.top + initTopOffset[key]
                                });
                            });
                            opts.stopNative ? opts.stopNative() : {};
                        },
                    });
                }
            });
        });
    };
}(jQuery));