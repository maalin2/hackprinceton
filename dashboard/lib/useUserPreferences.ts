import { useEffect, useState } from "react";

export interface UserPreferences {
	name: string;
	topics: string[];
	completedAt: string;
}

const STORAGE_KEY = "kalshi-ai:user-preferences";
const PREFERENCES_UPDATED_EVENT = "kalshi-ai:user-preferences-updated";
const SKIP_ONBOARDING_KEY = "kalshi-ai:skip-onboarding-redirect";

function readPreferencesFromStorage(): UserPreferences | null {
	if (typeof window === "undefined") {
		return null;
	}

	const raw = window.localStorage.getItem(STORAGE_KEY);
	if (!raw) {
		return null;
	}

	try {
		return JSON.parse(raw) as UserPreferences;
	} catch (error) {
		window.localStorage.removeItem(STORAGE_KEY);
		return null;
	}
}

function notifyPreferencesUpdated() {
	if (typeof window === "undefined") {
		return;
	}

	window.dispatchEvent(new Event(PREFERENCES_UPDATED_EVENT));
}

export function useUserPreferences() {
	const [preferences, setPreferences] = useState<UserPreferences | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		if (typeof window === "undefined") {
			setLoading(false);
			return;
		}

		const updateFromStorage = () => {
			setPreferences(readPreferencesFromStorage());
			setLoading(false);
		};

		const handleStorage = (event: StorageEvent) => {
			if (event.key === STORAGE_KEY) {
				updateFromStorage();
			}
		};

		const handleCustom = () => updateFromStorage();

		updateFromStorage();
		window.addEventListener("storage", handleStorage);
		window.addEventListener(PREFERENCES_UPDATED_EVENT, handleCustom);

		return () => {
			window.removeEventListener("storage", handleStorage);
			window.removeEventListener(PREFERENCES_UPDATED_EVENT, handleCustom);
		};
	}, []);

	return { preferences, loading };
}

export function saveUserPreferences(data: UserPreferences) {
	if (typeof window === "undefined") {
		return;
	}

	window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
	notifyPreferencesUpdated();
}

export function clearUserPreferences() {
	if (typeof window === "undefined") {
		return;
	}

	window.localStorage.removeItem(STORAGE_KEY);
	notifyPreferencesUpdated();
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
