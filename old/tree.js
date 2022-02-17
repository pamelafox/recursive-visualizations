
class TreeViz {
  
  constructor(div, tree, options) {
    this.div = div;
    this.tree = tree;
    options = options || {};
    this.width = options.width;
    this.nodeWidth = 74;
    this.plumber = jsPlumb.getInstance();
    this.maxTop = 0;
    this.nodes = [];
  }
  
  draw() {
    this.drawNode(this.tree, 0, this.width/2);
  }
  
  drawNode(nodeInfo, depth, x, parentDiv) {
    var div = document.createElement("div");
    let label = nodeInfo.label;
    div.innerText = label;
    div.className = "node node-activated";
    var y = depth * 70;
    div.style.top = y + "px";
    this.maxTop = Math.max(y, this.maxTop);
    div.style.left = (x - this.nodeWidth/2) + "px";
    div.addEventListener("click", this.highlightNode.bind(this));
    div.addEventListener("mouseover", this.highlightNode.bind(this));
    this.div.appendChild(div);
    this.nodes.push(div);

    var descriptor = "Inner node";    
    if (this.nodes.length == 1) {
      descriptor = "The root node of entire tree";
    } else if (nodeInfo.children.length) {
      descriptor += " and root node of subtree";
    } else {
      descriptor = "A leaf node";
    }

    tippy(div, {
      allowHTML: true,
      content: descriptor + '<br>Label: ' + label,
      trigger: 'mouseenter click'
    });

    nodeInfo.div = div;
    nodeInfo.parentDiv = parentDiv;;
    
    if (parentDiv) {
      this.plumber.setContainer(this.div);
      this.plumber.connect({
              source: parentDiv, target: div,
              anchor: "Center", endpoint: "Blank",
              connector: ["Straight"],
              paintStyle:{ stroke:"#12bf96", strokeWidth:2 }
          });
    }
    if (nodeInfo.children) {
      var childDepth = depth + 1;
      var maxChildrenAtDepth = Math.pow(nodeInfo.children.length, childDepth);
      var spaceBetween = (this.width - (this.nodeWidth * maxChildrenAtDepth)) / ( maxChildrenAtDepth + 1);
      var theseChildrenSpace = (this.nodeWidth * nodeInfo.children.length) + (spaceBetween * (nodeInfo.children.length + 1));
      var childrenStartX = x - (spaceBetween/2 + this.nodeWidth/2);
      if (nodeInfo.children.length === 3) {
        childrenStartX = x - (spaceBetween + this.nodeWidth);
      }
      nodeInfo.children.forEach((child, i) => 
         this.drawNode(child, childDepth, (childrenStartX + i * (spaceBetween + this.nodeWidth)), div)
      );
    }
  }
  
  highlightNode(event) {
    const node = event.target;
    this.nodes.forEach((node, _) => {
      node.style.zIndex = 1;
    });
    node.style.zIndex = 300;
  }
}
