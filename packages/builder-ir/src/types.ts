// ============================================================
// @builder/ir — Canonical Intermediate Representation Types
// Spec version 1.0.0 — aligned with ADR and companion specs
// ============================================================

export type Breakpoint = 'base' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface StyleValue {
  value: string | number;
  breakpoint?: Breakpoint;
  mediaQuery?: string;
}

export interface ResponsiveStyles {
  [key: string]: StyleValue | StyleValue[] | undefined;
}

export interface PropDefinition {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'enum' | 'function' | 'slot';
  defaultValue?: any;
  required?: boolean;
  description?: string;
  enumValues?: string[];
}

export interface EventHandler {
  name: string;
  handler: string;
  preventDefault?: boolean;
}

export interface StateVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  initialValue: any;
  persist?: boolean;
}

export type NodeType = 'element' | 'component' | 'slot' | 'text' | 'fragment';

export interface BaseNode {
  id: string;
  type: NodeType;
  name?: string;
  locked?: boolean;
  customCode?: {
    imports?: string;
    variables?: string;
    functions?: string;
    effects?: string;
  };
}

export interface ElementNode extends BaseNode {
  type: 'element';
  tag: string;
  styles: ResponsiveStyles;
  props: Record<string, any>;
  children: IRNode[];
  events?: EventHandler[];
  accessibility?: {
    role?: string;
    label?: string;
    [key: string]: any;
  };
}

export interface ComponentNode extends BaseNode {
  type: 'component';
  componentId: string;
  variant?: string;
  props: Record<string, any>;
  slots: Record<string, IRNode[]>;
  events?: EventHandler[];
  state?: StateVariable[];
  propSchema?: Record<string, PropSchemaEntry>;
  slotSchema?: Record<string, SlotSchemaEntry>;
}

export interface PropSchemaEntry {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'union' | 'literal';
  required?: boolean;
  default?: any;
  description?: string;
  properties?: Record<string, PropSchemaEntry>;
  items?: PropSchemaEntry;
  options?: PropSchemaEntry[];
  enum?: string[];
}

export interface SlotSchemaEntry {
  description?: string;
  allowedTypes?: string[];
}

export interface TextNode extends BaseNode {
  type: 'text';
  content: string | { binding: string };
  styles: ResponsiveStyles;
}

export interface SlotNode extends BaseNode {
  type: 'slot';
  slotName: string;
  fallback?: IRNode[];
}

export type IRNode = ElementNode | ComponentNode | TextNode | SlotNode;

export interface PageIR {
  id: string;
  name: string;
  route: string;
  root: IRNode;
  meta: {
    title?: string;
    description?: string;
    ogImage?: string;
  };
  state?: StateVariable[];
}

export interface ProjectIR {
  schemaVersion: string;
  framework: 'react' | 'vue' | 'svelte' | 'web-component' | 'vanilla';
  designTokens: Record<string, any>;
  pages: PageIR[];
  components: Record<string, ComponentNode>;
  assets: Record<string, string>;
}
