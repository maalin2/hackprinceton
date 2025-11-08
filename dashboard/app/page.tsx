import { getUser } from "@/lib/auth";
import { redirect } from "next/navigation";
import { LandingPage } from "@/components/LandingPage";

export default async function Home() {
  const user = await getUser();
  
  if (user) {
    redirect("/dashboard");
  }

  return <LandingPage />;
}
