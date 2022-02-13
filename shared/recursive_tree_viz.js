class RecursiveTreeViz {

    constructor(svg, options) {
        this.svg = svg;
        options = options || {};
        this.startStep = options.startStep;
        this.steps = [];
        this.frames = {};
    }

    draw() {
        // Store all the frames
        const frames = this.svg.querySelectorAll(".node");
        for (var i = 0; i < frames.length; i++) {
        const frame = frames[i];
        const frameId = frame.getElementsByTagName("title")[0].textContent;
        this.frames[frameId] = frame;
        }

        // Determine number of steps
        const edges = this.svg.querySelectorAll(".edge");
        for (let i = 0; i < edges.length; i++) {
        const edge = edges[i];
        const edgeTitle = edge.getElementsByTagName("title")[0].textContent;
        const edgeText = edge.getElementsByTagName("text")[0].textContent;

        let stepNum, isReturn;
        stepNum = parseInt(edgeText.split("(#")[1], 10);
        if (edgeTitle.endsWith(":c")) {
            isReturn = true;
            edge.getElementsByTagName("text")[0].textContent = edgeText.split("(#")[0];
        } else {
            edge.getElementsByTagName("text")[0].textContent = "";
            isReturn = false;
        }
        const edgeFrames = edgeTitle.split(":c")[0];
        const parentFrameId = edgeFrames.split("->")[0];
        const childFrameId = edgeFrames.split("->")[1];
        this.steps[stepNum] = {
            parentFrame: this.frames[parentFrameId],
            childFrame: this.frames[childFrameId],
            edge: edge,
            isReturn: isReturn
        };
        }

        if (this.startStep == null || isNaN(this.startStep)) {
        this.currentStep = this.steps.length - 1;
        } else {
        this.currentStep = this.startStep;
        }
        this.drawControls();
        this.toggleSteps();
    }


    drawControls() {
        var controlsDiv = document.createElement("div");
        controlsDiv.classList.add("svg-controls");

        this.prevButton = document.createElement("button");
        this.prevButton.innerText = "< Prev";
        if (this.currentStep <= 0) {
        this.prevButton.setAttribute("disabled", "disabled");
        }
        this.prevButton.addEventListener("click", this.onPrevClick.bind(this));
        document.addEventListener("keypress", (e) => {
            if (e.key == "p" || e.key == "ArrowLeft") {
            this.onPrevClick();
            } else if (e.key == "n" || e.key == "ArrowRight") {
            this.onNextClick();
            }
        });

        this.nextButton = document.createElement("button");
        this.nextButton.innerText = "> Next";
        if (this.currentStep >= this.steps.length - 1) {
        this.nextButton.setAttribute("disabled", "disabled");
        }
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

        this.svg.before(controlsDiv);
    }

    toggleSteps() {
        this.steps.forEach((step, stepI) => {
        if (stepI == 1) {
            step.parentFrame && step.parentFrame.classList.add("activated");
        }
        if (stepI <= this.currentStep) {
            step.edge.classList.add("activated");
            step.childFrame.classList.add("activated");
        } else {
            step.edge.classList.remove("activated");
            !step.isReturn && step.childFrame.classList.remove("activated");
        }
        })
    }

    onSliderChange(event) {
        this.currentStep = parseInt(event.target.value, 10);
        this.fixButtons();
        this.toggleSteps();
    }

    onPrevClick(event) {
        this.currentStep--;
        this.fixButtons();
        this.slider.value = this.currentStep;
        this.toggleSteps();
    }

    onNextClick(event) {
        this.currentStep++;
        this.fixButtons();
        this.slider.value = this.currentStep;
        this.toggleSteps();
    }

    fixButtons() {
        if (this.currentStep === 0) {
        this.prevButton.setAttribute("disabled", "disabled");
        }
        if (this.currentStep < this.steps.length - 1) {
        this.nextButton.removeAttribute("disabled");
        }
        if (this.currentStep > 0) {
        this.prevButton.removeAttribute("disabled");
        }
        if (this.currentStep === this.steps.length - 1) {
        this.nextButton.setAttribute("disabled", "disabled");
        }
    }
}