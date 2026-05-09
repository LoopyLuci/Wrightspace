import { PageIR } from "./types";

export interface EmitResult {
  filePath: string;
  code: string;
}

export abstract class Emitter {
  abstract emit(page: PageIR): EmitResult;
}
