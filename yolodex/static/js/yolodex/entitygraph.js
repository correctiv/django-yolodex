if (!String.fromCodePoint) {
  (function() {
    var defineProperty = (function() {
      // IE 8 only supports `Object.defineProperty` on DOM elements
      var result;
      try {
        var object = {};
        var $defineProperty = Object.defineProperty;
        result = $defineProperty(object, object, object) && $defineProperty;
      } catch(error) {}
      return result;
    }());
    var stringFromCharCode = String.fromCharCode;
    var floor = Math.floor;
    var fromCodePoint = function() {
      var MAX_SIZE = 0x4000;
      var codeUnits = [];
      var highSurrogate;
      var lowSurrogate;
      var index = -1;
      var length = arguments.length;
      if (!length) {
        return '';
      }
      var result = '';
      while (++index < length) {
        var codePoint = Number(arguments[index]);
        if (
          !isFinite(codePoint) ||       // `NaN`, `+Infinity`, or `-Infinity`
          codePoint < 0 ||              // not a valid Unicode code point
          codePoint > 0x10FFFF ||       // not a valid Unicode code point
          floor(codePoint) != codePoint // not an integer
        ) {
          throw RangeError('Invalid code point: ' + codePoint);
        }
        if (codePoint <= 0xFFFF) { // BMP code point
          codeUnits.push(codePoint);
        } else { // Astral code point; split in surrogate halves
          // http://mathiasbynens.be/notes/javascript-encoding#surrogate-formulae
          codePoint -= 0x10000;
          highSurrogate = (codePoint >> 10) + 0xD800;
          lowSurrogate = (codePoint % 0x400) + 0xDC00;
          codeUnits.push(highSurrogate, lowSurrogate);
        }
        if (index + 1 == length || codeUnits.length > MAX_SIZE) {
          result += stringFromCharCode.apply(null, codeUnits);
          codeUnits.length = 0;
        }
      }
      return result;
    };
    if (defineProperty) {
      defineProperty(String, 'fromCodePoint', {
        'value': fromCodePoint,
        'configurable': true,
        'writable': true
      });
    } else {
      String.fromCodePoint = fromCodePoint;
    }
  }());
}

d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
  this.parentNode.appendChild(this);
  });
};


function EntityGraph(subjectId, containerId, graphUrl, options) {
  options = options || {};
  var defaults = {
    respectCoords: false,
    autoPrune: true,
    groupingMinHeight: 350,
    scrollZoom: true
  };
  for (var k in defaults) {
    options[k] = options[k] === undefined ? defaults[k] : options[k];
  }

  var types;
  var container = d3.select('#' + containerId);
  var svg, outer;
  var width, height;
  var isFullScreen = false;

  var nodeMouseDown = false;
  var nodeRadius = 5;
  var nodeRadiusFunc = d3.scale.sqrt().range([10, 25]);
  var linkSizeFunc = d3.scale.linear().range([3, 8]).domain([1, 10]);
  var fontSizeFunc = d3.scale.linear().range([12, 16]);

  var tooltip;
  var tooltipShowing = false;

  var color = d3.scale.category20();
  var d3cola = cola.d3adaptor()
      .linkDistance(function(d){
        return nodeRadiusFunc(d.source.importance) * 2.2 + nodeRadiusFunc(d.target.importance) * 2.2 + 10;
      })
      // .avoidOverlaps(true)
      .symmetricDiffLinkLengths(10);

  var scaleFactor = 1;
  var translation = [0, 0];
  var tick = function(){};

  var xScale = d3.scale.linear();
  var yScale = d3.scale.linear();
  var MAX_ZOOM = 8;

  var zoomListener = d3.behavior.zoom()
    .scaleExtent([0.2, MAX_ZOOM])
    .on('zoom', zoomHandler);

  function start() {
    setSize();
    d3cola.size([width, height]).start(20, 20, 20);
    window.setTimeout(function(){
      zoomToFit(true);
    }, 500);
  }

  function setSize(fullScreenChanged) {
    var oldWidth = width, oldHeight = height;
    if (isFullScreen) {
      width = window.screen.width;
      height = window.screen.height;
      container.style('width', width + 'px');
    } else {
      if (fullScreenChanged) {
        container.style('width', null);
      }
      var containerBounds = container.node().getBoundingClientRect();
      width = containerBounds.width;
      if (width === oldWidth) {
        return;
      }
      if (options.embed) {
        height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
        height = height - 30;
      } else {
        height = Math.floor(width * 0.5);
      }
    }
    container.style('height', height + 'px');
    outer.attr('width', width)
      .attr('height', height);
    xScale
      .domain([0, width])
      .range([0, width]);

    yScale
      .domain([0, height])
      .range([0, height]);

    zoomListener
      .x(xScale)
      .y(yScale);
  }

  function mousemove() {
    if (!tooltipShowing) {
      return;
    }
    var b = tooltip.node().getBoundingClientRect();
    var w = b.width;
    var h = b.height;
    var coords = d3.mouse(outer[0][0]);
    tooltip
      .style("left", (coords[0] - w / 2) + "px")
      .style("top", (coords[1] - h - 15) + "px");
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
  function labelVisible(threshold) {
    return function(d) {
      var ret = d.subject || parseInt(getNodeTypeSetting(d, 'show-label'));
      var zoomScale = zoomListener.scale();
      if (!ret && zoomScale > threshold) {
        ret = true;
      }
      return ret;
    };
  }
  function switchFunc(func, t, f) {
    return function(d) {
      return func(d) ? t : f;
    };
  }
  function showLabel(sel) {
    var t = (MAX_ZOOM / 3) - 0.5;
    var t2 = t + 0.5;
    sel
      .attr('display', switchFunc(labelVisible(t), 'block', 'none'))
      .style('opacity', switchFunc(labelVisible(t2), '1', '0'));
  }

  function zoomHandler() {
    if (nodeMouseDown) { return; }
    svg.selectAll('.node-label')
      .call(showLabel);
    tick();
  }

  function graphBounds(padding) {
    padding = padding || 0;
    var x = Number.POSITIVE_INFINITY, X=Number.NEGATIVE_INFINITY, y=Number.POSITIVE_INFINITY, Y=Number.NEGATIVE_INFINITY;
    svg.selectAll(".node").each(function(v) {
        var r = nodeRadiusFunc(v.importance);
        x = Math.min(x, v.x - r);
        X = Math.max(X, v.x + r);
        y = Math.min(y, v.y - r);
        Y = Math.max(Y, v.y + r);
    });
    return {x: x - padding, X: X + padding, y: y - padding, Y: Y + 4 * padding};
  }

  function zoomToFit(render) {
      var b = graphBounds(6);
      var w = (b.X - b.x), h = (b.Y - b.y);
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

  function getNodeTypeSetting(d, n) {
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
    if (icon) {
      return String.fromCodePoint(parseInt(icon.substring(1), 16));
    }
  }

  function getNodeIcon(d) {
    var icon = getNodeTypeSetting(d, 'icon');
    if (icon.indexOf('\\') === 0) {
      return getFontIcon(icon);
    }
    return icon;
  }

  function getNodeIconColor(d) {
    return getNodeTypeSetting(d, 'icon-color');
  }

  function getNodeColor(d) {
    return getNodeTypeSetting(d, 'color');
  }

  function getNodeStrokeColor(d){
    return getNodeTypeSetting(d, 'stroke-color');
  }

  function getNodeImportance(d) {
    return (d.degree || 1) * +(getNodeTypeSetting(d, 'importance-factor') || 1);
  }

  d3.json(graphUrl, function (error, graph) {
    if (error) {
      container.selectAll('.spinner').attr('class', 'spinner-error');
      return;
    }
    container.selectAll('*').remove();

    tooltip = container.append("div")
        .attr("class", "tooltip")
        .style("opacity", 1e-6);

    outer = container.append("svg")
      .classed('svg-network', true)
      .attr("pointer-events", "all")
      .on("mousemove touchmove", mousemove);

    svg = outer.append('g')
      .attr('class', 'network-group');

    setSize();

    zoomListener(outer);
    outer.on("dblclick.zoom", null)
      .on('dblclick', function(){
        zoomToFit();
      });

    if (!options.scrollZoom){
      outer.on(".zoom", null);
    }

    types = graph.types;
    if (types && options.legendContainerId) {
      for (var type in types.node) {
        type = types.node[type];
        var icon = type.settings.icon;
        if (icon) {
          icon = getFontIcon(icon);
          icon = '<span class="icon-legend">' + icon + '</span>';
        }
        if (!icon) {
          icon = '';
        }
        $('#' + options.legendContainerId).append(
          '<li>' + icon + type.name + '</li>'
        );
      }
    } else {
      types = {};
    }

    var groupings = null;

    if (types.realm['group-by'] && options.groupContainerId && height > options.groupingMinHeight) {
      groupings = [];
      var groups = types.realm['group-by'].split(',');
      groups.forEach(function(group) {
        var groupSplit = group.split(':');
        var groupType = null;
        if (groupSplit.length > 1){
          groupType = groupSplit[0];
          group = groupSplit[1];
        } else {
          group = groupSplit[0];
        }
        groupings.push({
          group: group,
          type: groupType,
          members: {}
        });
      });
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
      n.importance = getNodeImportance(n);
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
      if (e.sourceId === e.targetId) {
        return true;
      }
      highestDegree = Math.max(highestDegree, source.importance);
      highestDegree = Math.max(highestDegree, target.importance);
      var edgeKey = [e.sourceId, e.targetId].sort().join('-');
      var prev = distinctEdge[edgeKey];
      if (prev !== undefined) {
        distinctEdge[edgeKey] += 1;
        return false;
      }
      distinctEdge[edgeKey] = 1;

      e.toPrune = false;
      if (source.distance > 0 &&
          source.degree > 20 &&
          target.distance > 1) {
        e.toPrune = true;
      }
      if (target.distance > 0 &&
          target.degree > 20 &&
          source.distance > 1) {
        e.toPrune = true;
      }

      return true;
    });

    graph.edges.forEach(function(e) {
      var source = idMapping[e.sourceId];
      var target = idMapping[e.targetId];
      source.rdegree = source.rdegree || 0;
      target.rdegree = target.rdegree || 0;
      if (e.toPrune) { return; }
      source.rdegree += 1;
      target.rdegree += 1;
    });

    if (options.autoPrune) {

      graph.edges = graph.edges.filter(function(e) {
        if (e.toPrune) {
          var source = idMapping[e.sourceId];
          var target = idMapping[e.targetId];
          return target.rdegree > 0 && source.rdegree > 0;
        }
        return true;
      });
      graph.nodes.forEach(function(n) {
        n.rdegree = 0;
      });
      graph.edges.forEach(function(e) {
        var source = idMapping[e.sourceId];
        var target = idMapping[e.targetId];
        source.rdegree += 1;
        target.rdegree += 1;
      });
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

    if (options.groupContainerId && groupings !== null) {
      var groupContainer = d3.select('#' + options.groupContainerId);
      groupings.forEach(function(group) {
        graph.nodes.forEach(function(node) {
          if ((group.groupType === null || node.type === group.type) && node.data[group.group] !== undefined) {
            var val = node.data[group.group];
            group.members[val] = group.members[val] || 0;
            group.members[val] += 1;
          }
        });
        var groupCondition = function(member) {
          return function(node) {
            return (group.groupType === null || node.type === group.type) && node.data[group.group] == member;
          };
        };
        var groupMembers = d3.entries(group.members).sort(function(a, b){
          return a.key.localeCompare(b.key);
        });
        var currentGroupContainer = groupContainer.append('li')
          .append('ul').classed('list-unstyled', true);
        currentGroupContainer.selectAll('li')
          .data(groupMembers)
          .enter()
            .append('li')
            .on('mouseover touchstart', function(d){
              d3.select(this).classed('highlighted', true);
              highlightNodes(groupCondition(d.key));
            })
            .on('mouseout touchend', function(d){
              d3.select(this).classed('highlighted', false);
              unHighlightNodes();
            })
            .attr('title', function(d) { return d.value; })
            .text(function(d){
              return d.key;
            });
      });
    }




    d3cola
      .nodes(graph.nodes)
      .links(graph.edges);


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
        .on('mouseover touchstart', function(d){
          var s = [d.source.name];
          if (d.data.label) {
            s = s.concat(['➞', '(' + d.data.label + ')']);
          }

          s = s.concat(['➞', d.target.name]);
          showTooltip(s.join(' '));
        })
        .on('mouseout touchend', function(d){
          hideTooltip(d);
        });

    var nodeContainer = svg.selectAll(".node")
        .data(graph.nodes)
      .enter().append("g")
        .classed("nodecontainer", true)
        .on("mouseover touchstart", function(){
          d3.select(this).moveToFront();
        });

    var nodes = nodeContainer
      .append('circle')
        .classed("node", true)
        .classed("subject", function(d){ return d.subject; })
        .attr("r", function(d) {
          return nodeRadiusFunc(d.importance);
        })
        .style("fill", function (d) { return getNodeColor(d); })
        .style("stroke", function (d) {
          if (d.subject) {
            return getNodeStrokeColor(d);
          }
          return getNodeStrokeColor(d);
        })
        .on('mouseover touchstart', function(d){
          showTooltip(d.name);
          highlightConnections(d);
        })
        .on('mouseout touchend', function(d){
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
            var url = d.url;
            if (options.embed) {
              url += 'embed/';
            }
            document.location.href = url;
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
        return fontSizeFunc(d.importance) + 'px';
      })
      .text(function(d) {
        return getNodeIcon(d);
      });
    nodeContainer.each(function(d){
      var el = d3.select(this);
      el.append('text')
        .classed('node-label', true)
        .classed('node-label-shadow', true)
        .call(showLabel)
        .attr('text-anchor', 'middle')
        .attr('font-size', function(d) {
          return (fontSizeFunc(d.importance)) + 'px';
        })
        .attr('y', function(l, i){
          return nodeRadiusFunc(d.importance) * 1.75;
        })
        .tspans(function(d) {
          return d3.wordwrap(d.name, 20);
        });

      el.append('text')
        .classed('node-label', true)
        .call(showLabel)
        .attr('text-anchor', 'middle')
        .attr('font-size', function(d) {
          return (fontSizeFunc(d.importance)) + 'px';
        })
        .attr('y', function(l, i){
          return nodeRadiusFunc(d.importance) * 1.75;
        })
        .tspans(function(d) {
          return d3.wordwrap(d.name, 20);
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

    function highlightNodes(cond) {
      graph.nodes.forEach(function(n) { n.highlighted = cond(n); });
      svg.classed('highlighting', true);
      svg.classed('strong-highlighting', true);
      d3.selectAll('.nodecontainer').classed('highlighted', function(d){ return d.highlighted; });
    }

    function unHighlightNodes() {
      svg.classed('highlighting', false);
      svg.classed('strong-highlighting', false);
      d3.selectAll('.nodecontainer').classed('highlighted', false);
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
          sourcePadding = nodeRadiusFunc(d.source.importance) + 1,
          targetPadding = nodeRadiusFunc(d.target.importance) + 1,
          sourceX = sx + (sourcePadding * normX),
          sourceY = sy + (sourcePadding * normY),
          targetX = tx - (targetPadding * normX),
          targetY = ty - (targetPadding * normY);


        if (options.linkStyle === 'curved') {
          return "M" + sx + "," + sy + "A" + dist + "," + dist + " 0 0,1 " + tx + "," + ty;
        } else {
          return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
        }
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

    d3cola.on("tick", tick);
    start();

    if (options.respectCoords) {
      tick();
      moveToCoords();
    }

    window.addEventListener('resize', function(){
      start();
    });
  });

  var goFullScreen = function(){
    var elem = container.node();
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.msRequestFullscreen) {
      elem.msRequestFullscreen();
    } else if (elem.mozRequestFullScreen) {
      elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) {
      elem.webkitRequestFullscreen();
    }
    return false;
  };

  document.addEventListener("fullscreenchange", function () {
      isFullScreen = document.fullscreen;
      setSize(true);
  }, false);

  document.addEventListener("mozfullscreenchange", function () {
      isFullScreen = document.mozFullScreen;
      setSize(true);
  }, false);

  document.addEventListener("webkitfullscreenchange", function () {
      isFullScreen = document.webkitIsFullScreen;
      setSize(true);
  }, false);

  document.addEventListener("msfullscreenchange", function () {
      isFullScreen = document.msFullscreenElement;
      setSize(true);
  }, false);

  if (options.fullscreenSelector) {
    if (document.fullscreenEnabled || document.webkitFullscreenEnabled || document.mozFullScreenEnabled) {
      d3.selectAll(options.fullscreenSelector).on('click', function(){
        goFullScreen();
      });
    } else {
      d3.selectAll(options.fullscreenSelector).remove();
    }
  }
}
