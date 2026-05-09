import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";

export interface CollabConnection {
  doc: Y.Doc;
  provider: WebsocketProvider;
}

export function connectCollab(url: string, room: string): CollabConnection {
  const doc = new Y.Doc();
  const provider = new WebsocketProvider(url, room, doc);
  return { doc, provider };
}
