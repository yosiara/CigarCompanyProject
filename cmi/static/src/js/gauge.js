nv.models.gauge = function() {
    "use strict";

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var margin = {top: 0, right: 0, bottom: 0, left: 0}
        , width = 500
        , height = 500
        , id = Math.floor(Math.random() * 10000) //Create semi-unique ID in case user doesn't select one
        , color = nv.utils.getColor(['#88ac67', '#f78f20', '#db4e4e'])
        , valueFormat = d3.format(',.2f')
        , valueFormatMinMaxValues = d3.format(',.0f')
        , title = false
        , showMinMaxLabels = true
        , uom = ''
        , min = 0
        , max = 100
        , zoneLimit1 = 0.6
        , zoneLimit2 = 0.8
        , dispatch = d3.dispatch('chartClick', 'renderEnd')
        ;


    //============================================================
    // chart function
    //------------------------------------------------------------

    var renderWatch = nv.utils.renderWatch(dispatch);

    function chart(selection) {
        renderWatch.reset();

        selection.each(function(data) {
            var availableWidth = width - margin.left - margin.right
                , availableHeight = height - margin.top - margin.bottom
                , container = d3.select(this)
                ;

            var cx = availableWidth / 2;
            var cy = availableHeight / 2;

            nv.utils.initSVG(container);

            var radius = Math.min(availableWidth, availableHeight) / 2;
            var range = max - min;
            var valueDegrees = data[0][0] > max ? max / range * 270 : data[0][0] / range * 270;
            var fontSize = Math.round(Math.min(availableWidth, availableHeight) / 10);

            var zones = [
                { from: min, to: min + range * zoneLimit1 },
                { from: min + range * zoneLimit1, to: min + range * zoneLimit2 },
                { from: min + range * zoneLimit2, to: max }
            ];

            // Setup containers and skeleton of chart
            var wrap = container.selectAll('.nv-wrap.nv-gauge').data([data]);
            var wrapEnter = wrap.enter().append('g').attr('class','nvd3 nv-wrap nv-gauge nv-chart-' + id);
            var gEnter = wrapEnter.append('g');
            var g_bands = gEnter.append('g').attr('class', 'nv-gaugeBands');
            var g_title = gEnter.append('g').attr('class', 'nv-gaugeTitle');
            var g_needle = gEnter.append('g').attr('class', 'nv-gaugeNeedle');
            var g_label = gEnter.append('g').attr('class', 'nv-gaugeLabel');
            var g_minLabel = gEnter.append('g').attr('class', 'nv-gaugeMinLabel');
            var g_maxLabel = gEnter.append('g').attr('class', 'nv-gaugeMaxLabel');

            wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            // draw gauge bands
            for (var i in zones) {
                drawBand(zones[i].from, zones[i].to, color(i), min, max, radius, g_bands);
            }

            // draw needle
            var needlePath = buildNeedlePath(min,range, cx, cy, min, max, radius);

            var needleLine = d3.svg.line()
                .x(function(d) { return d.x; })
                .y(function(d) { return d.y; })
                .interpolate("basis");

            g_needle.append("path")
                .data([needlePath])
                .attr("d", needleLine)
                .style("fill", "#555555");

            g_needle.append('circle')
                .attr('cx', 0)
                .attr('cy', 0)
                .attr('r', 0.115 * radius)
                .style("fill", "#555555");

            wrap.selectAll('.nv-gaugeBands path')
                .attr("transform", function () { return "translate(" + cx + ", " + (cy - 0.08 * radius) + ") rotate(270)" });

            wrap.select('.nv-gaugeNeedle')
                .attr('transform', 'translate(' + cx + ',' + (cy - 0.08 * radius) + ')')
                .transition()
                .duration(2500)
                .delay(500)
                .ease('bounce')
                .attrTween("transform", function() { return d3.interpolate('translate(' + cx + ',' + (cy - 0.08 * radius) + ') rotate(0)', 'translate(' + cx + ',' + (cy - 0.08 * radius) + ') rotate('+valueDegrees+')'); } );

            wrap.select('.nv-gaugeTitle')
                .attr('transform', 'translate(' + cx + ',' + (cy / 2 + fontSize / 2) + ')');

            wrap.select('.nv-gaugeLabel')
                .attr('transform', 'translate(' + cx * 0.5 + ',' + (cy + radius / 2 - fontSize * 0.8) + ')');

            if (showMinMaxLabels) {
                wrap.select('.nv-gaugeMinLabel')
                    .attr('transform', 'translate(' + (cx - radius / 2.6 - fontSize * 0.9) + ',' + (cy + radius / 1.35 - fontSize * 0.9) + ')');

                wrap.select('.nv-gaugeMaxLabel')
                    .attr('transform', 'translate(' + (cx + radius / 1.25 - fontSize * 0.9) + ',' + (cy + radius / 1.35 - fontSize * 0.9) + ')');
            }

            // draw title
            if (title) {
                g_title.append("text")
                    .attr("dy", fontSize / 2)
                    .attr("text-anchor", "middle")
                    .text(title)
                    .style("font-size", fontSize + "px");
            }

            // draw value
            g_label.append("g")
                .data(data)
                .html("<foreignObject width=\"50%\" height=\"15\">\n" +
                    "    <div xmlns=\"http://www.w3.org/1999/xhtml\">\n" +
                            valueFormat(data) + uom +
                    "    </div>\n" +
                    "</foreignObject>"
                )
                .style("font-size", fontSize*0.8 + "px");

            if (showMinMaxLabels) {
                g_minLabel.append("text")
                    .data(data)
                    .attr("dy", fontSize / 2)
                    .attr("text-anchor", "start")
                    .text(valueFormatMinMaxValues(min))
                    .style("font-size", fontSize*0.65 + "px")
                    .style("fill", "#78291c");

                g_maxLabel.append("text")
                    .data(data)
                    .attr("dy", fontSize / 2)
                    .attr("text-anchor", "end")
                    .text(valueFormatMinMaxValues(max))
                    .style("font-size", fontSize*0.65 + "px")
                    .style("fill", "#78291c");
            }

            container.on('click', function(d,i) {
                dispatch.chartClick({
                    data: d,
                    index: i,
                    pos: d3.event,
                    id: id
                });
            });

            // draws a gauge band
            function drawBand(start, end, color, min, max, radius, element) {
                if (0 >= end - start) return;

                element.append("path")
                    .style("fill", color)
                    .attr("d", d3.svg.arc()
                        .startAngle(valueToRadians(start, min, max))
                        .endAngle(valueToRadians(end, min, max))
                        .innerRadius(0.65 * radius)
                        .outerRadius(0.85 * radius))
                    .attr("transform", function() { return "translate(" + radius + ", " + radius + ") rotate(270)" });
            }

            function buildNeedlePath(value, range, cx, cy, min, max, radius) {
                if(value > max){
                    value = max;
                }
                var delta = range / 1;
                var tailValue = value - (range * (1/(270/360)) / 2);

                var head = centerPoint(valueToPoint(value, 0.8, min, max, radius), cx, cy);
                var head1 = centerPoint(valueToPoint(value - delta, 0.12, min, max, radius), cx, cy);
                var head2 = centerPoint(valueToPoint(value + delta, 0.12, min, max, radius), cx, cy);

                var tail = centerPoint(valueToPoint(tailValue, 0, min, max, radius), cx, cy);
                var tail1 = centerPoint(valueToPoint(tailValue - delta, 0.12, min, max, radius), cx, cy);
                var tail2 = centerPoint(valueToPoint(tailValue + delta, 0.12, min, max, radius), cx, cy);

                function centerPoint(point, cx, cy) {
                    point.x -= cx;
                    point.y -= cy;
                    return point;
                }

                return [head, head1, tail2, tail, tail1, head2, head];
            }

            function valueToDegrees(value, min, max) {
                range = max - min;
                return value / range * 270 - (min / range * 270 + 45);
            }

            function valueToRadians(value, min, max) {
                return valueToDegrees(value, min, max) * Math.PI / 180;
            }

            function valueToPoint(value, factor, min, max, radius) {
                return {
                    x: cx - radius * factor * Math.cos(valueToRadians(value, min, max)),
                    y: cy - radius * factor * Math.sin(valueToRadians(value, min, max))
                };
            }
        });

        renderWatch.renderEnd('gauge immediate');
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    chart.dispatch = dispatch;
    chart.options = nv.utils.optionsFunc.bind(chart);

    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        width:      {get: function(){return width;}, set: function(_){width=_;}},
        height:     {get: function(){return height;}, set: function(_){height=_;}},
        title:      {get: function(){return title;}, set: function(_){title=_;}},
        showMinMaxLabels:    {get: function(){return showMinMaxLabels;}, set: function(_){showMinMaxLabels=_;}},
        valueFormat:    {get: function(){return valueFormat;}, set: function(_){valueFormat=_;}},
        id:         {get: function(){return id;}, set: function(_){id=_;}},
        min:         {get: function(){return min;}, set: function(_){min=_;}},
        max:         {get: function(){return max;}, set: function(_){max=_;}},
        uom:         {get: function(){return uom;}, set: function(_){uom=_;}},
        zoneLimit1: {get: function(){return zoneLimit1;}, set: function(_){zoneLimit1=_;}},
        zoneLimit2: {get: function(){return zoneLimit2;}, set: function(_){zoneLimit2=_;}},

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
            margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
            margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
            margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
        }},
        color: {get: function(){return color;}, set: function(_){
            color=nv.utils.getColor(_);
        }}
    });

    nv.utils.initOptions(chart);
    return chart;
};