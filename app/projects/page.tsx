"use client";

import { Navbar } from "@/app/components/navbar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Button } from "@/app/components/ui/button";
import Link from "next/link";

export default function ProjectsPage() {
  return (
    <>
      <Navbar />
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground">
            Manage your video projects
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Your Projects</CardTitle>
            <CardDescription>
              All your video generation projects
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-muted-foreground">
              <p className="mb-4">No projects yet</p>
              <Link href="/create">
                <Button>Create Your First Project</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}

