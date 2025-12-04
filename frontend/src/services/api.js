import axios from 'axios';
import { URL } from '../constants';

/**
 * Fetch LeetCode rating predictions for a contest
 * @param {Object} params - Contest parameters
 * @param {string} params.contestType - Type of contest (weekly-contest- or biweekly-contest-)
 * @param {string} params.contestNo - Contest number
 * @param {string} params.channelNo - Discord channel number (optional)
 * @param {string} params.username - LeetCode username (optional)
 * @returns {Promise} Response with contest predictions
 */
export const fetchPredictions = async (params) => {
    const response = await axios.get(`${URL.API_BASE_URL}${URL.ENDPOINTS.PREDICTIONS}`, { params });
    return response.data;
};

/**
 * Fetch actual updated ratings after contest completion
 * @param {Object} params - Contest parameters
 * @returns {Promise} Response with actual ratings
 */
export const fetchActualRatings = async (params) => {
    const response = await axios.get(`${URL.API_BASE_URL}${URL.ENDPOINTS.ACTUAL_RATINGS}`, { params });
    return response.data;
};

/**
 * Fetch both predictions and actual ratings in parallel
 * @param {Object} params - Contest parameters
 * @param {Object} callbacks - Optional callbacks for loading states
 * @param {Function} callbacks.onPredictionsStart - Called when predictions fetch starts
 * @param {Function} callbacks.onPredictionsEnd - Called when predictions fetch ends
 * @param {Function} callbacks.onActualRatingsStart - Called when actual ratings fetch starts
 * @param {Function} callbacks.onActualRatingsEnd - Called when actual ratings fetch ends
 * @returns {Promise<Object>} Object containing predictions and actualRatings
 */
export const fetchContestData = async (params, callbacks = {}) => {
    const requestParams = {
        ...params,
        name: params.contestType + params.contestNo
    };

    // Start loading states
    callbacks.onPredictionsStart?.();
    callbacks.onActualRatingsStart?.();

    const [predictionsResponse, actualRatingsResponse] = await Promise.allSettled([
        fetchPredictions(requestParams),
        fetchActualRatings(requestParams)
    ]);

    // End loading states
    callbacks.onPredictionsEnd?.();
    callbacks.onActualRatingsEnd?.();

    return {
        predictions: predictionsResponse.status === 'fulfilled' ? predictionsResponse.value : null,
        actualRatings: actualRatingsResponse.status === 'fulfilled' ? actualRatingsResponse.value : null,
        error: predictionsResponse.status === 'rejected' ? predictionsResponse.reason : null
    };
};
