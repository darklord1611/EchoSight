import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

export const useNewsStore = defineStore('news', () => {
    const articles = ref<any[]>([]);
    const query = ref<string>('');
    const loading = ref(false);
    const error = ref<string | null>(null);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    const fetchNews = async (newQuery: string) => {
        query.value = newQuery;
        loading.value = true;
        error.value = null;

        console.log("Fetching news articles...");
        try {
            const formData = new FormData();
            formData.append("news_query", newQuery);

            const response = await axios.post(
                `${BACKEND_URL}/fetching_news`,
                formData,
                {
                    headers: {
                        // Let the browser set the correct multipart/form-data headers
                        "Content-Type": "multipart/form-data",
                    },
                }
            );

            if (response.status === 200 && response.data.articles) {
                articles.value = response.data.articles;
            } else {
                error.value = response.data.message || 'Failed to fetch news';
            }

            console.log(response.data)

            return response.data;
        } catch (err) {
            error.value = 'Network error';
        } finally {
            loading.value = false;
        }
    };

    return {
        articles,
        query,
        loading,
        error,
        fetchNews,
    };
});
