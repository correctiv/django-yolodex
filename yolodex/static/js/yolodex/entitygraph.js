function EntityGraph(subjectId, legendContainer, containerId, types, graphUrl) {

  for (var type in types.node) {
    type = types.node[type];
    var icon = type.settings.icon;
    icon = String.fromCodePoint(parseInt(icon.substring(1), 16));
    $('#' + legendContainer).append(
      '<li><span class="glyphicon">' + icon + '</span>' + type.name + '</li>'
    );
  }

  var container = d3.select('#' + containerId);
  var width = $('#' + containerId).width();
  var height = Math.floor(width * 0.5);
  $('#' + containerId).height(height);
  var nodeMouseDown = false;
  var nodeRadius = 5;
  var nodeRadiusFunc = d3.scale.sqrt().range([10, 25]);
  var linkSizeFunc = d3.scale.linear().range([3, 8]).domain([1, 10]);
  var fontSizeFunc = d3.scale.linear().range([8, 16]);

  var tooltip = container.append("div")
      .attr("class", "tooltip")
      .style("opacity", 1e-6);
  var tooltipShowing = false;

  function mousemove() {
    if (!tooltipShowing) {
      return;
    }
    var b = tooltip.node().getBoundingClientRect();
    var w = b.width;
    var h = b.height;
    tooltip
      .style("left", (d3.event.pageX - w / 2) + "px")
      .style("top", (d3.event.pageY - h - 15) + "px");
  }

  function showTooltip(text) {
    tooltipShowing = true;
    tooltip.text(text)
      .style('opacity', 1);
  }
  function hideTooltip(node) {
    tooltipShowing = false;
    tooltip.style('opacity', 1e-6);
  }

  var color = d3.scale.category20();
  var zoom = d3.behavior.zoom();
  var d3cola = cola.d3adaptor()
      .linkDistance(function(d){
        return nodeRadiusFunc(d.source.degree) * 2.2 + nodeRadiusFunc(d.target.degree) * 2.2 + 10;
      })
      // .avoidOverlaps(true)
      .symmetricDiffLinkLengths(10)
      .size([width, height]);

  var outer = container.append("svg")
    .classed('svg-network', true)
    .attr("width", width)
    .attr("height", height)
    .attr("pointer-events", "all")
    .on("mousemove", mousemove);

  var svg = outer.append('g')
    .attr('class', 'network-group');

  var scaleFactor = 1;
  var translation = [0,0];
  var tick = function(){};
  var xScale = d3.scale.linear()
   .domain([0, width])
   .range([0, width]);

  var yScale = d3.scale.linear()
    .domain([0, height])
    .range([0, height]);

  var zoomListener = d3.behavior.zoom()
    .scaleExtent([0.2, 8])
    .x(xScale)
    .y(yScale)
    .on('zoom', zoomHandler);

  function zoomHandler(t, s) {
    if (nodeMouseDown) { return; }
    tick();
  }
  zoomListener(outer);
  outer.on("dblclick.zoom", null);

  function graphBounds() {
      var x = Number.POSITIVE_INFINITY, X=Number.NEGATIVE_INFINITY, y=Number.POSITIVE_INFINITY, Y=Number.NEGATIVE_INFINITY;
      svg.selectAll(".node").each(function(v) {
          var r = nodeRadiusFunc(v.degree);
          x = Math.min(x, v.x - r);
          X = Math.max(X, v.x + r);
          y = Math.min(y, v.y - r);
          Y = Math.max(Y, v.y + r);
      });
      return { x: x, X: X, y: y, Y: Y };
  }

  function zoomToFit(render) {
      var b = graphBounds();
      var w = b.X - b.x, h = b.Y - b.y;
      var cw = outer.attr("width"), ch = outer.attr("height");
      var s = Math.min(cw / w, ch / h);
      var tx = (-b.x * s + (cw / s - w) * s / 2),
          ty = (-b.y * s + (ch / s - h) * s / 2);

      d3.transition()
        .duration(500)
        .call(zoomListener
              .scale(s)
              .translate([tx, ty]).event);
      if (render){
        tick();
      }
  }

  var drag = d3cola.drag()
    .origin(function(d) { return [d.x, d.y]; })
    .on("dragstart.d3adaptor", dragstarted)
    .on("drag.d3adaptor", dragged)
    .on("dragend.d3adaptor", dragended);

  function dragstarted(d){
    d3.event.sourceEvent.stopPropagation();
    d3.select(this).classed("dragging", true);
     //stop ticks while dragging
     d3cola.stop();
  }
  function dragged(d){
    d.wasDragged = true;

    var mouse = d3.mouse(svg.node());

    d.px = d.x = xScale.invert(mouse[0]);
    d.py = d.y = yScale.invert(mouse[1]);
    // d3cola.resume();
    tick();//re-position this node and any links
  }
  function dragended(d){
    d.fixed = true;
    d3.select(this).classed("dragging", false);
    d3cola.resume();
  }

  function getNodeTypeSettings(d, n) {
    var t = types.node[d.type];
    if (!t) {
      return {};
    }
    var val = t.settings[n] || '';
    if (val.indexOf('@') === 0) {
      return d.data[val.substring(1)];
    }
    return val;
  }

  function getNodeIcon(d) {
    var icon = getNodeTypeSettings(d, 'icon');
    if (icon.indexOf('\\') === 0) {
      return String.fromCodePoint(parseInt(icon.substring(1), 16));
    }
    return icon;
  }

  function getNodeIconColor(d) {
    return getNodeTypeSettings(d, 'icon-color');
  }

  function getNodeColor(d) {
    return getNodeTypeSettings(d, 'color');
  }

  function getNodeStrokeColor(d){
    return getNodeTypeSettings(d, 'stroke-color');
  }

  d3.json(graphUrl, function (error, graph) {
    var linkMapping = {};
    var idMapping = {};
    var distinctEdge = {};
    var highestDegree = 0;
    graph.nodes.forEach(function(n, i) {
      n.subject = (n.id === subjectId);
      if (n.subject) {
        n.fixed = true;
        n.x = width / 2;
        n.y = height / 2;
      }
      idMapping[n.id] = n;
    });
    graph.edges = graph.edges.filter(function(e) {
      e.sourceId = e.source;
      e.targetId = e.target;
      var source = idMapping[e.sourceId];
      var target = idMapping[e.targetId];
      source.degree = source.degree || 0;
      target.degree = target.degree || 0;
      source.degree += 1;
      target.degree += 1;
      highestDegree = Math.max(highestDegree, source.degree);
      highestDegree = Math.max(highestDegree, target.degree);
      var edgeKey = [e.sourceId, e.targetId].sort().join('-');
      var prev = distinctEdge[edgeKey];
      if (prev !== undefined) {
        distinctEdge[edgeKey] += 1;
        return false;
      }
      distinctEdge[edgeKey] = 1;
      return true;
    });

    var shouldPruneEdge = function(edge) {
      // Remove connection to self
      if (edge.sourceId === edge.targetId) {
        return true;
      }

      var source = idMapping[edge.sourceId];
      var target = idMapping[edge.targetId];
      var pruned = false;
      if (source.distance > 0 &&
          source.degree > 20 &&
          target.distance > 1) {
        pruned = true;
      }
      if (target.distance > 0 &&
          target.degree > 20 &&
          source.distance > 1) {
        pruned = true;
      }
      return pruned;
    };

    var shouldPruneNode = function(node) {
      if (node.pruned && node.distance > 1) {
        return true;
      }
      return false;
    };

    graph.edges = graph.edges.filter(function(e) {
      return !shouldPruneEdge(e);
    });

    graph.edges.forEach(function(e) {
      var source = idMapping[e.sourceId];
      var target = idMapping[e.targetId];
      source.rdegree = source.rdegree || 0;
      target.rdegree = target.rdegree || 0;
      source.rdegree += 1;
      target.rdegree += 1;
    });
    graph.nodes = graph.nodes.filter(function(n){
      return !!n.rdegree;
    });

    graph.nodes.forEach(function(n, i){
      linkMapping[n.id] = i;
    });
    graph.edges.forEach(function(e) {
      var edgeKey = [e.sourceId, e.targetId].sort().join('-');
      e.weight = distinctEdge[edgeKey];
      e.source = linkMapping[e.source];
      e.target = linkMapping[e.target];
    });

    nodeRadiusFunc.domain([1, highestDegree]);
    fontSizeFunc.domain([1, highestDegree]);

    d3cola
      .nodes(graph.nodes)
      .links(graph.edges)
      .start(20, 20, 20);

    var link = svg.selectAll(".link")
        .data(graph.edges)
      .enter().append('svg:path')
        .classed('link', true)
        .classed('subjectlink', function(d){
          return d.sourceId === subjectId || d.targetId === subjectId;
        })
        .attr('stroke-width', function(d){
          return linkSizeFunc(d.weight);
        })
        .on('mouseover', function(d){
          showTooltip(d.data.label + ' -> ' + d.target.name);
        })
        .on('mouseout', function(d){
          hideTooltip(d);
        });

    var nodeContainer = svg.selectAll(".node")
        .data(graph.nodes)
      .enter().append("g")
        .classed("nodecontainer", true);

    var node = nodeContainer
      .append('circle')
        .classed("node", true)
        .classed("subject", function(d){ return d.subject; })
        .attr("r", function(d) {
          return nodeRadiusFunc(d.degree);
        })
        .style("fill", function (d) { return getNodeColor(d); })
        .style("stroke", function (d) {
          if (d.id === subjectId) {
            return getNodeStrokeColor(d);
          }
          return getNodeStrokeColor(d);
        })
        .on('mouseover', function(d){
          showTooltip(d.name);
        })
        .on('mouseout', function(d){
          hideTooltip(d);
        })
        .on("mousedown", function (d) {
          d.wasDragged = false;
          nodeMouseDown = true;
        })
        .on("mouseup", function () {
          nodeMouseDown = false;
        })
        .on('click', function(d){
          if (d.wasDragged) {
            return;
          }
          if (d.id !== subjectId) {
            document.location.href = d.url;
          }
        })
        .call(drag);

    nodeContainer.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .classed('node-icon', true)
      .style("stroke", function (d) {
        return getNodeIconColor(d);
      })
      .on('mouseover', function(d){
        showTooltip(d.name);
      })
      .on('mouseout', function(d){
        hideTooltip(d);
      })
      .attr('font-size', function(d) {
        return fontSizeFunc(d.degree) + 'px';
      })
      .text(function(d) {
        return getNodeIcon(d);
      });

    tick = function(){
      // draw directed edges with proper padding from node centers
      link.attr('d', function (d) {
        // var sx = translation[0] + scaleFactor * d.source.x,
        // sy = translation[1] + scaleFactor * d.source.y,
        // tx = translation[0] + scaleFactor * d.target.x,
        // ty = translation[1] + scaleFactor * d.target.y;
        var sx = xScale(d.source.x),
        sy = yScale(d.source.y),
        tx = xScale(d.target.x),
        ty = yScale(d.target.y);
        var deltaX = tx - sx,
          deltaY = ty - sy,
          dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
          normX = deltaX / dist,
          normY = deltaY / dist,
          sourcePadding = nodeRadiusFunc(d.source.degree) + 1,
          targetPadding = nodeRadiusFunc(d.target.degree) + 1,
          sourceX = sx + (sourcePadding * normX),
          sourceY = sy + (sourcePadding * normY),
          targetX = tx - (targetPadding * normX),
          targetY = ty - (targetPadding * normY);
        return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
      });

      nodeContainer.attr('transform', function(d){
        var t = [xScale(d.x), yScale(d.y)];
        return 'translate(' + t + ')';
      });
    };
    d3cola.on("tick", tick);
    window.setTimeout(function(){
      zoomToFit(true);
    }, 500);
  });

}
