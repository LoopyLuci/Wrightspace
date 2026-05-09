"use client";

import { useEffect, useMemo, useState } from "react";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";

export interface CollabConnection {
  doc: Y.Doc;
  provider: WebsocketProvider;
}

type CollabSession = CollabConnection & {
  destroy: () => void;
};

export interface AwarenessEntry {
  clientId: number;
  state: unknown;
}

export interface AwarenessSnapshot {
  awareness: WebsocketProvider["awareness"] | null;
  clientId: number | null;
  connected: boolean;
  localState: unknown | null;
  states: AwarenessEntry[];
}

const providerByDoc = new WeakMap<Y.Doc, WebsocketProvider>();

function buildCollabUrl(roomId: string) {
  const baseUrl = process.env.NEXT_PUBLIC_COLLAB_SERVER_URL ?? "ws://127.0.0.1:4001";
  return `${baseUrl.replace(/\/$/, "")}/ws/projects/${encodeURIComponent(roomId)}`;
}

function createSession(roomId: string): CollabSession {
  const doc = new Y.Doc();
  const provider = new WebsocketProvider(buildCollabUrl(roomId), "collab", doc);
  providerByDoc.set(doc, provider);

  return {
    doc,
    provider,
    destroy() {
      provider.destroy();
      doc.destroy();
      providerByDoc.delete(doc);
    }
  };
}

export function connectCollab(url: string, room: string): CollabConnection {
  const doc = new Y.Doc();
  const provider = new WebsocketProvider(url, room, doc);
  providerByDoc.set(doc, provider);
  return { doc, provider };
}

function useDocRevision(doc: Y.Doc): number {
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const bumpRevision = () => setRevision((current: number) => current + 1);
    doc.on("update", bumpRevision);

    return () => {
      doc.off("update", bumpRevision);
    };
  }, [doc]);

  return revision;
}

export function useYjsDoc(roomId: string): Y.Doc {
  const session = useMemo(() => createSession(roomId), [roomId]);

  useEffect(() => () => session.destroy(), [session]);

  return session.doc;
}

export function useSharedObject<T extends Y.Map<unknown>>(doc: Y.Doc, key: string): T {
  useDocRevision(doc);
  return doc.getMap(key) as T;
}

export function useAwareness(doc: Y.Doc): AwarenessSnapshot {
  const provider = providerByDoc.get(doc) ?? null;
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    if (!provider) {
      return;
    }

    const awareness = provider.awareness;
    const bumpRevision = () => setRevision((current: number) => current + 1);

    awareness.on("change", bumpRevision);
    awareness.on("update", bumpRevision);

    return () => {
      awareness.off("change", bumpRevision);
      awareness.off("update", bumpRevision);
    };
  }, [provider]);

  return useMemo(() => {
    if (!provider) {
      return {
        awareness: null,
        clientId: null,
        connected: false,
        localState: null,
        states: []
      };
    }

    const awareness = provider.awareness;
    const states = Array.from(awareness.getStates().entries()).map(([clientId, state]) => ({
      clientId: Number(clientId),
      state
    }));

    return {
      awareness,
      clientId: doc.clientID,
      connected: provider.wsconnected,
      localState: awareness.getLocalState(),
      states
    };
  }, [doc.clientID, provider, revision]);
}
