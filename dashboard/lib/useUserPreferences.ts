import { useCallback, useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

export interface UserPreferences {
	name: string;
	topics: string[];
	completedAt: string;
}

const SKIP_ONBOARDING_KEY = "kalshi-ai:skip-onboarding-redirect";

type LoadPreferencesOptions = {
	silent?: boolean;
};

export function useUserPreferences() {
	const [preferences, setPreferences] = useState<UserPreferences | null>(null);
	const [loading, setLoading] = useState(true);
	const supabase = createClient();

	const loadPreferences = useCallback(
		async ({ silent = false }: LoadPreferencesOptions = {}) => {
			if (!silent) {
				setLoading(true);
			}

			try {
				const {
					data: { user },
				} = await supabase.auth.getUser();

				if (!user) {
					setPreferences(null);
					return;
				}

				const { data, error } = await supabase
					.from("user_preferences")
					.select("*")
					.eq("user_id", user.id)
					.single();

				if (error && error.code !== "PGRST116") {
					// PGRST116 is "not found" error, which is fine
					console.error("Error loading preferences:", error);
				}

				if (data) {
					setPreferences({
						name: data.name || "",
						topics: data.topics || [],
						completedAt: data.completed_at || "",
					});
				} else {
					setPreferences(null);
				}
			} catch (error) {
				console.error("Error loading preferences:", error);
				setPreferences(null);
			} finally {
				setLoading(false);
			}
		},
		[supabase]
	);

	useEffect(() => {
		loadPreferences();

		// Listen for auth state changes
		const {
			data: { subscription },
		} = supabase.auth.onAuthStateChange(() => {
			loadPreferences();
		});

		return () => {
			subscription.unsubscribe();
		};
	}, [loadPreferences, supabase]);

	const refreshPreferences = useCallback(() => loadPreferences({ silent: true }), [loadPreferences]);

	return { preferences, loading, refreshPreferences };
}

export async function saveUserPreferences(data: UserPreferences) {
	const supabase = createClient();

	try {
		const {
			data: { user },
		} = await supabase.auth.getUser();

		if (!user) {
			console.error("No user logged in");
			return;
		}

		const { error } = await supabase.from("user_preferences").upsert(
			{
				user_id: user.id,
				name: data.name,
				topics: data.topics,
				completed_at: data.completedAt,
			},
			{
				onConflict: "user_id",
			}
		);

		if (error) {
			console.error("Error saving preferences:", error);
			throw error;
		}
	} catch (error) {
		console.error("Error saving preferences:", error);
		throw error;
	}
}

export async function clearUserPreferences() {
	const supabase = createClient();

	try {
		const {
			data: { user },
		} = await supabase.auth.getUser();

		if (!user) {
			return;
		}

		const { error } = await supabase
			.from("user_preferences")
			.delete()
			.eq("user_id", user.id);

		if (error) {
			console.error("Error clearing preferences:", error);
		}
	} catch (error) {
		console.error("Error clearing preferences:", error);
	}
}

export function markSkipOnboardingRedirect() {
	if (typeof window === "undefined") {
		return;
	}

	window.sessionStorage.setItem(SKIP_ONBOARDING_KEY, "true");
}

export function consumeSkipOnboardingRedirect() {
	if (typeof window === "undefined") {
		return false;
	}

	const shouldSkip = window.sessionStorage.getItem(SKIP_ONBOARDING_KEY) === "true";

	if (shouldSkip) {
		window.sessionStorage.removeItem(SKIP_ONBOARDING_KEY);
	}

	return shouldSkip;
}
