import { verifyBlock } from "@builder/marketplace/integrity";
import type { BlockPackage } from "@builder/marketplace/schema";
import { NextResponse } from "next/server";

export async function POST(request: Request): Promise<NextResponse> {
  const pkg = (await request.json()) as BlockPackage;
  const valid = verifyBlock(pkg);
  return NextResponse.json({ valid });
}
