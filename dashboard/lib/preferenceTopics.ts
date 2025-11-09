export interface PreferenceTopic {
	id: string;
	name: string;
	emoji: string;
}

export const MAX_PREFERENCE_TOPICS = 3;

export const PREFERENCE_TOPICS: PreferenceTopic[] = [
	{ id: "politics", name: "Politics", emoji: "🗳️" },
	{ id: "weather", name: "Weather", emoji: "🌤️" },
	{ id: "crypto", name: "Crypto", emoji: "₿" },
	{ id: "sports", name: "Sports", emoji: "⚽" },
	{ id: "finance", name: "Finance", emoji: "💰" },
	{ id: "technology", name: "Technology", emoji: "💻" },
	{ id: "entertainment", name: "Entertainment", emoji: "🎬" },
	{ id: "economics", name: "Economics", emoji: "📈" },
];
