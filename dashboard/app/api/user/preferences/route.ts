import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const supabase = await createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { data, error } = await supabase
      .from("user_preferences")
      .select("*")
      .eq("user_id", user.id)
      .single();

    if (error && error.code !== "PGRST116") {
      // PGRST116 is "not found" error, which is fine
      return NextResponse.json(
        { error: "Failed to fetch preferences" },
        { status: 500 }
      );
    }

    if (!data) {
      return NextResponse.json({ preferences: null });
    }

    return NextResponse.json({
      preferences: {
        name: data.name || "",
        topics: data.topics || [],
        completedAt: data.completed_at || "",
      },
    });
  } catch (error) {
    console.error("Error fetching preferences:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { name, topics, completedAt } = body;

    const { data, error } = await supabase
      .from("user_preferences")
      .upsert(
        {
          user_id: user.id,
          name,
          topics,
          completed_at: completedAt,
        },
        {
          onConflict: "user_id",
        }
      )
      .select()
      .single();

    if (error) {
      return NextResponse.json(
        { error: "Failed to save preferences" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      preferences: {
        name: data.name || "",
        topics: data.topics || [],
        completedAt: data.completed_at || "",
      },
    });
  } catch (error) {
    console.error("Error saving preferences:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

