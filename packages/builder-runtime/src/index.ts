export interface InstrumentationSelectionMessage {
  type: "builder:selection";
  nodeId: string;
}

export function installInstrumentation(root: ParentNode = document): void {
  root.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    const nodeId = target.getAttribute("data-builder-id");
    if (!nodeId) {
      return;
    }

    const message: InstrumentationSelectionMessage = {
      type: "builder:selection",
      nodeId
    };

    window.parent.postMessage(message, "*");
  });
}
