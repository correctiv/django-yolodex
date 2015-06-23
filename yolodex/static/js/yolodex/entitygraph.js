function EntityGraph(subjectId, legendContainer, containerId, graphUrl, options) {
  options = options || {};
  var defaults = {
    respectCoords: false,
    autoPrune: true
  };
  for (var k in defaults) {
    options[k] = options[k] === undefined ? defaults[k] : options[k];
  }

  var types;
  var container = d3.select('#' + containerId);
  var $container = $('#' + containerId);
  var svg, outer;
  var width = $('#' + containerId).width();
  var height = Math.floor(width * 0.5);
  $container.height(height);
  var nodeMouseDown = false;
  var nodeRadius = 5;
  var nodeRadiusFunc = d3.scale.sqrt().range([10, 25]);
  var linkSizeFunc = d3.scale.linear().range([3, 8]).domain([1, 10]);
  var fontSizeFunc = d3.scale.linear().range([12, 16]);

  var tooltip;
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

  function getFontIcon(icon){
    return String.fromCodePoint(parseInt(icon.substring(1), 16));
  }

  function getNodeIcon(d) {
    var icon = getNodeTypeSettings(d, 'icon');
    if (icon.indexOf('\\') === 0) {
      return getFontIcon(icon);
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
    if (error) {
      $container.find('.spinner').attr('class', 'spinner-error');
      return;
    }
    $container.html('');

    tooltip = container.append("div")
        .attr("class", "tooltip")
        .style("opacity", 1e-6);

    outer = container.append("svg")
      .classed('svg-network', true)
      .attr("width", width)
      .attr("height", height)
      .attr("pointer-events", "all")
      .on("mousemove", mousemove);

    svg = outer.append('g')
      .attr('class', 'network-group');

    zoomListener(outer);
    outer.on("dblclick.zoom", null)
      .on('dblclick', function(){
        zoomToFit();
      });


    types = graph.types;
    if (types) {
      for (var type in types.node) {
        type = types.node[type];
        var icon = type.settings.icon;
        icon = getFontIcon(icon);
        $('#' + legendContainer).append(
          '<li><span class="icon-legend">' + icon + '</span>' + type.name + '</li>'
        );
      }
    } else {
      types = {};
    }

    var linkMapping = {};
    var idMapping = {};
    var distinctEdge = {};
    var highestDegree = Number.NEGATIVE_INFINITY;
    graph.nodes.forEach(function(n, i) {
      n.subject = (n.id === subjectId);
      if (n.subject) {
        n.fixed = true;
        n.x = width / 2;
        n.y = height / 2;
      }
      n.degree = 0;
      idMapping[n.id] = n;
    });
    graph.edges = graph.edges.filter(function(e) {
      e.sourceId = e.source;
      e.targetId = e.target;
      var source = idMapping[e.sourceId];
      var target = idMapping[e.targetId];
      if (source === undefined || target === undefined) {
        return false;
      }
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
    if (options.autoPrune) {
      graph.nodes = graph.nodes.filter(function(n){
        return !!n.rdegree;
      });
    }

    graph.nodes.forEach(function(n, i){
      linkMapping[n.id] = i;
    });
    graph.edges.forEach(function(e) {
      var edgeKey = [e.sourceId, e.targetId].sort().join('-');
      e.weight = distinctEdge[edgeKey];
      e.source = linkMapping[e.source];
      e.target = linkMapping[e.target];
    });

    if (highestDegree === Number.NEGATIVE_INFINITY) {
      highestDegree = 1;
    }

    nodeRadiusFunc.domain([1, highestDegree]);
    fontSizeFunc.domain([1, highestDegree]);

    d3cola
      .nodes(graph.nodes)
      .links(graph.edges)
      .start(20, 20, 20);

    var links = svg.selectAll(".link")
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

    var nodes = nodeContainer
      .append('circle')
        .classed("node", true)
        .classed("subject", function(d){ return d.subject; })
        .attr("r", function(d) {
          return nodeRadiusFunc(d.degree);
        })
        .style("fill", function (d) { return getNodeColor(d); })
        .style("stroke", function (d) {
          if (d.subject) {
            return getNodeStrokeColor(d);
          }
          return getNodeStrokeColor(d);
        })
        .on('mouseover', function(d){
          showTooltip(d.name);
          highlightConnections(d);
        })
        .on('mouseout', function(d){
          hideTooltip(d);
          unHighlightConnections(d);
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
          if (!d.subject) {
            document.location.href = d.url;
          }
        })
        .call(drag);

    nodeContainer.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .classed('node-icon', true)
      .style("fill", function (d) {
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
    nodeContainer.each(function(d){
      if (!(d.subject || parseInt(getNodeTypeSettings(d, 'show-label')))) {
        return;
      }
      var el = d3.select(this);
      el.append('text')
        .classed('node-label', true)
        .classed('node-label-shadow', true)
        .attr('text-anchor', 'middle')
        .attr('dy', function(d){ return nodeRadiusFunc(d.degree) * 1.75; })
        .attr('font-size', function(d) {
          return (fontSizeFunc(d.degree)) + 'px';
        })
        .text(function(d) {
          return d.name;
        });
      el.append('text')
        .classed('node-label', true)
        .attr('text-anchor', 'middle')
        .attr('dy', function(d){ return nodeRadiusFunc(d.degree) * 1.75; })
        .attr('font-size', function(d) {
          return (fontSizeFunc(d.degree)) + 'px';
        })
        .text(function(d) {
          return d.name;
        });
    });

    function highlightConnections(d) {
      graph.nodes.forEach(function(n) { n.highlighted = false; });
      d.highlighted = true;
      graph.edges.forEach(function(e) {
        e.highlighted = false;
        if (e.sourceId === d.id) {
          e.target.highlighted = true;
          e.highlighted = true;
        }
        else if (e.targetId === d.id) {
          e.source.highlighted = true;
          e.highlighted = true;
        }
      });
      svg.classed('highlighting', true);
      d3.selectAll('.nodecontainer').classed('highlighted', function(d){ return d.highlighted; });
      d3.selectAll('.link').classed('highlighted', function(d){ return d.highlighted; });
    }

    function unHighlightConnections(d) {
      svg.classed('highlighting', false);
      d3.selectAll('.nodecontainer').classed('highlighted', false);
      d3.selectAll('.link').classed('highlighted', false);
    }

    tick = function(){
      links.attr('d', function (d) {
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

    function coordBounds(arr) {
      var x = Number.POSITIVE_INFINITY, X=Number.NEGATIVE_INFINITY, y=Number.POSITIVE_INFINITY, Y=Number.NEGATIVE_INFINITY;
      arr.forEach(function(n){
        if (n.x !== undefined) {
          x = Math.min(x, n.x);
          y = Math.min(y, n.y);
          X = Math.max(X, n.x);
          Y = Math.max(Y, n.y);
        }
      });
      return {x: x, y: y, X: X, Y: Y};
    }

    function moveToCoords() {
      var cb = coordBounds(graph.nodes.map(function(d){
        return {x: d.data.lng, y: d.data.lat};
      }));
      graph.nodes.forEach(function(n){
        if (n.data.lng !== undefined) {
          n.fixed = true;
          n.x = (n.data.lng - cb.x) / (cb.X - cb.x) * width;
          n.y = (-n.data.lat + cb.y) / (cb.Y - cb.y) * height;
        }
      });
    }

    if (options.respectCoords) {
      tick();
      moveToCoords();
    }


    d3cola.on("tick", tick);
    window.setTimeout(function(){
      zoomToFit(true);
    }, 500);
  });

}
