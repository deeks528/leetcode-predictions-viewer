/**
 * Application Constants
 * Centralized configuration for the application
 */

// API Configuration
export const URL = {
    // Backend API Base URL
    // API_BASE_URL: 'https://leetcode-predictions-viewer.onrender.com',
    API_BASE_URL: 'http://localhost:7667',

    // API Endpoints
    ENDPOINTS: {
        PREDICTIONS: '/lc',
        ACTUAL_RATINGS: '/obtained',
    }
};

// Application Settings
export const APP = {
    NAME: 'LeetCode Rating Predictions',
    VERSION: '1.0.0',
    DEFAULT_THEME: 'light',
};

// Contest Types
export const CONTEST = {
    TYPES: {
        WEEKLY: 'weekly-contest-',
        BIWEEKLY: 'biweekly-contest-',
    }
};

// Loading Messages
export const MESSAGES = {
    LOADING: {
        INITIALIZING: 'INITIALIZING SCAN...',
        PREDICTIONS: '→ Fetching predictions...',
        ACTUAL_RATINGS: '→ Fetching actual ratings...',
    },
    STATUS: {
        READY: 'SYSTEM READY...',
        NO_DATA: 'NO DATA FOUND.',
        AWAITING: 'AWAITING INPUT...',
    },
    ERROR: {
        FETCH_FAILED: 'Failed to fetch data',
        PREDICTIONS_FAILED: 'Failed to fetch predictions',
    }
};

// Export default for easy importing
const constants = {
    URL,
    APP,
    CONTEST,
    MESSAGES,
};

export default constants;
