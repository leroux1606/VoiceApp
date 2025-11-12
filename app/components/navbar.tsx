"use client";

import * as React from "react";
import Link from "next/link";
import { Button } from "@/app/components/ui/button";
import { Video, Plus, Settings } from "lucide-react";

export function Navbar() {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <Video className="h-6 w-6" />
            <span className="font-bold">YouTube Generator</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2">
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link
              href="/"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Dashboard
            </Link>
            <Link
              href="/create"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Create Video
            </Link>
            <Link
              href="/projects"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Projects
            </Link>
          </nav>
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
            <Link href="/create">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Video
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

