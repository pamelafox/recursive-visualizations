
class RecursiveTreeViz {
  
  constructor(div, tree, width) {
    this.div = div;
    this.tree = tree;
    this.width = width;
    this.plumber = jsPlumb.getInstance();
    this.maxTop = 0;
    this.steps = [];
  }
  
  draw() {
    this.drawNode(this.tree, 0, this.width/2);
    this.drawControls();
  }
  
  drawNode(nodeInfo, depth, x, parentDiv) {
    var div = document.createElement("div");
    div.innerText = nodeInfo.label;
    div.className = "node node-activated";
    var y = depth * 70;
    div.style.top = y + "px";
    this.maxTop = Math.max(y, this.maxTop);
    div.style.left = (x) + "px";
    this.div.appendChild(div);
    
    nodeInfo.div = div;
    nodeInfo.parentDiv = parentDiv;;
    this.steps.push(nodeInfo);
    
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
      var numMargins = 2 * childDepth;
      var spaceBetween = this.width / ( Math.pow(2, childDepth) );
      var childrenStartX = x - (spaceBetween/2);
      nodeInfo.children.forEach((child, i) => 
         this.drawNode(child, childDepth, (childrenStartX + i * spaceBetween), div)
      );
    }
  }
  
  drawControls() {
    this.currentStep = this.steps.length - 1;
    var controlsDiv = document.createElement("div");
    controlsDiv.style.position = "absolute";
    controlsDiv.style.left = (this.width/2 - 100) + "px";
    controlsDiv.style.top = this.maxTop + 50 + "px";
    
    this.prevButton = document.createElement("button");
    this.prevButton.innerText = "< Prev";
    this.prevButton.addEventListener("click", this.onPrevClick.bind(this));
    
    this.nextButton = document.createElement("button");
    this.nextButton.innerText = "> Next";
    this.nextButton.setAttribute("disabled", "disabled");
    this.nextButton.addEventListener("click", this.onNextClick.bind(this));

    this.slider = document.createElement("input");
    this.slider.setAttribute("type", "range");
    this.slider.setAttribute("min", 0);
    this.slider.setAttribute("max", this.steps.length - 1);
    this.slider.setAttribute("value", this.currentStep);
    this.slider.addEventListener("change", this.onSliderChange.bind(this));

    controlsDiv.appendChild(this.prevButton);
    controlsDiv.appendChild(this.slider);
    controlsDiv.appendChild(this.nextButton);
    this.div.appendChild(controlsDiv);
  }

  toggleSteps() {
    
    let prevDiv;
    this.steps.forEach((step, stepI) => {
      var connectors =  this.plumber.getConnections(
        {source: step.parentDiv, target: step.div});
      if (stepI <= this.currentStep) {
        step.div.className = "node node-activated";
        connectors.forEach((connection) => {
          connection.setPaintStyle({ stroke:"#12bf96", strokeWidth:2 })
        });
      } else {
        step.div.className = "node";
        connectors.forEach((connection) => {
          connection.setPaintStyle({ stroke:"#ccc", strokeWidth:2 })
        });
      }
      prevDiv = step.div;
    })
  }
  
  onSliderChange(event) {
    this.currentStep = parseInt(event.target.value, 10);
    this.toggleSteps();
  }
  
  onPrevClick(event) {
    this.currentStep--;
    if (this.currentStep === 0) {
      this.prevButton.setAttribute("disabled", "disabled");
    }
    if (this.currentStep < this.steps.length - 1) {
      this.nextButton.removeAttribute("disabled");
    }
    this.slider.setAttribute("value", this.currentStep);
    this.toggleSteps();
  }
  
  onNextClick(event) {
    this.currentStep++;
    if (this.currentStep > 0) {
      this.prevButton.removeAttribute("disabled");
    }
    if (this.currentStep === this.steps.length - 1) {
      this.nextButton.setAttribute("disabled", "disabled");
    }
    
    this.slider.setAttribute("value", this.currentStep);
    this.toggleSteps();
  }
  
}
