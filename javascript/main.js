import {EditorView, basicSetup} from "codemirror"
import {python} from "@codemirror/lang-python"

let editor = new EditorView({
  extensions: [basicSetup, python()],
  parent: document.body
})
