import type { ComponentNode, ElementNode, ProjectIR, SlotNode, TextNode } from "../../src/types";

const footerFallbackSlot: SlotNode = {
  id: "card-footer-slot",
  type: "slot",
  slotName: "footerActions",
  fallback: [
    {
      id: "fallback-text",
      type: "text",
      content: "No actions provided",
      styles: {},
    } as TextNode,
  ],
};

const cardCounterComponent: ComponentNode = {
  id: "card-component-1",
  type: "component",
  componentId: "CardCounter",
  props: {
    className: "card-shell",
    "aria-label": "Counter card",
  },
  state: [
    {
      name: "count",
      type: "number",
      initialValue: 0,
    },
  ],
  slots: {
    header: [
      {
        id: "card-header-title",
        type: "text",
        content: "Counter Card",
        styles: {
          fontWeight: { value: "700" },
          color: { value: "white" },
        },
      } as TextNode,
    ],
    body: [
      {
        id: "card-body-counter",
        type: "element",
        tag: "p",
        props: {},
        styles: {},
        children: [
          {
            id: "card-body-counter-label",
            type: "text",
            content: "Current value:",
            styles: {},
          } as TextNode,
          {
            id: "card-body-counter-value",
            type: "text",
            content: { binding: "count" },
            styles: {},
          } as TextNode,
        ],
      } as ElementNode,
      {
        id: "card-actions",
        type: "element",
        tag: "div",
        props: { className: "actions" },
        styles: {},
        children: [
          {
            id: "increment-button",
            type: "element",
            tag: "button",
            props: { type: "button" },
            styles: {},
            events: [{ name: "onClick", handler: "incrementCount" }],
            children: [
              {
                id: "increment-label",
                type: "text",
                content: "Increment",
                styles: {},
              } as TextNode,
            ],
          } as ElementNode,
          {
            id: "decrement-button",
            type: "element",
            tag: "button",
            props: { type: "button" },
            styles: {},
            events: [{ name: "onClick", handler: "decrementCount" }],
            children: [
              {
                id: "decrement-label",
                type: "text",
                content: "Decrement",
                styles: {},
              } as TextNode,
            ],
          } as ElementNode,
        ],
      } as ElementNode,
    ],
    footer: [footerFallbackSlot],
  },
};

export const slotStateFixture: ElementNode = {
  id: "slot-state-page-root",
  type: "element",
  tag: "section",
  styles: {
    display: { value: "flex" },
    flexDirection: { value: "column", breakpoint: "base" },
  },
  props: { className: "slot-state-host" },
  children: [cardCounterComponent],
  customCode: {
    functions:
      "function incrementCount() {\n  setCount((prev) => prev + 1);\n}\n\nfunction decrementCount() {\n  setCount((prev) => prev - 1);\n}",
  },
};

export function createSlotStateProjectIR(): ProjectIR {
  return {
    schemaVersion: "1.0.0",
    framework: "react",
    designTokens: {},
    pages: [
      {
        id: "slot-state-page",
        name: "SlotStatePage",
        route: "/",
        root: slotStateFixture,
        meta: {},
        state: [],
      },
    ],
    components: {},
    assets: {},
  };
}
