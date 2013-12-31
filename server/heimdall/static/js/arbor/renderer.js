Array.prototype.remByVal = function(val) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] === val) {
            this.splice(i, 1);
            i--;
        }
    }
    return this;
}

function xinspect(o,i){
    if(typeof i=='undefined')i='';
    if(i.length>50)return '[MAX ITERATIONS]';
    var r=[];
    for(var p in o){
        var t=typeof o[p];
        r.push(i+'"'+p+'" ('+t+') => '+(t=='object' ? 'object:'+xinspect(o[p],i+'  ') : o[p]+''));
    }
    return r.join(i+'\n');
};
Permissions = {
  visibleItems     : null,
  data             : null,
  central          : null,
  servers          : null,
  hostuser         : null,
  user             : null,
  currentSelection : null
};
Permissions.visibleItems = [];



(function() {
    Renderer = function(elt){
    var dom = $(elt)
    var canvas = dom.get(0)
    var ctx = canvas.getContext("2d");
    var gfx = arbor.Graphics(canvas)
    var sys = null

    var serverVisible = false;

    var _vignette = null
    var selected = null,
        nearest = null,
        _mouseP = null;

    
    var that = {
      init:function(pSystem){
        sys = pSystem
        sys.screen({size:{width:dom.width(), height:dom.height()},
                    padding:[36,60,36,60]})

        $(window).resize(that.resize)
        that.resize()
        that._initMouseHandling()

        if (document.referrer.match(/echolalia|atlas|halfviz/)){
          // if we got here by hitting the back button in one of the demos, 
          // start with the demos section pre-selected
          that.switchSection('demos')
        }
      },
      resize:function(){
        canvas.width = $(window).width() - 50
        canvas.height = $(window).height() - 150
        sys.screen({size:{width:canvas.width, height:canvas.height}})
        _vignette = null
        that.redraw()
      },
      redraw:function(){
        gfx.clear()
        sys.eachEdge(function(edge, p1, p2){
          if (edge.source.data.alpha * edge.target.data.alpha == 0) return
          gfx.line(p1, p2, {stroke:"#b2b19d", width:2, alpha:edge.target.data.alpha})
        })
        sys.eachNode(function(node, pt){
          var w = Math.max(20, 20+gfx.textWidth(node.name) )
          if (node.data.alpha===0) return
          if (node.data.shape=='dot'){
            gfx.oval(pt.x-w/2, pt.y-w/2, w, w, {fill:node.data.color, alpha:node.data.alpha})
            gfx.text(node.name, pt.x, pt.y+7, {color:"white", align:"center", font:"Arial", size:12})
            gfx.text(node.name, pt.x, pt.y+7, {color:"white", align:"center", font:"Arial", size:12})
          }else{
            gfx.rect(pt.x-w/2, pt.y-8, w, 20, 4, {fill:node.data.color, alpha:node.data.alpha})
            gfx.text(node.name, pt.x, pt.y+9, {color:"white", align:"center", font:"Arial", size:12})
            gfx.text(node.name, pt.x, pt.y+9, {color:"white", align:"center", font:"Arial", size:12})
          }
        })
        that._drawVignette()
      },
      
      _drawVignette:function(){
        var w = canvas.width
        var h = canvas.height
        var r = 20

        if (!_vignette){
          var top = ctx.createLinearGradient(0,0,0,r)
          top.addColorStop(0, "#e0e0e0")
          top.addColorStop(.7, "rgba(255,255,255,0)")

          var bot = ctx.createLinearGradient(0,h-r,0,h)
          bot.addColorStop(0, "rgba(255,255,255,0)")
          bot.addColorStop(1, "white")

          _vignette = {top:top, bot:bot}
        }
        
        // top
        ctx.fillStyle = _vignette.top
        ctx.fillRect(0,0, w,r)

        // bot
        ctx.fillStyle = _vignette.bot
        ctx.fillRect(0,h-r, w,r)
      },

      switchMode:function(e){
        if (e.mode=='hidden'){
          dom.stop(true).fadeTo(e.dt,0, function(){
            if (sys) sys.stop()
            $(this).hide()
          })
        }else if (e.mode=='visible'){
          dom.stop(true).css('opacity',0).show().fadeTo(e.dt,1,function(){
            that.resize()
          })
          if (sys) sys.start()
        }
      },

      toggleNodeVisible: function(node){
        if(node.data.alpha==0){
          sys.tweenNode(node, 0.5, {alpha:1})
          node.data.alpha = 1
        }else{
          sys.tweenNode(node, 0.5, {alpha:0})
          //node.data.alpha = 1
        }
      },

      setNodeVisible: function(node, isVisible){
        if(isVisible){
          sys.tweenNode(node, 0.5, {alpha:1})

          if (Permissions.currentSelection != null){
            node.p.x = Permissions.currentSelection.p.x + .5*Math.random() - .0015
            node.p.y = Permissions.currentSelection.p.y + .5*Math.random() - .0015
            node.tempMass = .001
          }
        }else{
          sys.tweenNode(node, 0.5, {alpha:0})
        }
      },

      toggleServers: function(){
        sys.eachNode(function(node){
          if(node.data.type == 'server'){
            if (serverVisible){
              that.setNodeVisible(node, false)
            }else{
              that.setNodeVisible(node, true)
            }
            //that.toggleNodeVisible(node)
          }else if(node.data.type == 'central'){
            that.setNodeVisible(node, true)
          }else{
            that.setNodeVisible(node, false)
          }
        })
        serverVisible = !serverVisible;
      },

      toggleUsers: function(hostUser){
        sys.eachNode(function(node){
          if(node.data.type == 'user'){
            that.setNodeVisible(node, false)
          }
        })

        $.map(sys.getEdgesFrom(hostUser), function(edge){
            console.log("toggle: " + edge.target.data.label)
            that.setNodeVisible(edge.target, true)
        })
      },

      toggleHostUsers: function(fromServer){
        // Hide all
        sys.eachNode(function(node){
          if(node.data.type == 'hostuser'){
            that.setNodeVisible(node, false)
          }else if(node.data.type == 'user'){
            that.setNodeVisible(node, false)
          }
        })

        $.map(sys.getEdgesFrom(fromServer), function(edge){
            console.log("toggle: " + edge.target.data.label)
            that.setNodeVisible(edge.target, true)
           
        })
      },

      hideOtherInSameLevel: function(node){
        sys.eachNode(function(nodeToHide){
          if(nodeToHide.data.type == node.data.type && nodeToHide.data != node.data){
            that.setNodeVisible(nodeToHide, false)
          }
        })
      },
      
      switchSection:function(newSection){
        console.log("selection: " + newSection.data.type)
        Permissions.currentSelection = sys.getEdgesFrom(newSection)[0].source

        type = newSection.data.type;
        if (type=='central'){
          // alert('central')
          // show / hide servers
          that.toggleServers()
        }else if (type=='server'){
          console.log('server')
          // show / hide hostusers
          that.toggleHostUsers(newSection)
          that.hideOtherInSameLevel(newSection)
          serverVisible = false;
        }else if (type=='hostuser'){
          console.log('hostuser')
          // show / hide users
          that.toggleUsers(newSection)
          that.hideOtherInSameLevel(newSection)
        }else if (type=='user'){
          console.log('user')
          // hide user
        }


        sys.eachNode(function(node){
         
        })
      },
      
      
      _initMouseHandling:function(){
        // no-nonsense drag and drop (thanks springy.js)
        selected = null;
        nearest = null;
        var dragged = null;
        var oldmass = 1

        var handler = {
          clicked:function(e){
            var pos = $(canvas).offset();
            _mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)
            nearest = sys.nearest(_mouseP);

            if (!nearest.node) return false
            if ($.inArray(nearest.node.name, Permissions.data) >=0 ){
                selected = (nearest.distance < 50) ? nearest : null
                //console.log(console.log(nearest.node.data))
                if (nearest.node.data.alpha == 1){
                    //console.log(nearest.node.data.type)
                    _section = nearest.node.name
                    that.switchSection(nearest.node)
                }
            }
            return false
          }
        }
        $(canvas).mousedown(handler.clicked);
      }
    } 
    return that
  }
})(this.jQuery)
